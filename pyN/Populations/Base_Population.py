'''
Base Population class.
This class does nothing by default (will not work with simulator). Must be subclassed.
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN.synapse import generate_synapses
import numpy as np
import ipdb as pdb

class Base_Population():
  def __init__(self, name, N=10, synapses=None, mode="Excitatory", tau_psc=5.0, connectivity=None, spike_delta=100, v_rest=-70):
    '''
    non-changing variables
    '''
    self.name = name
    self.N         = N           # Number of neurons in population
    self.receiver = [] #stored list of synapse weight matrices from other populations
    self.mode       = mode       # Excitatory or Inhibitory currents generated
    self.tau_psc = tau_psc #postsynaptic current filter constant
    self.spike_delta = spike_delta
    self.T = None #needs to be set upon starting simulation.
    '''
    state variables for each population
    These variables are Markov Variables so there is no need to recall more than one previous value
    '''
    self.v = np.ones(N) * v_rest #voltage trace
    self.I_ext = np.zeros(N) #externally injected current
    self.I_rec = np.zeros(N) #current from recurrent connections + other populations
    '''
    non-memoryless state variables to be initiated upon Network.simualte:
    '''
    #self.psc = np.zeros((N,len(time))) #the post-synaptic current that the population emits. (will be delayed)
    #self.spike_raster = np.zeros((N,len(time))) * np.nan #for plotting spike raster

    '''
    configure synapses and delays
    '''
    if (synapses == None and connectivity == None): (self.synapses,self.delays) = generate_synapses(N,N,connectivity="none")
    elif connectivity != None: (self.synapses,self.delays) = generate_synapses(N,N,connectivity=connectivity,delay=0.25,std=0.25)
    elif (N == synapses.shape[0] == synapses.shape[1]): self.synapses = synapses
    else: raise Exception("Synapse matrix wrong dimensions!")

    #feed the population into its own receiver
    if connectivity is not None:
      self.receiver.append({'from':self.name,'syn':self.synapses, 'delay':self.delays})

  def initialize(self, len_time_trace, save_data, now, properties_to_save, dt):
    self.spike_raster = np.zeros((self.N, len_time_trace))
    self.psc = np.zeros((self.N, len_time_trace))
    self.integrate_window = np.int(np.ceil(30/dt))
    if self.integrate_window > len_time_trace:
      self.integrate_window = len_time_trace #if we are running a short simulation then integrate window will overflow available time slots!
    self.i_to_dt = np.array([i*dt for i in reversed(range(1,self.integrate_window + 1))])
    if save_data:
      self.init_save(now, save_data, properties_to_save)



  #configure EPSP or IPSPs
  def Isyn(self,postsyn,t_diff):
    '''
    Excitatory or Inhibitory postsynaptic current model.
    - t_diff is an array of every presynaptic neuron's (t - last spike time)
    when t_diff > 0, current starts getting applied.

    - e.g. if a neuron fires at time 1 but not at time 2, the decaying current from time 1 will still be applied

    however, we want to accomodate spike delays so...
    postsyn = postsynaptic matrix (can be self)
    - instead of returning a M x 1 column of currents, instead we make a matrix where every row is t - row of delay matrix
    - then (< 0) criterion will make any 'not ready yet' spike go to zero

    - in order to get the current delayed, we shift the exponential function to the right by the corresponding delay in self.delay
    - then do np.nonzero(t_diff - delay < 0) to clamp any t to 0.
    - this produces the delayed effect.

    Computational cost: we are computing N * more, where previously we used the same postsynaptic current for all receiving neurons.

    returns current applied to every POSTSYNAPTIC NEURON
    '''

    t[np.nonzero(t < 0)] = 0
    #in order for a good modicum of current to even be applied, t must be negative!
    if self.mode == "Excitatory": return t*np.exp(-t/self.tau_psc)
    elif self.mode == "Inhibitory": return -t*np.exp(-t/self.tau_psc)

  def update_currents(self, all_populations, I_ext, t):
    #reset I_ext (previously I was forgetting to do this and the whole thing was going nuts)
    self.I_ext = np.zeros(self.I_ext.shape[0])
    #update I_ext vector for current time step
    for name, inj in I_ext.items():
      if name == self.name:
        for stim in inj:
          if stim['start'] <= t <= stim['stop']:
            self.I_ext += stim['mV']

    #update I_rec vector (includes own recurrent connections)
    for proj in self.receiver:
      presyn = all_populations[proj['from']] #presynaptic population
      #because we are accounting for spike delays now, we cannot dot the entire matrix. matlab has bsxfun but we'll just do a loop
      '''
      this looks like a bit of black magic but what we are doing here is starting out with a few of presyn's recent current values for each of its neurons.
      we subtract time delays, convert it to a index value, then get current perceived by postsynaptic population at time t.
      This is an expensive process, but better than a compartamental model and the easiest method I can think of.
      Future TODO: don't store entire current trace, just a sliding window of currents you MIGHT need to access at time t based on the longest delay time in network'
      '''
      delay_indices = (t - self.delays)/self.T
      received_currents = presyn.psc[delay_indices, xrange(delay_indices.shape[1])]
      p.I_rec += np.sum(self.synapses * received_currents, axis=1)#we only care about the diagonals

  def update_state(self, i, T, t, dt):
    '''
    although we don't REALLY need them, it helps to know i and t
    - compute v and adaptation resets
    - Compute deltas and apply them to state variables.
    - Decide whether to spike or not, update spike raster
    - Update self.psc currents for time t by integrating any spikes that might have happened in last 30 msec (Isyn function).

    Example:

    #update self.psc
    if i==0:
      #the first time update_state is run, initialize a self.i_to_dt vector that converts columns of spike raster into t_diff = times since last spike
      self.integrate_window = i - np.floor(30/dt)
      self.i_to_dt = np.array([i*dt for i in reversed(range(1,window))])

    t_diff = self.spike_raster[self.integrate_window:] * (self.integrate_window * self.i_to_dt).T
    self.psc[:,i] = t_diff * np.exp(-t_diff/self.tau_psc)
    '''

    return True

    #update the neuron's own psc trace
  def init_save(self, now, save_data, properties_to_save):
    #properties to save
    self.files = []
    for prop in properties_to_save:
      self.files.append({'property':prop,'file':open(save_data + now + '-' + self.name + '-' + prop, 'a')})

  def save_data(self,i):
    for file in self.files:
      prop = file['property']
      if (prop in ['v','u','I_ext','I_syn']):
        np.savetxt(file['file'], getattr(self, prop), fmt='%-7.4f')
      elif (prop in ['psc']):
        np.savetxt(file['file'], getattr(self,prop)[:,i],fmt='%-7.4f')

  def close(self):
    #close files.
    for file in self.files: file['file'].close()