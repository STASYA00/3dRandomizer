from blender_utils import deselect_all, normalize_prob, select
import bpy
import numpy as np

from config import HEAD_SWITCH, D_PROB, MAIN_BODY, MAX_PROB, HEAD_MESH, FACE_COLLECTION, CATEGORY_INDICATOR
from face import FaceManager


class Attribute:
    """
    Class that stores an attribute.
    """
    def __init__(self, name):  #, prob) -> None:
        """
        Class initialization.
        :param: name        name of the attribute, str
        :param: prob        probability of this attribute to be picked, float
        """
        self.name = name
        self.material = "plastic_{}_smooth_grain".format(self.name.lower())
        self.prob = self._get_prob()
        self.current_state = True
        self.current_color = (0, 0, 0)
        self.mesh = self._load()
        self.keys = ["hide_viewport", "hide_render"]
        self.nodenames = ["Principled BSDF"]
        #self.material

    def activate(self, hide=False)-> None:
        """
        Function that activates / deactivates the attribute in the render view.
        :param: hide        activate / deactivate attr, bool
        """
        
        self.mesh.hide_render = hide
        self.mesh.hide_viewport = hide
        self.current_state = hide
        return self

    def apply(self, color=None):
        if color:
            return self._apply(color)

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current
        for key in self.keys:
            self.mesh.keyframe_insert(key, frame=frame)        

    def _apply(self, color=None):
        # Understand if one material or many
        # gold silver and stuff
        
            if isinstance(color, str):
                if color in [x.name for x in bpy.data.materials]:
                    self.mesh.active_material = bpy.data.materials[color]
            elif isinstance(color, list) or isinstance(color, set):
                
                self.mesh.active_material = bpy.data.materials[self.material]
                
                for _nodename in self.nodenames:
                    if _nodename in [x.name for x in self.mesh.active_material.node_tree.nodes]:
                        for inp in list(self.mesh.active_material.node_tree.nodes[_nodename].inputs.keys()):
                            if "Color" in inp and "Subsurface" not in inp:
                                for i in range(3):
                                    self.mesh.active_material.node_tree.nodes[_nodename].inputs[
                                        inp].default_value[i] = color[i]
            self.current_color = color

    def _get_prob(self):
        """
        Function that returns the probability of the attribute being selected.
        1 - super rare
        10 - super common
        """
        try:
            prob = int(self.name.split("_")[-2])
        except ValueError:
            prob = 10
        except IndexError:
            prob = 10
        return prob / MAX_PROB

    def _load(self):
        """
        Function that loads the attribute object as mesh.
        return: mesh, mesh
        """
        return bpy.data.objects[self.name]


class BodyAttribute(Attribute):
    """
    Class that stores an attribute.
    """
    def __init__(self, name):  #, prob) -> None:
        """
        Class initialization.
        :param: name        name of the attribute, str
        :param: prob        probability of this attribute to be picked, float
        """
        super().__init__(name)
        self.nodenames = ["Group", HEAD_SWITCH, "Principled BSDF"]
        self._clean()

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current
        for key in self.keys:
            self.mesh.keyframe_insert(key, frame=frame)
            
        if self.name != "Head":

            if self.mesh.active_material.name == self.material:
                self.mesh.active_material.node_tree.nodes["Principled BSDF"].inputs[
                    "Base Color"].keyframe_insert("default_value", frame=frame)

    def _clean(self):
        if len(self.mesh.material_slots) > 1:
            deselect_all()
            select(self.mesh)
            for i in range(1, len(self.mesh.material_slots)):
                self.mesh.active_material_index = i
                bpy.ops.object.material_slot_remove()


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
            for content in self.attributes:
                _ = content.activate(hide=hide)
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
        self.facemanager = FaceManager(bpy.data.objects[HEAD_MESH])
        self._attrfactory = AttributeFactory()
        self.current_state = 0  # 0 - 2D, 1 - 3D

    def activate(self, hide=False, content=None) -> None:
        self.collection.hide_render = hide
        self.active = []
        _prob = self._which_face(content=content)
        if not hide:
            if not _prob:
                # 2D face
                self.facemanager.make(content)
                self._hide_3d()
                self.current_state = _prob  # 0 for 2D
            else:
                # 3D face
                self.facemanager.deactivate(hide=True)

                # assemble
                if content:
                    for _facial_attr in content["attributes"]["cat0900_face"]:
                        self.active.append(self._attrfactory.produce(_facial_attr).activate())
                    return self

                # randomize
                for coll in bpy.data.collections[FACE_COLLECTION].children:
                    _objects = [self._attrfactory.produce(x.name) for x in coll.all_objects if "Empty" not in x.name]
                    if len(_objects) > 0:
                        self.active.append(np.random.choice(_objects, size=1, 
                                           p=normalize_prob([x.prob for x in _objects]))[0].activate())
                self.current_state = _prob  # 1 for 3D
                
        else:
            self.facemanager.deactivate()
            self._hide_3d()

        return self

    def set_key(self, frame=None):
        if not frame:
            frame = bpy.context.scene.frame_current
        self.facemanager.set_key(frame=frame)
        for attr in self.attributes:
            attr.set_key(frame=frame)

    def _get_prob(self):
        return 1

    def _hide_3d(self):
        for obj in self.get_children():
            obj.hide_render = True
            obj.hide_viewport = True

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
        :param: database        database with attributes and their rarity, Database
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

    # def _populate(self, attrgroup):
    #     """
    #     Function that populates the attributegroup with attributes.
    #     :param: attrgroup        attribute group to fill with its attributes, AttributeGroup
    #     """
        
    #     for name in [x.name for x in attrgroup.get_children()]:
    #         attrgroup.attributes.append(self.attrfactory.produce(name))


class AttributeFactory:
    """
    Class that produces Attribute objects.
    """
    def __init__(self, database=None) -> None:
        """
        Class initialization.
        :param: database        database storing the attribute data, Database
        """
        self.database = database
        self.body = MAIN_BODY

    def produce(self, name):
        """
        Function that produces an attribute from the given name.
        :param: name        name of the attribute, str
        return: attribute   resulting attribute, Attribute
        """
        if name in [x.name for x in bpy.data.collections[self.body].all_objects]:
            return BodyAttribute(name)
        return Attribute(name)  #, self.database.get(name))


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

