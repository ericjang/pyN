import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

single_neuron = AdExPopulation(name='neuron', N=1)
brain = Network(populations=[single_neuron])
stim = [{'start':10,'stop':100,'mV':14,'neurons':[0]}]
results = brain.simulate(experiment_name='Single AdEx Neuron',T=100,dt=0.25,integration_time=30,I_ext={'neuron':stim}, save_data='/Users/eric/Documents/College/CLPS1492/final/data/blender_data/', properties_to_save=['v','w','psc','I_ext'])
save_plots(results,'./')
