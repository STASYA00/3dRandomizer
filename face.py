import bpy
import numpy as np
import os

from blender_utils import get_nodes_link
from config import FACES, HEAD_MESH, HEAD_SWITCH
from naming import NamingProtocol

class FaceManager:
    def __init__(self, obj) -> None:
        self.path = FACES
        self.name_protocol = NamingProtocol()
        self.options = self._get()
        self.prob = self._get_prob()
        self.content = obj
        self.key = "default_value"
        self.current_texture = ""
        self.current_position = self._get_position()

    def _get(self):
        _options = []
        for img in [x for x in os.listdir(self.path) if x.endswith(".png")]:
            _options.append(img)
        return _options

    def _get_prob(self):
        return np.array([1 for x in range(len(self.options))]) / len(self.options)  # equal prob for now

    def deactivate(self, hide=True):
        return self._deactivate(hide=hide)

    def make(self, content=None):
        return self._make(content)

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current

        if self._check_material():

            # key 2D vs 3D
            _node = self.content.active_material.node_tree.nodes[HEAD_SWITCH]
            print("key1", _node.inputs[0].default_value)
            _node.inputs[0].keyframe_insert(self.key, frame=frame)
            _node.inputs[2].keyframe_insert(self.key, frame=frame)

            # key position
            _node1 = self.content.active_material.node_tree.nodes["Group"]
            print("key2", _node1.inputs[1].default_value)
            _node1.inputs[0].keyframe_insert(self.key, frame=frame)
            _node1.inputs[1].keyframe_insert(self.key, frame=frame)
    
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

    def _check_material(self):
        _nodes = [x.name for x in self.content.active_material.node_tree.nodes]
        return HEAD_SWITCH in _nodes and "Group" in _nodes

    def _deactivate(self, hide=True):
        if self._check_material():
            _node = self.content.active_material.node_tree.nodes[HEAD_SWITCH]
            _node.inputs[0].default_value = hide

    def _deactivate_old(self, hide=True):
        
        node_group = [x for x in self.content.active_material.node_tree.nodes if x.type == "GROUP"][0]
        math_node = self.content.active_material.node_tree.nodes["Math"]
        link = get_nodes_link(node_group, math_node, self.content.active_material.node_tree.links)
        link.to_socket.enabled = not hide

    def _get_position(self, content=None):
        _value = np.round(np.random.random())
        if content:
            _value = content["face"]["position"]
        self.current_position = int(_value)
        return int(1 + _value)

    def _make(self, content=None):
        if self._check_material():
            self.deactivate(hide=False)  # activate texture node
            self._position_head(self._get_position(content=content))  # choose face's position
            node_group = [x for x in self.content.active_material.node_tree.nodes if x.type == "GROUP"][0]
            node = [x for x in node_group.node_tree.nodes if x.name.startswith("Image Texture")][0]
            self.current_texture = np.random.choice(self.options, 1, p=self.prob)[0]
            if content:
                self.current_texture = content["face"]["texture"]
            self._assign_image(node, self.current_texture)

    def _position_head(self, value=1):
        if self._check_material():
            _node = self.content.active_material.node_tree.nodes["Group"]
            if value not in [1, 2]:
                value = np.random.choice([1, 2], 1)[0]
            _node.inputs[1].default_value = value

            # for 3D
            # for obj in facial_attributes:
            #     obj.active_shape_key.value = value

class Face:
    def __init__(self) -> None:
        self.category = 0  # 0 - 2D, 1 - 3D

    def make(self, content=None):
        return self._make(content)

    def _check_material(self):
        _nodes = [x.name for x in self.content.active_material.node_tree.nodes]
        return HEAD_SWITCH in _nodes and "Group" in _nodes

    def _make(self, content=None):
        if self._check_material():
            self.deactivate(hide=False)  # activate texture node
            self._position_head(self._get_position(content=content))  # choose face's position
            node_group = [x for x in self.content.active_material.node_tree.nodes if x.type == "GROUP"][0]
            node = [x for x in node_group.node_tree.nodes if x.name.startswith("Image Texture")][0]
            self.current_texture = np.random.choice(self.options, 1, p=self.prob)[0]
            if content:
                self.current_texture = content["face"]["texture"]
            self._assign_image(node, self.current_texture)

    def _position_head(self, value=1):
        if self._check_material():
            _node = self.content.active_material.node_tree.nodes["Group"]
            if value not in [1, 2]:
                value = np.random.choice([1, 2], 1)[0]
            _node.inputs[1].default_value = value


class Face3D(Face):
    def __init__(self) -> None:
        Face.__init__(self)
        self.category = 1  # 0 - 2D, 1 - 3D'
        self.attributes = []

    def _position_head(self, value=1):
        if value not in [1, 2]:
            value = np.random.choice([1, 2], 1)[0]
        for _face_attr in self.attributes:
            _face_attr.active_shape_key.value = value





        
