import sys

from background import Background
from character import Character

class Assembler:
    def __init__(self) -> None:
        self.background = Background()
        self.character = Character()

    def make(self, content):
        return self._make(content)

    def _make(self, content):
        
        # make background
        self.background.make(color=content["background"])
        # make character
        self.character.make(content=content)
        
