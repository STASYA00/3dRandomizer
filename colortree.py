import sys

from blender_utils import normalize_prob
from config import SCRIPT_PATH

sys.path.append(SCRIPT_PATH)

import numpy as np
import pandas as pd

from config import FILENAME


class ColorTree:
    def __init__(self) -> None:
        self.tree = self.build()

    def build(self):
        return self._build()

    def _build(self):
        _d = {"head": {"prob": 0.98,
                       "inner_belly": {"same": 1.0},
                       "arms": {
                           "same": 0.58,
                           "Black": 0.2,
                           "White": 0.2,
                           "silver": 0.015,
                           "gold": 0.005
                       },
                       "belly": {
                           "complementary": 0.98,
                           "silver": 0.015,
                           "gold": 0.005
                           }
              },
              "silver": {"prob": 0.015,
                       "inner_belly": {"same": 1.0},
                       "arms": {
                           "Black": 0.49,
                           "White": 0.49,
                           "silver": 0.015,
                           "gold": 0.005
                       },
                       "belly": {
                           "complementary": 0.98,
                           "silver": 0.015,
                           "gold": 0.005
                           }
              },
              "gold": {"prob": 0.005,
                       "inner_belly": {"same": 1.0},
                       "arms": {
                           "Black": 0.49,
                           "White": 0.49,
                           "silver": 0.015,
                           "gold": 0.005
                       },
                       "belly": {
                           "complementary": 0.98,
                           "silver": 0.015,
                           "gold": 0.005
                           }
              }
        }
        return _d

class ColorPicker:
    def __init__(self, tree=None, content=None, name="generic") -> None:
        self.name = name
        self.columns = {
            "name": "Name",
            "main": "RGB Mains",
            "complementary": "RGB Complementaries"
                        }
        if content:
            self.content = content
        else:
            self.content = self._load()
        self.main_colors = self._main_colors()
        self.current_color = ""
        self.current_category = ""
        self.current_prob = 1.0
        self.tree = tree
        if not self.tree:
            self.tree = ColorTree()

    def make(self, **kwargs):
        return self._make(**kwargs)

    def _exclusivity_check(self, color):
        return color.lower() in ["gold", "silver"]
        
    def _get_color_value(self, color):
        """
        Function that returns a list of rgb values for a color.
        """
        if not isinstance(self.main_colors, list):
            self.main_colors = self._main_colors()

        if self._exclusivity_check(color):
            return color

        return self._split(self.content[self.content[self.columns["name"]]==color][self.columns["main"]].iat[0])

    def _get_complementary(self, color):
        """
        color - Blue
        complementary - White (returns)
        """
        _options = len(self.content[self.content[self.columns["name"]]==color])
        return self.content[self.content[self.columns["name"]]==color][self.columns[
            "complementary"]].iat[np.random.choice(list(range(_options)))]

    def _get_current_prob(self):
        _prob = 1.0
        _prob *= self.tree.tree[self.current_category]["prob"]
        return _prob

    def _load(self):
        _file = pd.read_csv(FILENAME)
        if "Name" not in _file.columns:
            _file = pd.read_csv(FILENAME, delimiter=";")
        return _file

    def _main_colors(self):
        return [x for x in self.content["Name"].unique()[:-2] if not self._exclusivity_check(x)]
        
    def _make(self, **kwargs):
        
        self.current_category = np.random.choice(list(self.tree.tree.keys()), 1, 
                                       p=normalize_prob([x["prob"] for x in self.tree.tree.values()]))[0]
        self.current_prob = self._get_current_prob()
        if self.current_category == "head":
            self.current_color = np.random.choice(self.main_colors, 1)[0]
            _color = self._get_color_value(self.current_color)  # RGB values as a list
            return _color
        else:
            self.current_color = self.current_category
            return self.current_color

    def _split(self, color):
        if isinstance(color, str):
            return [int(x) / 255 for x in color.split(',')]

class ComplColorPicker(ColorPicker):
    def __init__(self, tree=None, content=None, name="complementary") -> None:
        super().__init__(tree=tree, content=content, name=name)

    def _get_current_prob(self, color):
        raise NotImplementedError

    def _get_color_value(self, color):
        """
        Function that returns a list of rgb values for a color.
        """
        _options = len(self.content[self.columns["name"]==color])
        return self._split(self.content[self.content[self.columns["name"]]==color][self.columns[
            "complementary"]].iat[np.random.choice(list(range(_options)))])

