import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

my_neurons = IzhikevichPopulation(name='group', N=10, a=0.01, b=0.2, c=-65, d=8, v0=-70, u0=None, connectivity="full-random")
brain = Network(populations=[my_neurons])
stim = [{'start':10,'stop':100,'mV':14,'neurons':[0,1,2]}]
results = brain.simulate(experiment_name='Network of Spike-Frequency-Adapting Neurons',T=100,dt=0.25,integration_time=30,I_ext={'group':stim}, save_data='../data/', properties_to_save=['v','u','psc','I_ext'])
show_data(results)
