import bpy
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from attrfactory import AttributeFactory
from blender_utils import deselect_all
from colortree import ColorGenerator
from config import MODEL_DIR, BLEND_DIR, MAIN_BODY, HEAD_SWITCH
from factory import CharacterFactory
from pose import PosePicker

class Character:
    """
    Class containing the character.
    """
    def __init__(self, database=None):
        """
        Class initialization.
        :param: database        database with attributes and their rarity, Database
        """
        self.name = MAIN_BODY
        # self.mesh = self._load()
        
        self.factory = CharacterFactory(database)
        self.body = Body()
        
        #self.posepicker = PosePicker()

    def get_name(self):
        _naming = ""
        for group in self.factory.groups:
            if group.active:
                for obj in group.active:
                    _naming += "{}_".format(obj.name)
        _naming += str(self.posepicker.active_pose)
        return _naming[:200]

    def make(self, content=None):
        """
        Function that generates a new configuration of a character.
        """
        return self._make(content)

    def save(self, filename='test', ext='blend'):
        """
        Function that saves the building as a separate file.
        :param filename: name of the file to write without extension, str,
        default='test'
        :param ext: file extension, str, default='obj'
        :return:
        """
        deselect_all()
        if not MODEL_DIR in os.listdir(file_dir):
            os.mkdir(file_dir + '/' + MODEL_DIR)
        if ext == 'obj':
            bpy.ops.export_scene.obj(filepath='{}/{}/{}.{}'.format(file_dir, MODEL_DIR,
                                                                   filename, ext),
                                    use_selection=False)
        elif ext == 'blend':
            if not BLEND_DIR in os.listdir():
                os.mkdir(BLEND_DIR)
            bpy.ops.wm.save_as_mainfile(filepath='{}/{}.blend'.format(BLEND_DIR,
                                                                        filename))
        else:
            return NotImplementedError

    def set_key(self, frame):
        for group in self.factory.groups:
            group.set_key(frame)
        #self.posepicker.set_key(frame)
        self.body.set_key(frame)

    def _load(self):
        return bpy.data.objects[self.name]

    def _make(self, content=None):
        """
        Function that generates a new configuration of a character.
        """
        self.body.make(content)
        self.factory.produce(content)
        #self.posepicker.make()


class Body:
    def __init__(self) -> None:
        self.name = MAIN_BODY
        self.exclusive = False  # Body is of a special color: gold or silver
        self._factory = AttributeFactory()
        self.color_gen = ColorGenerator()
        self.mapping = {"Arms": "arms",
                        "Body": "belly",
                        "Head": "body"
        }
        self.content = self._populate()


    def make(self, content=None):
        return self._make(content)

    def set_key(self, frame):
        if not frame:
            frame = bpy.context.scene.frame_current
        for _part in self.content:
            _part.set_key(frame)

    def _make(self, content=None):
        if not content:
            self.color_gen.make()
        for _part in self.content:
            _part.activate()
            if not content:
                _part.apply(color=self.color_gen.content[self.mapping[_part.name]])
            else:
                _part.apply(color=content["colors"][_part.name])
            
        if isinstance(self.color_gen.content["body"], str):
            self.exclusive = True

    def _populate(self):
        _body = []
        for _part in [x.name for x in bpy.data.collections[MAIN_BODY].all_objects]:
            _body.append(self._factory.produce(_part))
        return _body