class ArmsColorPicker(ColorPicker):
    def __init__(self, tree=None, content=None, name="arms") -> None:
        super().__init__(tree=tree, content=content, name=name)

    def _get_color_value(self, color):
        """
        Function that returns a list of rgb values for a color.
        """
        if color == "Black":
            return  [0, 0, 0]
        elif color == "White":
            return [1, 1, 1]
        elif color.lower() in ["gold", "silver"]:
            return color
            
        return self._split(self.content[self.content[self.columns["name"]]==color][self.columns["main"]].iat[0])

    def _get_current_prob(self):
        _prob = 1.0
        _prob *= self.tree.tree[self.current_category][self.name][self.current_color]
        return _prob

    def _make(self, color):
        
        self.current_category = color.lower()
        if not self._exclusivity_check(color):
            self.current_category = "head"
        
        self.current_color = np.random.choice(list(self.tree.tree[self.current_category][self.name].keys()), 1,
                                              p=list(self.tree.tree[self.current_category][self.name].values()))[0]
        self.current_prob = self._get_current_prob()
        if self.current_color == "same":
            self.current_color = color
        if self.current_color == "complementary":
            return self._split(self._get_complementary(color))
            
        return self._get_color_value(self.current_color)

class BellyColorPicker(ColorPicker):
    def __init__(self, tree=None, content=None, name="belly") -> None:
        super().__init__(tree=tree, content=content, name=name)

    def _get_color_value(self, color):
        """
        Function that returns a list of rgb values for a color. category: 0 - main, 1 - complementary.
        """
        
        if self._exclusivity_check(color):
            return color

        _options = len(self.content[self.content[self.columns["name"]]==color])
        return self._split(self.content[self.content[self.columns["name"]]==color][self.columns[
            "complementary"]].iat[np.random.choice(list(range(_options)))])

    def _get_current_prob(self, color):
        _prob = 1.0
        if self._exclusivity_check(color):
            return _prob * self.tree.tree[self.current_category][self.name][color]
         
        _options = len(self.content[self.content[self.columns["name"]]==color])
        if _options == 0:
            print(color)
            print(self.content[self.columns["name"]])
        return _prob * self.tree.tree[self.current_category][self.name]["complementary"] / _options

    def _make(self, color):
        
        self.current_category = color.lower()
        if not self._exclusivity_check(color):
            self.current_category = "head"
        
        self.current_color = np.random.choice(list(self.tree.tree[self.current_category][self.name].keys()), 1,
                                              p=list(self.tree.tree[self.current_category][self.name].values()))[0]
        
        self.current_color = color
        self.current_prob = self._get_current_prob(self.current_color)
        return self._get_color_value(self.current_color)

class BackGroundColorPicker(ColorPicker):
    def __init__(self, tree=None, content=None, name="background") -> None:
        super().__init__(tree=tree, content=content, name=name)

    def _get_current_prob(self, color=None):
        return 1.0 / len(self.main_colors)

    def _main_colors(self):
        
        return self.content[self.content["Name"]==self.name][self.columns["main"]].unique()

    def _make(self, **kwargs):
        self.current_category = self.name
        self.current_color = np.random.choice(self.main_colors, 1)[0]

        return self._split(self.current_color) 

class ColorGenerator:
    def __init__(self) -> None:
        self.content = {}
        self.rarity = 0
        self._clear()
        self._tree = ColorTree()
        self._rarity_calculator = ColorRarityCalculator()
        self._pickers = self._populate()

    def make(self):
        return self._make()

    def _clear(self):
        self.content = {"body": [0, 0, 0],
                        "arms": [0, 0, 0],
                        "belly": [0, 0, 0],
                        "complementary": [0, 0, 0]
                        }
    
    def _get_rarity(self):
        if self._pickers[0].current_color:
            return self._rarity_calculator.make(self._pickers)

    def _make(self):
        self._clear()
        _main_picker = [x for x in self._pickers if x.name == "generic"][0]
        self.content["body"] = _main_picker.make()
        
        for _picker in self._pickers:
            if _picker.name != "generic":
                self.content[_picker.name] = _picker.make(color=_main_picker.current_color)
        self.rarity = self._get_rarity()

    def _populate(self):
        _pickers = []
        for _picker in [ColorPicker, ArmsColorPicker, BellyColorPicker]:
            _pickers.append(_picker(self._tree))
        return _pickers

class ColorRarityCalculator:
    def __init__(self) -> None:
        self.prob = self._clear

    def make(self, pickers):
        return self._make(pickers)

    def _clear(self):
        return 1.0

    def _make(self, pickers):
        self.prob = self._clear()
        for _picker in pickers:
            if _picker.current_color:
                self.prob *= _picker.current_prob
        return self.prob


