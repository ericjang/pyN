import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

ten_neurons = IzhikevichPopulation(name='ten neurons', N=10, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None, connectivity="full-random")
brain = Network(populations=[ten_neurons])
stim = [{'start':100,'stop':100,'mV':14,'neurons':[0]}]
results = brain.simulate(T=122,dt=0.25,integration_time=30,I_ext={'ten neurons':stim}, save_data='/Users/eric/Documents/College/CLPS1492/final/data/blender_data/', properties_to_save=['v','spike_raster'], stdp=True)

save_data(results,'./')
