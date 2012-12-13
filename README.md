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
results = brain.simulate(experiment_name='Single Neuron exhibiting tonic spiking',T=100,dt=0.25,I_ext={'Charly the Neuron':stim}, save_data='../data/', properties_to_save=['v','u','psc','I_ext'])
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


##Spike-Timing-Dependent Plasticity

It has been proposed that STDP mechanisms act as a biologically plausible substrate to Hebbian Learning. STDP is active by default, but to disable it (for performance reasons, etc.), you can set the <code>stdp=False</code> flag when running the network:

```python
brain.simulate(stdp=False)
```

Note that it takes a fairly large number of repeated spike pairings for STDP weights to take effect.

#Izhikevich Model Parameters:

<table>
    <tr>
        <td>Type</td>
        <td>Example</td>
        <td>a</td>
        <td>b</td>
        <td>c</td>
        <td>d</td>
        <td>v0</td>
        <td>u0</td>
    </tr>
    <tr>
        <td>Tonic Spiking</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/tonic_spiking.png'></td>
        <td>0.02</td>
        <td>0.2</td>
        <td>-65</td>
        <td>6</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Phasic Spiking</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/phasic_spiking.png'></td>
        <td>0.02</td>
        <td>0.25</td>
        <td>-65</td>
        <td>6</td>
        <td>-64</td>
        <td>u0</td>
    </tr>
    <tr>
        <td>Tonic Bursting</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/tonic_bursting.png'></td>
        <td>0.02</td>
        <td>0.25</td>
        <td>-50</td>
        <td>2</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Phasic Bursting</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/phasic_bursting.png'></td>
        <td>0.02</td>
        <td>0.25</td>
        <td>-55</td>
        <td>0.05</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Mixed Mode</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/mixed_mode.png'></td>
        <td>0.02</td>
        <td>0.2</td>
        <td>-55</td>
        <td>6</td>
        <td>-60</td>
        <td></td>
    </tr>
    <tr>
        <td>Spike Frequency Adaptation</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/spike_freq_adapt.png'></td>
        <td>0.01</td>
        <td>0.2</td>
        <td>-65</td>
        <td>8</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Class 1 exc.</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/class1_exc.png'></td>
        <td>0.02</td>
        <td>-0.1</td>
        <td>-55</td>
        <td>6</td>
        <td>-60</td>
        <td></td>
    </tr>
    <tr>
        <td>Class 2 exc.</td>
        <td>!<img src='https://raw.github.com/ericjang/pyN/master/images/class2_exc.png'></td>
        <td>0.2</td>
        <td>0.26</td>
        <td>-65</td>
        <td>0</td>
        <td>-64</td>
        <td></td>
    </tr>
    <tr>
        <td>Spike Latency</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/spike_latency.png'></td>
        <td>0.02</td>
        <td>0.2</td>
        <td>-65</td>
        <td>6</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Subthresh. osc.</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/subthresh_osc.png'></td>
        <td>0.05</td>
        <td>0.26</td>
        <td>-60</td>
        <td>0</td>
        <td>-62</td>
        <td></td>
    </tr>
    <tr>
        <td>Resonator</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/resonator.png'></td>
        <td>0.1</td>
        <td>0.26</td>
        <td>-60</td>
        <td>-1</td>
        <td>-62</td>
        <td></td>
    </tr>
    <tr>
        <td>Integrator</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/integrator.png'></td>
        <td>0.02</td>
        <td>-0.1</td>
        <td>-55</td>
        <td>6</td>
        <td>-60</td>
        <td></td>
    </tr>
    <tr>
        <td>Rebound Spike</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/rebound_spike.png'></td>
        <td>0.03</td>
        <td>0.25</td>
        <td>-60</td>
        <td>4</td>
        <td>-64</td>
        <td></td>
    </tr>
    <tr>
        <td>Rebound Burst</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/rebound_burst.png'></td>
        <td>0.03</td>
        <td>0.25</td>
        <td>-52</td>
        <td>0</td>
        <td>-64</td>
        <td></td>
    </tr>
    <tr>
        <td>Thresh. variability</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/thresh_variability.png'></td>
        <td>0.03</td>
        <td>0.25</td>
        <td>-60</td>
        <td>4</td>
        <td>-64</td>
        <td></td>
    </tr>
    <tr>
        <td>Bistability</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/bistability.png'></td>
        <td>0.1</td>
        <td>0.26</td>
        <td>-60</td>
        <td>0</td>
        <td>-61</td>
        <td></td>
    </tr>
    <tr>
        <td>DAP</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/DAP.png'></td>
        <td>1</td>
        <td>0.2</td>
        <td>-60</td>
        <td>-21</td>
        <td>-70</td>
        <td></td>
    </tr>
    <tr>
        <td>Accomodation</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/accomodation.png'></td>
        <td>0.02</td>
        <td>1</td>
        <td>-55</td>
        <td>4</td>
        <td>-65</td>
        <td>-16</td>
    </tr>
    <tr>
        <td>Inhibition induced spiking</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/inhib_induced_spiking.png'></td>
        <td>0.02</td>
        <td>-1</td>
        <td>-60</td>
        <td>8</td>
        <td>-63.8</td>
        <td></td>
    </tr>
    <tr>
        <td>Inhibition induced bursting</td>
        <td><img src='https://raw.github.com/ericjang/pyN/master/images/inhib_induced_bursting.png'></td>
        <td>-0.026</td>
        <td>-1</td>
        <td>-45</td>
        <td>-</td>
        <td>-63.8</td>
        <td></td>
    </tr>
</table>

#Adaptive Exponential Integrate-and-Fire Parameters:


#Performance:
  - Although pyN is biologically realistic and matrix calculations are vectorized, it is still dreadfully slow due to numerical integration techniques used when convolving spike deltas with exponential decay currents.
  - It takes ~10 minutes to simulate a single second of activity over 1000 Izhikevich neurons (recurrently connected to each other).

#Other Notes:
  - Do NOT create a Population with the same name as another Population or it will be overwritten when adding it to a Network.

#License

pyN is licensed under BSD.
