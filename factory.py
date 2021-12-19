import bpy
import numpy as np

from attribute import AttributeGroupFactory, FaceAttributeGroup
from config import CATEGORY_INDICATOR


class CharacterFactory:
    """
    Class that generates a character configuration.
    """
    def __init__(self, database=None) -> None:
        """
        Class initialization.
        :param database         database of elements and probabilities, Database
        """
        
        self.attrGrFactory = AttributeGroupFactory(database)
        self.groups = self._populate()

    def produce(self, content=None):
        """
        Function that produces a character configuration: activates the necessary 
        attribute groups and attributes.
        """
        return self._produce(content)

    def _deactivate_all(self):
        for group in self.groups:
            group.activate(hide=True)

    def _populate(self):
        """
        Function that returns a list of attribute groups and their probabilities.
        """
        _groups = [] 
        for name in [x.name for x in bpy.data.collections if x.name.startswith(CATEGORY_INDICATOR)]:
            _groups.append(self.attrGrFactory.produce(name))
        return _groups

    def _produce(self, content=None):
        """
        Function that activates attributes based on their rarity.
        """
        
        self._deactivate_all()
        for group in self.groups:
            _hide = np.random.random() > group.prob
            _attr = None
            if content:
                _attr = content["attributes"][group.name]
                _hide = len(_attr) == 0
                if isinstance(group, FaceAttributeGroup):
                    _hide = False
                    _attr = content
            group.activate(hide=_hide, content=_attr)
        
