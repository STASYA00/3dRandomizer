# import sys
# sys.path.append(SCRIPT_PATH)
# import pandas as pd

# from config import FILENAME, PROB_COL, NAME_COL


# class Database:
#     """
#     Class that contains info about the attributes and their rarity.
#     """
#     def __init__(self) -> None:
#         """
#         Class initialization.
#         """
#         self.content = self._read()

#     # def get(self, attribute_name):
#     #     """
#     #     Function that returns the rarity of an item
#     #     """
#     #     if attribute_name in list(self.content[NAME_COL]):
#     #         return self.content[PROB_COL].loc[self.content[NAME_COL]==attribute_name].iat[0]
#     #     else:
#     #         print(attribute_name)
#     #         raise AttributeError

#     def _read(self):
#         """
#         Function that loads the database content.
#         """
#         return pd.read_csv(FILENAME, delimiter=';')