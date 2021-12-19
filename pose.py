import bpy
import sys

from blender_utils import select
from config import RIG, SCRIPT_PATH

sys.path.append(SCRIPT_PATH)

import numpy as np


class PosePicker:
    """
    Class that picks a random pose with equal probability for each.
    """
    def __init__(self) -> None:
        """
        Class initialization.
        """
        self.rig = bpy.data.objects[RIG]
        self.max_index = len(self.rig.pose_library.pose_markers)
        self.context = self._set_context()
        self.active_pose = 0

    def make(self):
        """
        Function that activates a random pose.
        """
        self.active_pose = np.random.randint(self.max_index)
        select(self.rig)
        bpy.ops.poselib.apply_pose(self.context, pose_index=self.active_pose)

    def _set_context(self):
        """
        Function that sets up a context to activate a pose.
        """
        for area in bpy.context.screen.areas:
            if area.type == 'PROPERTIES':
                break
        context = {'scene': bpy.context.scene,
                   'active_object': self.rig,
                   'selected_pose_bones': [x for x in self.rig.pose.bones if x.bone.select],
                   'window': bpy.context.window,
                   'screen': bpy.context.screen,
                   'area': area,
                   'region': area.regions[1],
                   'space_data': area.spaces[0]
                   }
        return context