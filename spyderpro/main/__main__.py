import sys
import os

base_dir = os.getcwd()
sys.path[0] = base_dir
from spyderpro.function.TrafficFunction import TraffciFunction

if __name__ == "__main__":
    TraffciFunction().gettraffic(139)
