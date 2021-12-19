# Twickable parameters

# Output parameters
IMG_SAVE = "output"  # where to save the rendered images
IMAGE_SIZE = (500, 500)  # resolution of the output images (width, height)
RENDERS = 20  # number of images to render
ASSEMBLE_FRAME = 0  # model configuration to assemble

# Excel file
FILENAME = "colors.csv"  # path to the excel file with the color combinations
PROB_COL = "prob"  # column of the excel file with the probabilities for each color
NAME_COL = "name"  # column of the excel file with the color names

# Scene specific
RIG = "Armature"  # name of the rig object, currently not in use
CATEGORY_INDICATOR = "cat"  # symbol that is used to indicate an accessory collection
FACE_COLLECTION = "3D"
HEAD_MESH = "Head"
HEAD_SWITCH = "Mix.001"  # "2D or 3D"
MAIN_BODY = "Character"  # "Character_Low_01_A_Pose"
BGR_NAME = "Background"  # name of the background mesh object

# Bureaucratic parameters
FACES = "sample/02-Texturing/TEST"  # path to the folder with the face textures
BLEND_DIR = "blend"  # path to save the .blend files (currently not in use)
MODEL_DIR = "models"  # path to save the .obj files (currently not in use)
LOG = "json/log.json"  # filepath to log the generated configurations

D_PROB = 0.5  # probability that the face is 2D (e.g. 0.8 means 8 out of 10 will be 2D)

FRAMES = 2000  # number of frames after which the .blend file is saved (currently not in use)

MAX_PROB = 10  # scale of probability for each attribute

SCRIPT_PATH = open('setup.txt').read()[:-1]  # path to the python packages

# Renamed Arm into Arms