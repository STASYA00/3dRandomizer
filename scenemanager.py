import bpy

from background import Background

class SceneManager:
    def __init__(self) -> None:
        self.scene = bpy.context.scene
        self.current_frame = 0
        self.update_frame(self.current_frame)

    def make(self, character, background, frame):
        self.update_frame(frame)
        return self._make(character, background)

    def update_frame(self, frame):
        
        self.current_frame = frame
        self.scene.frame_current = self.current_frame

    def _make(self, character, background):
        # save bgr
        # 
        background.set_key(self.current_frame)
        character.set_key(self.current_frame)

    
