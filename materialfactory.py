import bpy
import numpy as np

class MaterialFactory:
    def __init__(self) -> None:
        self.ramp = "ColorRamp"
        self.v = 0

    def produce(self, obj):
        # should the color be same for all the parts of the body?
        return self._make(obj)

    def _produce(self, obj):
        

        return

    def _produce_from_ramp(self, obj):
        mat_index = np.random.randint(0, len(obj.material_slots))
        mat_index = 0
        active_material = obj.material_slots[mat_index].material
        obj.active_material = active_material
        _ramp = [x.name for x in active_material.node_tree.nodes if self.ramp in x.name]
        if len(_ramp) > 0:
            _ramp = _ramp[0]
            node_ramp = active_material.node_tree.nodes[_ramp]
            color_index = np.random.randint(0, len(node_ramp.color_ramp.elements))
            node_ramp.inputs[0].default_value = np.random.random()