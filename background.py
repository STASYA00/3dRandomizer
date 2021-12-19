import bpy
import numpy as np

from colortree import BackGroundColorPicker
from config import BGR_NAME


class Background:
    """
    Class that stores and manages the background of the scene.
    """
    def __init__(self) -> None:
        """
        Class initialization.
        """
        self.current_color = (0,0,0)
        self.mesh = self._get_mesh()
        self.picker = BackGroundColorPicker()
        self._node_value = self.mesh.active_material.node_tree.nodes["Principled BSDF"].inputs['Base Color']
        self.key = "default_value"

    def make(self, color=None):
        """
        Function that assigns a color to the background. In case no color is given
        the color is chosen randomly from colors.csv.
        :param: color          color to assign to the background, set of floats (r, g, b)
        """
        return self._make(color)

    def set_key(self, frame=None):
        """
        Function that keyframes background's state. In Blender keyframing means assigning certain parameters
        to a certain frame. In the other frames these same parameters may vary. In this case we are freezing
        the color value of the background.
        :param: frame          frame to save the parameters to, int
        """
        if not frame:
            frame = bpy.context.scene.frame_current
        self._node_value.keyframe_insert(self.key, frame=frame)

    def _get_mesh(self):
        """
        Function that gets the object that is considered to act as a background.
        returns: background object, bpy mesh
        """
        return bpy.data.objects[BGR_NAME]

    def _make(self, color=None):
        """
        Function that assigns a color to the background. In case no color is given
        the color is chosen randomly from colors.csv.
        :param: color          color to assign to the background, set of floats (r, g, b)
        """
        if not color:
            color = self.picker.make()
        for i in range(3):
            self._node_value.default_value[i] = color[i]  # rgb values
        self.current_color = color