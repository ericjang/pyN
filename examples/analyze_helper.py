import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

print 'starting...'
save_data('/data/people/evjang/pyN_data/2012-12-01_03-08-20-experiment.pkl','./')
