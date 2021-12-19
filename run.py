import os
import sys
from time import time

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from config import RENDERS
from pipeline import MainPipeline, InitializePipeline, AssemblePipeline

if __name__=="__main__":
    t1 = time()
    pipe = MainPipeline(RENDERS)
    pipe.run()
    print(time() - t1)

# 400x400  50 renders - 215 sec
#          5 renders - 88 sec
# 1Kx1K    50 renders - 12698 sec