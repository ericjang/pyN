'''
Just to make sure STDP is working
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

simTime = 100000#if works, try 100 seconds of activity...

A = AdExPopulation(name='A', N=100, connectivity="sparse-random")
B = AdExPopulation(name='B', N=15, connectivity="sparse-random")

brain = Network(populations=[A,B])

brain.connect(pre='A', post='B', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='B', post='A', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)#since there are less inhibitory neurons, postulate more sparse projections.

props = ['v','w','psc','spike_raster','I_rec']

#the ideal behavior is that one will flatten the other, then turn everything off and see if stuff dissipates after awhile...
A_stim = [{'start':0,'stop':100,'mV':10,'neurons':[0]},{'start':200,'stop':300,'mV':10,'neurons':[0]},{'start':400,'stop':500,'mV':10,'neurons':[0]}]
B_stim = [{'start':100,'stop':200,'mV':10,'neurons':[0]},{'start':300,'stop':400,'mV':10,'neurons':[0]},{'start':500,'stop':600,'mV':10,'neurons':[0]}]

results_1 = brain.simulate(experiment_name='dual inhibition-noSTDP',T=simTime,dt=0.25, I_ext={'A':A_stim,'B':B_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=False)

save_data(results_1,'./')

results_2 = brain.simulate(experiment_name='dual inhibition-STDP',T=simTime,dt=0.125, I_ext={'A':A_stim,'B':B_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=True)

save_data(results_2,'./')



