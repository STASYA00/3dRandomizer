import bpy
import os
import sys



file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from assembler import Assembler
from background import Background
from character import Character
from config import FRAMES, LOG
#from database import Database
from logger import Logger
from renderer import Renderer
from scenemanager import SceneManager

class Pipeline:
    """
    Generic pipeline class.
    """
    def __init__(self, value: int) -> None:
        """
        Class initialization.
        :param: value       value, int
        """
        self.value = value

    def run(self):
        """
        Function that executes the pipeline.
        """
        return self._run()

    def _run(self):
        """
        Function that executes the pipeline.
        """
        return 0


class AssemblePipeline(Pipeline):
    """
    Pipeline that creates different character configurations.
    """
    def __init__(self, value: int) -> None:
        """
        Class initialization.
        :param value        character configuration number to reproduce, int.
        """
        super().__init__(value)

    def _run(self):
        """
        Function that creates a character configuration from a number of parameters.
        """
        log = Logger(value=LOG)
        assembler = Assembler()
        renderer = Renderer()
        assembler.make(log.content[str(self.value)])
        renderer.render(filename="compare_" + str(self.value))


class InitializePipeline(Pipeline):
    """
    Pipeline that creates different character configurations.
    """
    def __init__(self, value: int) -> None:
        """
        Class initialization.
        :param value        amount of character configurations to create, int.
        """
        super().__init__(value)

    def _run(self):
        """
        Function that creates different character configurations.
        """
        background = Background()
        character = Character()
        renderer = Renderer()
        background.make()
        character.factory._deactivate_all()
        renderer.render(filename="deactivated")
        character.make()
        renderer.render(filename="after_deactivation")


class MainPipeline(Pipeline):
    """
    Pipeline that creates different character configurations.
    """
    def __init__(self, value: int) -> None:
        """
        Class initialization.
        :param value        amount of character configurations to create, int.
        """
        super().__init__(value)

    def _run(self):
        """
        Function that creates different character configurations.
        """
        #database = Database()
        log = Logger()
        background = Background()
        character = Character()
        renderer = Renderer()
        #scenemanager = SceneManager()
        for i in range(self.value):
            print("EPOCH {}".format(i))
            #scenemanager.update_frame(i)
            background.make()
            character.make()
            log.make(character, background, i)
            #scenemanager.make(character, background=background, frame=i)
            renderer.render(filename=str("%04d" % i)) #+ "_{}".format(character.get_name()))

            # if i % FRAMES == 0 and i > 0:
            #     character.save(filename="{}".format(i))
            
        log.save()
        character.save(filename="test")  #(filename="%04d" % i)

