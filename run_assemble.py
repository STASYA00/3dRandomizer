import os
import sys
from time import time

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from config import ASSEMBLE_FRAME
from pipeline import AssemblePipeline

if __name__=="__main__":
    t1 = time()
    pipe = AssemblePipeline(ASSEMBLE_FRAME)
    pipe.run()
    print(time() - t1)