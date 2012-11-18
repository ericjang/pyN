from AdEx import *


single_neuron = Population(N=1,name='bob',connectivity="none")
brain = Network(populations=[single_neuron])
stim = [{'start':10,'stop':20,'mV':10},{'start':30,'stop':40,'mV':20}]
results = brain.simulate(T=100,dt=0.25,I_inj={'bob':stim})#simulate for 50 msec, stimulating the thalamus
load_data(results)