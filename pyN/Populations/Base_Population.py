'''
Base Population class.
This class does nothing by default (will not work with simulator). Must be subclassed.
'''
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN.synapse import *
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
    if (synapses == None and connectivity == None): (synapses,delays) = generate_synapses(N,N,connectivity="none")
    elif connectivity != None: (synapses,delays) = generate_synapses(N,N,connectivity=connectivity,delay=0.25,std=0.05)
    elif (N == synapses.shape[0] == synapses.shape[1]): synapses = synapses
    else: raise Exception("Synapse matrix wrong dimensions!")

    #feed the population into its own receiver
    if connectivity is not None:
      self.receiver.append({'from':self.name,'syn':synapses,'delay':delays,'delay_indices':None})

  def initialize(self, T, len_time_trace, integration_time, save_data, now, properties_to_save, dt, stdp_t_window=50):
    #extra static parameters & state variables added when simulation starts
    '''
    stdp_t_window = how many msec to look backwards/forwards. Cannot be infinite value otherwise LDP will never take place
    '''
    self.T = T
    self.spike_raster = np.zeros((self.N, len_time_trace))
    self.psc = np.zeros((self.N, len_time_trace))
    self.integrate_window = np.int(np.ceil(integration_time/dt))
    self.dt = dt
    #convert every delay in its receiver (including itself) into a delay_indices matrix
    for connection in self.receiver:
      connection['delay_indices'] = np.int16(connection['delay']/dt)#convert millisecond delays to number of indices to look back when retrieving appropriate current

    if self.integrate_window > len_time_trace:
      self.integrate_window = len_time_trace #if we are running a short simulation then integrate window will overflow available time slots!
    self.i_to_dt_psc = np.array([j*dt for j in reversed(range(1,self.integrate_window + 1))])
    if save_data:
      self.init_save(now, save_data, properties_to_save)
    #convet stdp_window into number of time steps
    #we could use one i_to_dt function but it is computationally faster to simply cache these calculations.
    self.stdp_window = np.int(stdp_t_window / dt)
    self.i_to_dt_stdp = np.array([j*dt for j in reversed(range(1,self.stdp_window + 1))])

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

  def update_currents(self, all_populations, I_ext, i, t, dt):
    #reset I_ext (previously I was forgetting to do this and the whole thing was going nuts)
    self.I_ext = np.zeros(self.I_ext.shape[0])
    self.I_rec = np.zeros(self.I_rec.shape)
    #update I_ext vector for current time step
    for name, inj in I_ext.items():
      if name == self.name:
        for stim in inj:
          if stim['start'] <= t <= stim['stop']:
            #drive only neurons specified in stim['neurons']
            current = np.zeros(self.N)
            current[stim['neurons']] = stim['mV']
            self.I_ext += current

    #update I_rec vector (includes own recurrent connections)
    for recv in self.receiver:
      '''
      this looks like a bit of black magic but what we are doing here is starting out with a few of presyn's recent current values for each of its neurons.
      we subtract time delays, convert it to a index value, then get current perceived by postsynaptic population at time t.
      This is an expensive process, but better than a compartamental model and the easiest method I can think of.
      Future TODO: don't store entire current trace, just a sliding window of currents you MIGHT need to access at time t based on the longest delay time in network'

      note that presyn.psc[]

      '''
      presyn = all_populations[recv['from']]
      #delayed_current_indices = i - self.delay_indices
      delayed_current_indices = i - recv['delay_indices']
      received_currents = presyn.psc[xrange(delayed_current_indices.shape[1]),delayed_current_indices]
      self.I_rec += np.sum(recv['syn'] * received_currents, axis=1)#we only care about the diagonals

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
      #the first time update_state is run, initialize a self.i_to_dt_psc vector that converts columns of spike raster into t_diff = times since last spike
      self.integrate_window = i - np.floor(30/dt)
      self.i_to_dt_psc = np.array([i*dt for i in reversed(range(1,window))])

    t_diff = self.spike_raster[self.integrate_window:] * (self.integrate_window * self.i_to_dt).T
    self.psc[:,i] = t_diff * np.exp(-t_diff/self.tau_psc)
    '''

    return True

  def update_psc(self,i):
    #default current convolution technique
    #update self.psc
    #if window is too big for current i or entire simulation, adjust i_to_dt.T accordingly
    window = self.integrate_window if i > self.integrate_window else i
    i_to_dt = self.i_to_dt_psc if i > self.integrate_window else np.array([j*self.dt for j in reversed(range(1,window + 1))])
    #for any row (populations), get the -window previous entries all the way to the current one + 1 (for inclusivity)
    t_diff = self.spike_raster[:,i-window+1:i+1] * i_to_dt
    self.psc[:,i] = np.sum(t_diff * np.exp(-t_diff/self.tau_psc), axis=1)

  def update_synapses(self, all_populations, i, w_min=0, w_max=0):
    '''
    calls synaptic plasticity function to compute changes in synaptic weights (spike pairing rule), and then scales
    according to the number of repeats.

    in order for there to be balanced increasing/decreasing of weights, the time step actually being updated is not AT the current one, but halfway between 2*stdp_window

    <---stdp_window (backwards)---> i - stdp_window <---- stdp_window ("forwards") (includes i)---->

    this should be arbitrary for any two populations

    '''
    #FIXME
    window = self.stdp_window if i > 2*self.stdp_window else np.int(np.floor((i-1)/2))#no stdp weight modification takes place until a certain amount of time has passed
    i_to_dt = self.i_to_dt_stdp if i > 2*self.stdp_window else np.array([j*self.dt for j in reversed(range(1,window + 1))])
    self_spiked = np.nonzero(self.spike_raster[:,i-window])

    #step one, increase all weights of presyn->self
    for recv in self.receiver:
      #spiked,spiked_before,spiked_after are indices to which neurons spiked.
      #I am assuming that window and spike_raster for all populations line up (time-wise)
      if i >= 99:pdb.set_trace()
      presyn = all_populations[recv['from']]
      before = presyn.spike_raster[:,i - 2*window -1: i - window -1]
      presyn_spiked_before = np.nonzero(np.sum(before,axis=1))
      time_diff_before = before[presyn_spiked_before][:] * i_to_dt#only fetch time_diff_before if the neuron fired
      #print time_diff_before.shape
      #compute synapse increase vectors
      w_plus = np.nonzero(np.sum(stdp(time_diff_before, mode="LTP"),axis=1))
      #apply the synapse changes
      print w_plus
      recv['syn'][np.ix_(*(presyn_spiked_before + self_spiked))] += w_plus
      #alternative way to get the view, join the  [rsum<165][:,csum>80], but it is not a view.
      recv['syn'][recv['syn'] > w_max] = w_max

    #step 2, decrease all weights of postsyn->self
    for name, postsyn in all_populations.items():
      for recv in postsyn.receiver:
        if recv['from'] == self.name:
          #self feeds into this population! decrease weights
          after = postsyn.spike_raster[:,i-window:i]
          postsyn_spiked_after = np.nonzero(np.sum(after,axis=1))
          #make sure to reverse the i_to_dt vector and make these ones negative
          time_diff_after = after * -i_to_dt[::-1]
          w_minus = np.nonzero(np.sum(stdp(time_diff_after, mode="LTD"),axis=1))
          recv['syn'][np.ix_(*(self_spiked + postsyn_spiked_after))] += w_minus
          recv['syn'][recv['syn'] > w_min] = w_min

  def init_save(self, now, save_data, properties_to_save):
    #properties to save
    self.files = []
    for prop in properties_to_save:
      self.files.append({'property':prop,'file':open(save_data + now + '-' + self.name + '-' + prop, 'a')})

  def save_data(self,i):
    for file in self.files:
      prop = file['property']
      if (prop in ['v','u','w','I_ext','I_syn']):
        vector = getattr(self, prop)
      elif (prop in ['psc','spike_raster']):
        vector = getattr(self,prop)[:,i]
      np.savetxt(file['file'], vector, fmt='%-7.4f')


  def close(self):
    #close files.
    for file in self.files: file['file'].close()