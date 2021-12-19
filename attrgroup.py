import bpy
import sys

from attrfactory import AttributeFactory
from blender_utils import normalize_prob
from config import CATEGORY_INDICATOR, D_PROB, SCRIPT_PATH
from face import Face2D, Face3D

sys.path.append(SCRIPT_PATH)

import numpy as np


class AttributeGroup:
    """
    Class that stores an attribute group.
    """
    def __init__(self, name) -> None:
        """
        Class initialization.
        :param: name        name of the group, str
        """
        self.name = name
        self.prob = self._get_prob()
        self.collection = self._load()
        self._attrfactory = AttributeFactory()
        self.attributes = self._populate()
        self.active = []

    def activate(self, hide=False, content=None):
        """
        Function that activates the attribute group and one attribute in it.
        :param: hide        activation / deactivation of the group
        """
        self.active = []
        self.collection.hide_render = hide
        if hide:
            for obj in self.get_children():
                obj.hide_render = hide
                obj.hide_viewport = hide
            for _attr in self.attributes:
                _ = _attr.activate(hide=hide)
        else:
            # if the attribute to activate is known
            if content:
                for _attr in content:
                    self.active.append(self._attrfactory.produce(_attr).activate())
                return
            # pick random attribute from the group
            if len(self.attributes) > 0:
                self.active.append(np.random.choice(self.attributes, size=1, 
                                            p=normalize_prob(np.array([x.prob for x in self.attributes])))[0].activate())

    def apply(self, color=None):
        return self._apply(color)
    
    def get_children(self):
        """
        Function that returns all the attributes of the attribute group as mesh.
        return: list of objects in the group, list of mesh
        """
        return [x for x in self.collection.all_objects if "Empty" not in x.name]

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current
        for attr in self.attributes:
            attr.set_key(frame=frame)

    def _apply(self, color=None):
        for _active in self.active:
            _active.apply(color)
    
    def _get_prob(self):
        return AttributeGroupProb().get(self.name)
    
    def _load(self):
        """
        Function that returns the collection object of the attribute group.
        """
        return bpy.data.collections[self.name]

    def _populate(self):
        """
        Function that populates the attributegroup with attributes.
        :param: attrgroup        attribute group to fill with its attributes, AttributeGroup
        """
        _attributes = []
        for name in [x.name for x in self.get_children()]:
            _attributes.append(self._attrfactory.produce(name))
        return _attributes


class FaceAttributeGroup(AttributeGroup):
    def __init__(self, name):
        super().__init__(name)
        #self.facemanager = FaceManager(bpy.data.objects[HEAD_MESH])
        self._attrfactory = AttributeFactory()
        
        self.current_position = 0
        self.current_state = 0  # 0 - 2D, 1 - 3D
        self.current_texture = ""

        self.face2d = Face2D(name)
        self.face3d = Face3D(name)

    def activate(self, hide=False, content=None) -> None:
        self.collection.hide_render = hide
        self.active = []
        _prob = self._which_face(content=content)

        if not hide:
            self.face2d.activate(content=content, hide=_prob)
            self.face3d.activate(content=content, hide=not _prob)
            
            self.current_position = self._get_position()
            self.current_state = int(_prob)
            self.current_texture = self.face2d.current_texture
            self.active = self.face3d.active

        else:
            self.face2d.activate(hide=True)
            self.face3d.activate(hide=True)

        return self

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current
        self.face2d.set_key(frame=frame)
        self.face3d.set_key(frame=frame)

    def _get_position(self):
        return max(self.face2d.current_position, self.face3d.current_position)

    def _load(self):
        return bpy.data.collections[self.name]

    def _which_face(self, content=None):
        if content:
            return content["face"]["type"]
        return np.random.random() > D_PROB


class AttributeGroupFactory:
    """
    Class that produces Attribute Group classes.
    """
    def __init__(self, database=None) -> None:
        """
        Class initialization.
        """
        #self.database = database
        # self.attrfactory = AttributeFactory(database)
        pass

    def produce(self, name):
        """
        Function that produces an AttributeGroup from a given name.
        :param: name         name of the attribute group, str
        return: attrgroup    new attributegroup, AttributeGroup
        """
        
        if "face" not in name:
            a = AttributeGroup(name)
        else:
            a = FaceAttributeGroup(name)
        return a


class AttributeGroupProb:
    def __init__(self) -> None:
        self._special = ["face", "shoe", "feet"]
        self.default = 0.9
        self.content = self._load()

    def get(self, group):
        try:
            return self.content[group]
        except Exception:
            return self.default

    def _load(self):
        _groups = {}
        for name in [x.name for x in bpy.data.collections if x.name.startswith(CATEGORY_INDICATOR)]:
            _groups[name] = self.default
            for _sp in self._special:
                if _sp in name:
                    _groups[name] = 1.0
                    continue
            
        return _groups