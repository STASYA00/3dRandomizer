import bpy

from blender_utils import deselect_all, select
from config import HEAD_SWITCH, MAX_PROB



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



    # def _populate(self, attrgroup):
    #     """
    #     Function that populates the attributegroup with attributes.
    #     :param: attrgroup        attribute group to fill with its attributes, AttributeGroup
    #     """
        
    #     for name in [x.name for x in attrgroup.get_children()]:
    #         attrgroup.attributes.append(self.attrfactory.produce(name))



