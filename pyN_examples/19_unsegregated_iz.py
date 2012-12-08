'''
izhikevich verison of #14
although network is chaotic, starting to produce some interesting results..

'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from pyN import *

#substantia nigra releases dopamine. Stimulate this when good things happen. This one is special. because it is excitatory towards Go and inhibitory towards NoGo.
#tonic bursting parameters
SNc      = IzhikevichPopulation(name='snc',N=60,a=0.02,b=0.25, c=-50,d=2,v0=-70, connectivity="sparse-random")

Go_add   = IzhikevichPopulation(name='Go+', N=40, connectivity="sparse-random")
Go_sub   = IzhikevichPopulation(name='Go-', N=40, connectivity="sparse-random")
NoGo_add = IzhikevichPopulation(name='NoGo+',N=40, connectivity="sparse-random")
NoGo_sub = IzhikevichPopulation(name='NoGo-',N=40, connectivity="sparse-random")

#these inhibitory populations act to balance out activity and prevent go/nogo from going nuts when (not) driven by dopamine.
#Go_inhib = IzhikevichPopulation(name='go_inhib',N=8,connectivity="sparse-random")
#NoGo_inhib = IzhikevichPopulation(name='nogo_inhib',N=8,connectivity="sparse-random")

GPi = IzhikevichPopulation(name='gpi',N=40, connectivity="sparse-random")
GPe  = IzhikevichPopulation(name='gpe',N=40, connectivity="sparse-random")

thal_in = IzhikevichPopulation(name='thal_in',N=120,connectivity="sparse-random", scale=2.0)#where sensory info goes in
thal_add = IzhikevichPopulation(name='thal+',N=40, connectivity="sparse-random")#where motor output comes out
thal_sub = IzhikevichPopulation(name='thal-',N=40, connectivity="sparse-random")

PFC  = IzhikevichPopulation(name='pfc', N=340, connectivity="sparse-random")
#gain modulator for PFC
PFC_inhib = IzhikevichPopulation(name='pfc_inhib',N=60,connectivity="sparse-random")
brain = UnsegDopaNetwork(populations=[SNc, Go_add, NoGo_add, Go_sub, NoGo_sub, GPi, GPe, thal_in, thal_add, thal_sub, PFC, PFC_inhib])
#set up the excitatory connections between the populations

#SNc -> excitatory to Go+/- and inhibitory to NoGo +/-
brain.connect(pre='snc', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

#Go/NoGo Balanced by inhibitory population

#frontal cortex -> excitatory connections to all the go populations
brain.connect(pre='pfc', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc', post='NoGo+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc', post='NoGo-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#Go inhibits GPi
brain.connect(pre='Go+',post='gpi', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='Go-',post='gpi', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

#NoGo inhibits Gpe (disinhibited)
brain.connect(pre='NoGo+',post='gpe', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='NoGo-',post='gpe', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

brain.disconnect(pre='NoGo+',post='gpe')
brain.disconnect(pre='NoGo-',post='gpe')

#GPe inhibits GPi
brain.connect(pre='gpe', post='gpi', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

#GPi inhibits Thalamus (disinhibited)
brain.connect(pre='gpi', post='thal+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='gpi', post='thal-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.disconnect(pre='gpi', post='thal+')
brain.disconnect(pre='gpi', post='thal-')

#thalamus bidirectional activity to PFC
brain.connect(pre='pfc', post='thal+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc', post='thal-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc', post='thal_in', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal+', post='pfc', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal-', post='pfc', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal_in', post='pfc', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)


#PFC 15% inhibition gain modulation
brain.connect(pre='pfc', post='pfc_inhib', synapses="sparse-random", mode='excitatory')
brain.connect(pre='pfc_inhib', post='pfc', synapses="sparse-random", mode='inhibitory')

#####
#run the network for a goal of 10 seconds
#####

results1 = brain.simulate(experiment_name='seg-iz-unsegregated', T=30000, dt=0.25, save_data='/data/people/evjang/pyN_data/', properties_to_save=['v'],stdp=True)
save_data(results1,'./')
#results2 = brain.simulate(experiment_name='modelock-nocrossinhib-longer', T=30000, dt=0.250, save_data='/data/people/evjang/pyN_data/', properties_to_save=['v','psc','spike_raster','I_rec'],stdp=True)
#save_data(results2,'./')
