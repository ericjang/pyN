'''
Just to make sure STDP is working
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

A = IzhikevichPopulation(name='A', N=1, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)#tonic spiking
B = IzhikevichPopulation(name='B', N=1, a=0.02, b=0.25, c=-55, d=0.05, v0=-70, u0=None)#phasic bursting

brain = Network(populations=[A,B])
brain.connect(pre='A', post='B', synapses="none", delay=2.25,std=0.25)
brain.connect(pre='B', post='A', synapses="none", delay=2.25,std=0.25)#takes awhile for cortex to get back to thalamus?

A_stim = [{'start':1000*i,'stop':1000*i+50,'mV':14,'neurons':[0]} for i in range(10)]#stimuli spaced far enough apart such that B won't precede A
print brain.populations['B'].receiver[0]['from']
print brain.populations['B'].receiver[0]['syn']

B_stim = [{'start':1000*i+20,'stop':1000*i+70,'mV':14,'neurons':[0]} for i in range(10)]#not exactly 50 repetitions but should be enough to notice some change


results = brain.simulate(experiment_name='STDP test',T=10000,dt=0.25, I_ext={'A':A_stim,'B':B_stim}, save_data='../data/', properties_to_save=['v','psc','I_ext','spike_raster','I_rec'],stdp=True)


print brain.populations['B'].receiver[0]['syn']

show_data(results)

