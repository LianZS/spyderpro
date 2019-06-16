import sys
import os

base_dir = os.getcwd()
sys.path[0] = base_dir
from spyderpro.FunctionMain.TrafficFunction import TraffciFunction
from spyderpro.FunctionMain.ScenceFunction import ScenceFunction
if __name__ == "__main__":
    # TraffciFunction().gettraffic(139)
    ScenceFunction().gettraffic(315)
