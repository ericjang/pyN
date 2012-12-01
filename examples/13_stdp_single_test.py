'''
Just to make sure STDP is working
'''

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *

A = AdExPopulation(name='A', N=1)

brain = Network(populations=[A])

a_stim = [{'start':0,'stop':1000,'mV':14,'neurons':[0]}]

results = brain.simulate(experiment_name='STDP test',T=1000,dt=0.25, I_ext={'A':a_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=['v','psc','spike_raster','I_rec'],stdp=True)



save_data(results,'./')

