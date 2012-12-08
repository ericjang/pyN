'''
Implementation of the network shown in
http://grey.colorado.edu/CompCogNeuro/index.php/CCNBook/Motor

'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *





A = IzhikevichPopulation(name='thalamus', N=100, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)#tonic spiking
B = IzhikevichPopulation(name='cortex', N=50, a=0.02, b=0.25, c=-55, d=0.05, v0=-70, u0=None)#phasic bursting

brain = Network(populations=[A,B])
brain.connect(pre='thalamus', post='cortex', synapses="sparse-random")
brain.connect(pre='cortex', post='thalamus', synapses="sparse-random", delay=2.25,std=0.25)#takes awhile for cortex to get back to thalamus?

stim = [{'start':10,'stop':200,'mV':20,'neurons':[0]},{'start':50,'stop':300,'mV':30,'neurons':[i for i in range(3)]}]
results = brain.simulate(experiment_name='Reentrant Thalamocortical Circuit',T=600,dt=0.25, integration_time=30, I_ext={'thalamus':stim}, save_data='../data/', properties_to_save=['v','u','psc','I_ext'])
show_data(results)

