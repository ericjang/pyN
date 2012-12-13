import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import save_plots#we use the save_data function


print('starting...')
save_plots('/Users/eric/Documents/College/CLPS1492/final/data/blender_data/2012-12-09_18-44-19-experiment.pkl','./')
