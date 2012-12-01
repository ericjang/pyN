'''
Just to make sure STDP is working
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

A = AdExPopulation(name='A', N=100, connectivity="none")

brain = Network(populations=[A])

simTime = 100#10 seconds of activity...
props = ['v','w','psc','spike_raster','I_rec']

A_stim = [{'start':0,'stop':simTime,'mV':10,'neurons':[0]}]

results_1 = brain.simulate(experiment_name='Epilepsy:noSTDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=False)

save_data(results_1,'./')

results_2 = brain.simulate(experiment_name='Epilepsy: STDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=True)

save_data(results_2,'./')

#attach inhibitory population to hopefully modulate A
B = AdExPopulation(name='B', N=100, connectivity="sparse-random")
brain = Network(populations=[A,B])
brain.connect(pre='A', post='B', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='B', post='A', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)



results_3 = brain.simulate(experiment_name='Epilepsy+inhibition:noSTDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=False)
save_data(results_3,'./')
results_4 = brain.simulate(experiment_name='Epilepsy+inhibition:STDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=True)
save_data(results_4,'./')
