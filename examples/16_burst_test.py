'''
things to watch out for:
	- see if it becomes self sustaining or whether it eventually dissipates
	- see if STDP is causing network to go nuts.
ij
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

simTime = 1000#10 seconds of activity...

A = AdExPopulation(name='A', N=100, connectivity="sparse-random")

brain = Network(populations=[A])

props = ['v','w','psc','spike_raster','I_rec']

#the ideal behavior is that one will flatten the other, then turn everything off and see if stuff dissipates after awhile...
A_stim = [{'start':0,'stop':0,'mV':0,'neurons':[0]}]

results_1 = brain.simulate(experiment_name='goingNuts_dissipation-noSTDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=False)

save_data(results_1,'./')

results_2 = brain.simulate(experiment_name='goingNuts_dissipation-STDP',T=simTime,dt=0.25, I_ext={'A':A_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=props, stdp=True)

save_data(results_2,'./')



