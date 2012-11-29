'''
The objective of this network is to accumulate a number in the positive direction.

The populations begin in the "Go" state.

Most populations either only excite or inhibit other populations. That is conveninient for population-based inhibition but in the future
I should implement synapse-based inhibition.

Testing a couple things :

- dopamine stimulation built into this network
- disconnects populations -> "dis-inhibiting" action
- all-or-nothing stdp (only operates after 50 times)

'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from pyN import *

#substantia nigra releases dopamine. Stimulate this when good things happen. This one is special. because it is excitatory towards Go and inhibitory towards NoGo.

SNc      = IzhikevichPopulation(name='Substantia Nigra Complex',N=20, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
Go_add   = IzhikevichPopulation(name='Go+', N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
Go_sub   = IzhikevichPopulation(name='Go-', N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
NoGo_add = IzhikevichPopulation(name='NoGo+',N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
NoGo_sub = IzhikevichPopulation(name='NoGo-',N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
GPi      = IzhikevichPopulation(name='Globus Pallidus-Internal Segment',N=20, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
GPe      = IzhikevichPopulation(name='Globus Pallidus-External Segment',N=20, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
thal     = IzhikevichPopulation(name='Thalamus',N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)
PFC      = IzhikevichPopulation(name='Prefrontal Cortex', N=100, connectivity="sparse-random", a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)


brain = DopaNetwork(populations=[SNc, Go_add, NoGo_add, Go_sub, NoGo_sub, GPi, GPe, thal, PFC])
#set up the excitatory connections between the populations

#SNc -> excitatory to Go+/- and inhibitory to NoGo +/-
brain.connect(pre='Substantia Nigra Complex', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Substantia Nigra Complex', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Substantia Nigra Complex', post='NoGo+', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)
brain.connect(pre='Substantia Nigra Complex', post='NoGo-', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

#frontal cortex -> excitatory connections to all the go populations
brain.connect(pre='Prefrontal Cortex', post='Go+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Prefrontal Cortex', post='NoGo+', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Prefrontal Cortex', post='Go-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Prefrontal Cortex', post='NoGo-', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#Go inhibits GPi
brain.connect(pre='Go+',post='Globus Pallidus-Internal Segment', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='Go-',post='Globus Pallidus-Internal Segment', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

#NoGo inhibits Gpe (disinhibited)
brain.connect(pre='NoGo+',post='Globus Pallidus-External Segment', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
brain.connect(pre='NoGo-',post='Globus Pallidus-External Segment', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)

brain.disconnect(pre='NoGo+',post='Globus Pallidus-External Segment')
brain.disconnect(pre='NoGo-',post='Globus Pallidus-External Segment')

#GPe inhibits GPi
brain.connect(pre='Globus Pallidus-External Segment', post='Globus Pallidus-Internal Segment', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#GPi inhibits Thalamus (disinhibited)
brain.connect(pre='Globus Pallidus-Internal Segment', post='Thalamus', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.disconnect(pre='Globus Pallidus-Internal Segment', post='Thalamus')

#thalamus bidirectional activity to PFC
brain.connect(pre='Prefrontal Cortex', post='Thalamus', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
brain.connect(pre='Thalamus', post='Prefrontal Cortex', synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)

#####
#run the network for 10 seconds
#####
simTime = 10000

#Suppose SNc constantly generating Dopamine and synapse connect to simulate 'bursting'
snc_stim = [{'start':0,'stop':simTime,'mV':14,'neurons':[i for i in range(5)]}]
#GPe is tonically active
gpe_stim = [{'start':0,'stop':simTime,'mV':14,'neurons':[i for i in range(5)]}]
#thalamus also receives sensory input -> in the future transition to environmental input
thal_stim = [{'start':0,'stop':100,'mV':14,'neurons':[i for i in range(5)]}]

results = brain.simulate(experiment_name='Dopaminergic STDP Reinforcement Learning',T=simTime, dt=0.25, I_ext={'Thalamus':thal_stim,'Globus Pallidus-External Segment':gpe_stim, 'Substantia Nigra Complex':snc_stim}, save_data='../data/', properties_to_save=['psc','spike_raster','I_ext','I_rec'],stdp=True)

save_data(results,'./')#save the plots -> analyze the plots separately.