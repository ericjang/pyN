pyN(euron)
===

pyN (pronounced 'pine') is a python module for simulating spiking neural networks.

![Alt text](https://raw.github.com/ericjang/pyN/master/images/spike_freq_adapt_net.png)

#Features:

- Simulate single spiking neurons of various types and complexities (Izhikevich, AdEx, Hodgkin Huxley)
- Simulate a network of aforementioned neurons.
- Uses Matplotlib for visualization of results
- Lightweight : uses as little memory and as much vectorizing as possible to boost performance.

#Tutorial

##Getting Started - Single Neuron simulation:

###1. Create some populations.
A Population is a group of neurons with the same properties.

```python
from pyN import *
one_neurons = IzhikevichPopulation(name='Charly the Neuron', N=1)
```

###2. Create a Network and put the Population inside it.
The populations parameter takes an array of Populations. You can also create an empty Network and add Populations manually, if you like.

```python
brain = Network(populations=[one_neurons])
```
###[Optional]: Create some stimuli

In order for the neuron to do anything interesting, we need to present it with some externally "injected" current. This is defined by specifying a dictionary of the time interval for a certain voltage to be applied, and which neurons to apply it to. Voltages can stack on top of each other.

```python
stim = [{'start':10,'stop':100,'mV':14,'neurons':[0]}]
```

###3. Run the Network

```python
results = brain.simulate(experiment_name='Single Neuron exhibiting tonic spiking',T=100,dt=0.25,integration_time=30,I_ext={'Charly the Neuron':stim}, save_data='../data/', properties_to_save=['v','u','psc','I_ext'])
```

###4. Look at data. Profit.

```python
show_data(results)
```

![Alt text](https://raw.github.com/ericjang/pyN/master/images/single_tonic_spiking.png)

##Recurrent Networks

- If you create a Population with more than one neuron in it, pyN by default recurrently connects the neurons.
- Note that in the absense of Hebbian Learning / Spike Adaptation, large networks will exhibit over-saturation of spiking behavior. If the entire network becomes active, it will become unrealistically "epileptic".


##Connecting Populations
The brain is composed of many different types of neural populations with different properties.

###Construct two separate populations with different neural properties:

```python
A = IzhikevichPopulation(name='thalamus', N=100, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None)#tonic spiking
B = IzhikevichPopulation(name='cortex', N=50, a=0.02, b=0.25, c=-55, d=0.05, v0=-70, u0=None)#phasic bursting
```

###Add Populations to Network and then connect them

```python
brain = Network(populations=[A,B])
brain.connect(pre='thalamus', post='cortex')
brain.connect(pre='cortex', post='thalamus',delay=2.25,std=0.25)#corticothalamic loop longer than thalamocortical loop
```

###Create stimuli and run the network.

```python
stim = [{'start':10,'stop':200,'mV':20,'neurons':[0]},{'start':50,'stop':300,'mV':30,'neurons':[i for i in range(3)]}]
results = brain.simulate(experiment_name='Reentrant Thalamocortical Circuit',T=600,dt=0.25, integration_time=30, I_ext={'thalamus':stim}, save_data='../data/', properties_to_save=['v','u','psc','I_ext'])
show_data(results)
```

Note that if we wanted to stimulate the cortex as well, we merely pass in an additional attribute into the I_ext dictionary.

```python
I_ext = {'thalamus':stim,'cortex':another_stim}
```

###Result:

![Alt text](https://raw.github.com/ericjang/pyN/master/images/thalamocortical-driving.png)

#Performance:
  - Although pyN is biologically realistic and matrix calculations are vectorized, it is still dreadfully slow due to numerical integration techniques used when convolving spike deltas with exponential decay currents.
  - It takes ~10 minutes to simulate a single second of activity over 1000 Izhikevich neurons (recurrently connected to each other).

#Other Notes:
  - Do NOT create a Population with the same name as another Population or it will be overwritten when adding it to a Network.
