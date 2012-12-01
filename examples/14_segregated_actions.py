'''
Segregated version of #12

Things to try:
- Go/NoGo populations also inhibit each other (so no two actions can fire at once)

'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from pyN import *

#substantia nigra releases dopamine. Stimulate this when good things happen. This one is special. because it is excitatory towards Go and inhibitory towards NoGo.


SNc      = AdExPopulation(name='snc',N=20, connectivity="sparse-random")

Go_add   = AdExPopulation(name='Go+', N=30, connectivity="sparse-random")
Go_sub   = AdExPopulation(name='Go-', N=30, connectivity="sparse-random")
NoGo_add = AdExPopulation(name='NoGo+',N=30, connectivity="sparse-random")
NoGo_sub = AdExPopulation(name='NoGo-',N=30, connectivity="sparse-random")

GPi_add  = AdExPopulation(name='gpi+',N=20, connectivity="sparse-random")
GPi_sub  = AdExPopulation(name='gpi-',N=20, connectivity="sparse-random")
GPe_add  = AdExPopulation(name='gpe+',N=20, connectivity="sparse-random")
GPe_sub  = AdExPopulation(name='gpe-',N=20, connectivity="sparse-random")

thal_in = AdExPopulation(name='thal_in',N=20,connectivity="sparse-random")#where sensory info goes in
thal_add = AdExPopulation(name='thal+',N=20, connectivity="sparse-random")#where motor output comes out
thal_sub = AdExPopulation(name='thal-',N=20, connectivity="sparse-random")

PFC_add  = AdExPopulation(name='pfc+', N=42, connectivity="sparse-random")
PFC_sub  = AdExPopulation(name='pfc-', N=42, connectivity="sparse-random")


'''
In order for stability to occur in cortex, each should also have 15 percent inhibitory neurons? Do the cortex for now.
If the other parts of brain also go nuts consider adding inhibitory neurons to those as well.
'''
PFC_inhib = AdExPopulation(name='pfc_inhib',N=15,connectivity="sparse-random")



brain = DopaNetwork(populations=[SNc, Go_add, NoGo_add, Go_sub, NoGo_sub, GPi_add, GPe_add, GPi_sub, GPe_sub, thal_in, thal_add, thal_sub, PFC_add, PFC_sub, PFC_inhib])
#set up the excitatory connections between the populations

#SNc -> excitatory to Go+/- and inhibitory to NoGo +/-
brain.connect(pre='snc', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

#frontal cortex -> excitatory connections to all the go populations
brain.connect(pre='pfc+', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc+', post='NoGo+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='NoGo-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#Go inhibits GPi
brain.connect(pre='Go+',post='gpi+', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='Go-',post='gpi-', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

#NoGo inhibits Gpe (disinhibited)
brain.connect(pre='NoGo+',post='gpe+', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='NoGo-',post='gpe-', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

brain.disconnect(pre='NoGo+',post='gpe+')
brain.disconnect(pre='NoGo-',post='gpe-')

#GPe inhibits GPi
brain.connect(pre='gpe+', post='gpi+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='gpe+', post='gpi-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

#GPi inhibits Thalamus (disinhibited)
brain.connect(pre='gpi+', post='thal+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='gpi-', post='thal-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.disconnect(pre='gpi+', post='thal+')
brain.disconnect(pre='gpi-', post='thal-')

#thalamus bidirectional activity to PFC
brain.connect(pre='pfc+', post='thal+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='thal-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

brain.connect(pre='thal+', post='pfc+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal-', post='pfc-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

brain.connect(pre='thal_in', post='pfc+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal_in', post='pfc-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#PFC 15% inhibition
brain.connect(pre='pfc+', post='pfc_inhib', synapses="sparse-random", mode='excitatory')
brain.connect(pre='pfc-', post='pfc_inhib', synapses="sparse-random", mode='excitatory')
brain.connect(pre='pfc_inhib', post='pfc+', synapses="sparse-random", mode='inhibitory')
brain.connect(pre='pfc_inhib', post='pfc-', synapses="sparse-random", mode='inhibitory')

#####
#run the network for a goal of 10 seconds
#####
simTime = 10000

#Suppose SNc constantly generating Dopamine and synapse connect to simulate 'bursting'
snc_stim = [{'start':0,'stop':simTime,'mV':14,'neurons':[0]}]
#GPe is tonically active
gpe_stim = [{'start':0,'stop':simTime,'mV':14,'neurons':[0]}]
#thalamus also receives sensory input -> in the future transition to environmental input from 3D world
thal_stim = [{'start':0,'stop':10,'mV':14,'neurons':[i for i in range(5)]}]

results1 = brain.simulate(experiment_name='Dopaminergic STDP Reinforcement Learning - no STDP',T=simTime, dt=0.125, I_ext={'thal_in':thal_stim,'gpe+':gpe_stim, 'gpe-':gpe_stim, 'snc':snc_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=['psc','spike_raster','I_rec'],stdp=False)

save_data(results1,'./')#save the plots -> analyze the plots separately.

results2 = brain.simulate(experiment_name='Dopaminergic STDP Reinforcement Learning - with STDP',T=simTime, dt=0.125, I_ext={'thal_in':thal_stim,'gpe+':gpe_stim, 'gpe-':gpe_stim, 'snc':snc_stim}, save_data='/data/people/evjang/pyN_data/', properties_to_save=['psc','spike_raster','I_rec'],stdp=True)

save_data(results2,'./')
