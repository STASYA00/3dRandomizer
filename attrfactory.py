import bpy

from config import MAIN_BODY
from attribute import Attribute, BodyAttribute


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