import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN import *
import time

start_time = time.time()


thalamus = IzhikevichPopulation(name='thalamus', N=100, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None, connectivity="sparse-random")
brain = Network(populations=[thalamus])
stim = [{'start':10,'stop':100,'mV':14,'neurons':[0,1]}]
results = brain.simulate(T=1000,dt=0.25,integration_time=30,I_ext={'thalamus':stim}, save_data='../data/', properties_to_save=['v','u','psc'])
show_data(results)

elapsed_time = time.time() - start_time
print elapsed_time
