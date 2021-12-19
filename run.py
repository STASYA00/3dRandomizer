import sys
from time import time

sys.path.append("C:/Users/STFED/_personal/gaetan")

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