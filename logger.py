import sys

from config import LOG, SCRIPT_PATH
from prob_calculator import ProbCalculator

sys.path.append(SCRIPT_PATH)

import json

class Logger:
    def __init__(self, value=None) -> None:
        self.content = self._load(value)
        self.name = LOG
        if value:
            self.name = value
        self._calculator = ProbCalculator()

    def make(self, character, background, frame):
        return self._make(character, background, frame)

    def save(self):
        with open(self.name, 'w') as f:
            json.dump(self.content, f)

    def _clear(self):
        return {
            "attributes": {},
            "pose": 0,
            "face": {"type": 0, 
                     "texture": "", 
                     "position": 0
                     },
            "colors": {},
            "rarity": 0.1,
            "background": (0, 0, 0)
            }

    def _load(self, value=None):
        if value:
            return json.load(open(value))
        return {}

    def _make(self, character, background, frame):
        self.content[frame] = self._clear()
        
        # body colors
        for _part in character.body.content:
            self.content[frame]["colors"][_part.name] = _part.current_color

        # background
        self.content[frame]["background"] = background.current_color

        #attributes
        for _attrgroup in character.factory.groups:
            #face
            if "face" in _attrgroup.name:
                self.content[frame]["face"]["type"] = _attrgroup.current_state
                self.content[frame]["face"]["position"] = _attrgroup.current_position
                self.content[frame]["face"]["texture"] = _attrgroup.current_texture
                
            self.content[frame]["attributes"][_attrgroup.name] = [x.name for x in _attrgroup.active]

        #rarity
        self.content[frame]["rarity"] = self._calculator.make(character)

        #pose
        #self.content[frame]["pose"] = character.posepicker.active_pose        

        return 

    