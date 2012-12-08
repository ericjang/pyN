'''
izhikevich verison of #14

'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from pyN import *

#substantia nigra releases dopamine. Stimulate this when good things happen. This one is special. because it is excitatory towards Go and inhibitory towards NoGo.
#tonic bursting parameters
SNc      = IzhikevichPopulation(name='snc',N=30,a=0.02,b=0.25,c=-50,d=2,v0=-70, connectivity="full-random")

Go_add   = IzhikevichPopulation(name='Go+', N=20, connectivity="full-random")
Go_sub   = IzhikevichPopulation(name='Go-', N=20, connectivity="full-random")
NoGo_add = IzhikevichPopulation(name='NoGo+',N=20, connectivity="full-random")
NoGo_sub = IzhikevichPopulation(name='NoGo-',N=20, connectivity="full-random")

#these inhibitory populations act to balance out activity and prevent go/nogo from going nuts when (not) driven by dopamine.
#Go_inhib = IzhikevichPopulation(name='go_inhib',N=8,connectivity="full-random")
#NoGo_inhib = IzhikevichPopulation(name='nogo_inhib',N=8,connectivity="full-random")

GPi_add  = IzhikevichPopulation(name='gpi+',N=10, connectivity="full-random")
GPi_sub  = IzhikevichPopulation(name='gpi-',N=10, connectivity="full-random")
GPe_add  = IzhikevichPopulation(name='gpe+',N=10, connectivity="full-random")
GPe_sub  = IzhikevichPopulation(name='gpe-',N=10, connectivity="full-random")

thal_in = IzhikevichPopulation(name='thal_in',N=30,connectivity="full-random")#where sensory info goes in
thal_add = IzhikevichPopulation(name='thal+',N=20, connectivity="full-random")#where motor output comes out
thal_sub = IzhikevichPopulation(name='thal-',N=20, connectivity="full-random")

PFC_add  = IzhikevichPopulation(name='pfc+', N=85, connectivity="full-random")
PFC_sub  = IzhikevichPopulation(name='pfc-', N=85, connectivity="full-random")
'''
In order for stability to occur in cortex, each should also have 15 percent inhibitory neurons? Do the cortex for now.
If the other parts of brain also go nuts consider adding inhibitory neurons to those as well.
'''
PFC_inhib = IzhikevichPopulation(name='pfc_inhib',N=30,connectivity="full-random")
brain = DopaNetwork(populations=[SNc, Go_add, NoGo_add, Go_sub, NoGo_sub, GPi_add, GPe_add, GPi_sub, GPe_sub, thal_in, thal_add, thal_sub, PFC_add, PFC_sub, PFC_inhib])
#set up the excitatory connections between the populations

#SNc -> excitatory to Go+/- and inhibitory to NoGo +/-
brain.connect(pre='snc', post='Go+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='Go-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo+', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='snc', post='NoGo-', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)

#Go/NoGo Balanced by inhibitory population

'''s
brain.connect(pre='Go+', post='go_inhib', synapses="full-random", mode='excitatory')
brain.connect(pre='Go-', post='go_inhib', synapses="full-random", mode='excitatory')
brain.connect(pre='NoGo+', post='nogo_inhib', synapses="full-random", mode='excitatory')
brain.connect(pre='NoGo-', post='nogo_inhib', synapses="full-random", mode='excitatory')

brain.connect(pre='go_inhib', post='Go+', synapses="full-random", mode='inhibitory')
brain.connect(pre='go_inhib', post='Go-', synapses="full-random", mode='inhibitory')
brain.connect(pre='nogo_inhib', post='NoGo+', synapses="full-random", mode='inhibitory')
brain.connect(pre='nogo_inhib', post='NoGo-', synapses="full-random", mode='inhibitory')
'''
#frontal cortex -> excitatory connections to all the go populations
brain.connect(pre='pfc+', post='Go+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc+', post='NoGo+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='Go-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='NoGo-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)

#Go inhibits GPi
brain.connect(pre='Go+',post='gpi+', synapses='full-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='Go-',post='gpi-', synapses='full-random', mode='inhibitory', delay=2.25, std=0.25)

#ACTUALLY, we don't want Go populations to inhibit each other because that leads to one completely squashing out the other and having an 'unfair' advantage.

#Go populations inhibit each other (slightly)
#brain.connect(pre='Go+',post='Go-',synapses='full-random',mode='inhibitory')
#brain.connect(pre='Go-',post='Go+',synapses='full-random',mode='inhibitory')

#... and so do thalamic motor outputs...?
#brain.connect(pre='thal+',post='thal-',synapses='full-random',mode='inhibitory')
#brain.connect(pre='thal-',post='thal+',synapses='full-random',mode='inhibitory')


#NoGo inhibits Gpe (disinhibited)
brain.connect(pre='NoGo+',post='gpe+', synapses='full-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='NoGo-',post='gpe-', synapses='full-random', mode='inhibitory', delay=2.25, std=0.25)

brain.disconnect(pre='NoGo+',post='gpe+')
brain.disconnect(pre='NoGo-',post='gpe-')

#GPe inhibits GPi
brain.connect(pre='gpe+', post='gpi+', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='gpe-', post='gpi-', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)

#GPi inhibits Thalamus (disinhibited)
brain.connect(pre='gpi+', post='thal+', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='gpi-', post='thal-', synapses="full-random", mode='inhibitory', delay=2.25,std=0.25)
brain.disconnect(pre='gpi+', post='thal+')
brain.disconnect(pre='gpi-', post='thal-')

#thalamus bidirectional activity to PFC
brain.connect(pre='pfc+', post='thal+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='pfc-', post='thal-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)

brain.connect(pre='thal+', post='pfc+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal-', post='pfc-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)

brain.connect(pre='thal_in', post='pfc+', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='thal_in', post='pfc-', synapses="full-random", mode='excitatory', delay=2.25,std=0.25)

#PFC 15% inhibition
brain.connect(pre='pfc+', post='pfc_inhib', synapses="full-random", mode='excitatory')
brain.connect(pre='pfc-', post='pfc_inhib', synapses="full-random", mode='excitatory')
brain.connect(pre='pfc_inhib', post='pfc+', synapses="full-random", mode='inhibitory')
brain.connect(pre='pfc_inhib', post='pfc-', synapses="full-random", mode='inhibitory')

#####
#run the network for a goal of 10 seconds
#####

results1 = brain.simulate(experiment_name='seg-iz', T=100, dt=0.25, save_data='/data/people/evjang/pyN_data/', properties_to_save=['v','psc','spike_raster','I_rec'],stdp=True)
save_data(results1,'./')
#results2 = brain.simulate(experiment_name='modelock-nocrossinhib-longer', T=30000, dt=0.250, save_data='/data/people/evjang/pyN_data/', properties_to_save=['v','psc','spike_raster','I_rec'],stdp=True)
#save_data(results2,'./')
