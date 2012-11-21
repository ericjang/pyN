import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

single_neuron = IzhikevichPopulation(name='tonic spiking', N=1, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
brain = Network(populations=[single_neuron])
stim = [{'start':10,'stop':100,'mV':14}]
results = brain.simulate(T=100,dt=0.25,I_ext={'tonic spiking':stim}, save_data='../data/', properties_to_save=['v','u','psc'])
show_data(results)
