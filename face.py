import bpy
import os
import sys

from attrfactory import AttributeFactory
from blender_utils import normalize_prob
from config import FACE_COLLECTION, FACES, HEAD_MESH, HEAD_SWITCH, SCRIPT_PATH
from naming import NamingProtocol

sys.path.append(SCRIPT_PATH)

import numpy as np


class Face:
    def __init__(self, name) -> None:
        self.active = []
        self._attrfactory = AttributeFactory()
        self.collection = bpy.data.collections[name]
        self.attributes = self._populate()  # list of Attributes
        self.category = 0  # 0 - 2D, 1 - 3D
        
        self.current_texture = ""
        self.current_position = -1
        self.head = bpy.data.objects[HEAD_MESH]
        self.options = self._get()
        self.key = "default_value"

    def activate(self, content=None, hide=False):  # default option: random activation
        self._deactivate(hide=True)
        if not hide:
            self._make(content)
        self.current_position = self._position_head(content) - 1

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current

        if self._check_material():
            # key 2D vs 3D
            _node = self.head.active_material.node_tree.nodes[HEAD_SWITCH]
            _node.inputs[0].keyframe_insert(self.key, frame=frame)
            _node.inputs[2].keyframe_insert(self.key, frame=frame)

            # key position
            _node1 = self.head.active_material.node_tree.nodes["Group"]
            _node1.inputs[0].keyframe_insert(self.key, frame=frame)
            _node1.inputs[1].keyframe_insert(self.key, frame=frame)

    def _assemble(self, content):
        return

    def _check_material(self):
        _nodes = [x.name for x in self.head.active_material.node_tree.nodes]
        return HEAD_SWITCH in _nodes and "Group" in _nodes

    def _deactivate(self, hide=True):
        return

    def _get(self):
        return []

    def _get_children(self):
        return [x for x in self.collection.all_objects if "Empty" not in x.name]

    def _get_position(self, content=None):
        _value = np.round(np.random.random())
        if content:
            _value = content["face"]["position"]
        self.current_position = int(_value)
        return _value

    def _get_prob(self):
        return np.array([1 for x in range(len(self.options))]) / len(self.options)  # equal prob for now

    def _make(self, content=None):
        self.active = []
        if content:  # assemble
            self._assemble(content)
        else:  # randomize
            self._random_choice()

    def _populate(self):
        """
        Function that populates the attributegroup with attributes.
        :param: attrgroup        attribute group to fill with its attributes, AttributeGroup
        """
        _attributes = []
        for name in [x.name for x in self._get_children()]:
            _attributes.append(self._attrfactory.produce(name))
        return _attributes

    def _position_head(self, content=None):
        return self._get_position(content)

    def _random_choice(self):
        return


class Face2D(Face):
    def __init__(self, name) -> None:
        Face.__init__(self, name)
        self.category = 0
        self.name_protocol = NamingProtocol()
    
    def _assemble(self, content):
        self.current_texture = content["face"]["texture"] 

    def _assign_image(self, node, new_image):
        path = os.path.dirname(__file__) + '/'
        try:
            if not new_image in [x.name for x in bpy.data.images]:
                bpy.ops.image.open(filepath=path + self.name_protocol.material_path.format(new_image))
            else:                
                path1 = bpy.data.images[new_image].filepath[4:].replace('//', '/').replace('\\\\', '/').replace('\\', '/')
                other_path = path + self.name_protocol.material_path.format(new_image)
                other_path = other_path[3:].replace('//', '/').replace('\\\\', '/').replace('\\', '/')
                if path1 != other_path:
                    bpy.data.images[new_image].filepath = path + self.name_protocol.material_path.format(new_image)
            node.image = bpy.data.images[new_image]
            
        except Exception as e:
            print('Failed to load {} texture'.format(new_image))
            print(repr(e))
            self.current_texture = "Failed to load"

    def _deactivate(self, hide=True):
        if hide:
            self.current_texture = ""
            self.current_position = -1
        if self._check_material():
            _node = self.head.active_material.node_tree.nodes[HEAD_SWITCH]
            _node.inputs[0].default_value = hide

    def _get(self):
        _options = []
        for img in [x for x in os.listdir(FACES) if x.endswith(".png")]:
            _options.append(img)
        return _options

    def _make(self, content=None):
            node_group = [x for x in self.head.active_material.node_tree.nodes if x.type == "GROUP"]
            if node_group:
                node_group = node_group[0]
                node = [x for x in node_group.node_tree.nodes if x.name.startswith("Image Texture")][0]
                
            if content:
                self._assemble(content)
            else:
                self._random_choice()
            self._deactivate(hide=False)
            self._assign_image(node, self.current_texture)

    def _position_head(self, content=None):
        value = self._get_position(content) + 1
        if self._check_material():
            _node = self.head.active_material.node_tree.nodes["Group"]
            if value not in [1, 2]:
                value = np.random.choice([1, 2], 1)[0]
            _node.inputs[1].default_value = value
        return value

    def _random_choice(self):
        self.current_texture = np.random.choice(self.options, 1, p=self._get_prob())[0]


class Face3D(Face):
    def __init__(self, name) -> None:
        Face.__init__(self, name)
        self.category = 1  # 0 - 2D, 1 - 3D'

    def set_key(self, frame=None):
        for attr in self.attributes:
            attr.set_key(frame=frame)

    def _assemble(self, content):
        if content:
            for _facial_attr in content["attributes"]["cat0900_face"]:
                self.active.append(self._attrfactory.produce(_facial_attr).activate())

    def _deactivate(self, hide=True):
        self.active = []
        self.current_position = -1
        for obj in self.attributes:
            obj.mesh.hide_render = hide
            obj.mesh.hide_viewport = hide

    def _get(self):
        """
        Function that returns all the attributes of the attribute group as mesh.
        return: list of objects in the group, list of mesh
        """
        return [x for x in self.collection.all_objects if "Empty" not in x.name]

    def _position_head(self, content=None):
        value = self._get_position(content)
        if value not in [0, 1]:
            value = np.random.choice([0, 1], 1)[0]
        for _face_attr in self.active:
            if _face_attr.mesh.active_shape_key:
                _face_attr.mesh.active_shape_key.value = value
        return value

    def _random_choice(self):
        for coll in bpy.data.collections[FACE_COLLECTION].children:
            _objects = [self._attrfactory.produce(x.name) for x in coll.all_objects if "Empty" not in x.name]
            if len(_objects) > 0:
                self.active.append(np.random.choice(_objects, size=1, 
                                    p=normalize_prob([x.prob for x in _objects]))[0].activate())





        
