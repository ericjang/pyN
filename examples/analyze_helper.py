import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

save_data('../data/2012-11-29_11-32-16-experiment.pkl','./')
