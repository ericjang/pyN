'''
Testing to see whether it is possible to simulate for 40 seconds
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from pyN import *

A = IzhikevichPopulation(name='thalamus', connectivity="sparse-random", N=200, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)#tonic spiking

brain = Network(populations=[A])

stim = [{'start':10,'stop':200,'mV':20,'neurons':[0]},
        {'start':50,'stop':300,'mV':20,'neurons':[i for i in range(3)]}]

results = brain.simulate(experiment_name='Reentrant Thalamocortical Circuit',T=40000, dt=0.25, I_ext={'thalamus':stim}, save_data='../data/', properties_to_save=['psc','spike_raster'],stdp=True)

save_data(results,'./')#save the plots

