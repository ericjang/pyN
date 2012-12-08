import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

from pyN.synapse import *
import numpy as np

import pdb
#import ipdb as pdb


class Base_Population():
  """
  Base Population Class
  This class does not work on its own. Most functions only work after self.initialize() has been called by the Netwrok containing the Population.
  """
  def __init__(self, name, N=10, tau_psc=5.0, connectivity=None, spike_delta=100, v_rest=-70, scale=1.0):
    """
    Constructor for base population.
    @param name str Name of Neuron Population. Must be unique
    @param N int Number of neurons in Population
    @ tau_psc float postsynaptic current filter time constant
    @param connectivity str|None string representing type of synaptic connection between populations
    @param spike_delta float Voltage increase during spike. Affects adaptation variable so be careful with this.
    @param v_rest float Resting membrane potential
    @param scale float Scaling factor for synapses
    """
    self.name = name
    self.N         = N           # Number of neurons in population
    self.receiver = [] #stored list of synapse weight matrices from other populations
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
    if (connectivity == None): (synapses,delays) = generate_synapses(N,N,connectivity="none")
    elif connectivity != None: (synapses,delays) = generate_synapses(N,N,connectivity=connectivity,delay=0.25,std=0.05,scale=scale)
    else: raise Exception("Synapse matrix wrong dimensions!")

    #feed the population into its own receiver
    if connectivity is not None:
      self.receiver.append({'from':self.name,'syn':synapses,'delay':delays,'delay_indices':None})

  def initialize(self, T, len_time_trace, integration_time, save_data, now, properties_to_save, dt, stdp_t_window=50):
    """
    Set up extra parameters and state variables during simulation. Called once and only once before running.
    @param T
    @param len_time_trace Dictates how long the spike raster array should be
    @param integration_time Integration time for psc
    @param save_data save path
    @param now Current time (for writing to files)
    @param properties_to_save array properties to save
    @param dt float Length of time step (needed for integration methods)
    @param stdp_t_window float How many msec to look backwards/forwards for STDP
    """
    self.T = T
    self.spike_raster = np.zeros((self.N, len_time_trace))
    self.psc = np.zeros((self.N, len_time_trace))
    self.integrate_window = np.int(np.ceil(integration_time/dt))
    self.dt = dt
    self.save_data = save_data
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
    """
    Excitatory or Inhibitory postsynaptic current model.
    @param postsyn postsynaptic matrix (can be self)
    @param t_diff array of every presynaptic neuron's (t-last spike time)

    however, we want to accomodate spike delays so...
    postsyn = postsynaptic matrix (can be self)
    - instead of returning a M x 1 column of currents, instead we make a matrix where every row is t - row of delay matrix
    - then (< 0) criterion will make any 'not ready yet' spike go to zero

    - in order to get the current delayed, we shift the exponential function to the right by the corresponding delay in self.delay
    - then do np.nonzero(t_diff - delay < 0) to clamp any t to 0.
    - this produces the delayed effect.

    Computational cost: we are computing N * more, where previously we used the same postsynaptic current for all receiving neurons.

    returns current applied to every POSTSYNAPTIC NEURON
    """

    t[np.nonzero(t < 0)] = 0
    #in order for a good modicum of current to even be applied, t must be negative!
    return t*np.exp(-t/self.tau_psc)

  def update_currents(self, all_populations, I_ext, i, t, dt):
    #I_ext is reset at the very end of the update_state
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
      """
      this looks like a bit of black magic but what we are doing here is starting out with a few of presyn's recent current values for each of its neurons.
      we subtract time delays, convert it to a index value, then get current perceived by postsynaptic population at time t.
      This is an expensive process, but better than a compartamental model and the easiest method I can think of.
      Future TODO: don't store entire current trace, just a sliding window of currents you MIGHT need to access at time t based on the longest delay time in network'

      """
      presyn = all_populations[recv['from']]
      #delayed_current_indices = i - self.delay_indices
      delayed_current_indices = i - recv['delay_indices']
      #range -> xrange in Python3.2?
      received_currents = presyn.psc[range(delayed_current_indices.shape[1]),delayed_current_indices]
      self.I_rec += np.sum(recv['syn'][:,:,0] * received_currents, axis=1)#we only care about the diagonals

  def update_state(self, i, T, t, dt):
    """
    Update state variables for all neurons in the population
    This function should be superclassed by AdEx, Izhikevich, etc.
    """
    return True

  def update_psc(self,i):
    """
    Default convolution technique for generating postsynaptic currents emanating from a population
    @params i int Simulation step number
    """
    #if window is too big for current i or entire simulation, adjust i_to_dt.T accordingly
    window = self.integrate_window if i > self.integrate_window else i
    i_to_dt = self.i_to_dt_psc if i > self.integrate_window else np.array([j*self.dt for j in reversed(range(1,window + 1))])
    #for any row (populations), get the -window previous entries all the way to the current one + 1 (for inclusivity)
    t_diff = self.spike_raster[:,i-window+1:i+1] * i_to_dt
    self.psc[:,i] = np.sum(t_diff * np.exp(-t_diff/self.tau_psc), axis=1)

  def update_synapses(self, all_populations, i, w_min=-.1, w_max=.1):
    """
    Update synaptic weights using STDP
    @param all_populations dict Network's population dictionary passed down to each population.
    @param i Simulation step number
    @param w_min Minimum synaptic weight
    @param w_max Maximum synaptic weight

    calls synaptic plasticity function to compute changes in synaptic weights (spike pairing rule), and then scales
    according to the number of repeats.

    in order for there to be balanced increasing/decreasing of weights, the time step actually being updated is not AT the current one, but halfway between 2*stdp_window

    <---stdp_window (backwards)---> i - stdp_window <---- stdp_window ("forwards") (includes i)---->

    this should be arbitrary for any two populations, whether they are the same one or not
    """
    window = self.stdp_window if i > 2*self.stdp_window else np.int(np.floor((i-1)/2))#no stdp weight modification takes place until a certain amount of time has passed
    i_to_dt = self.i_to_dt_stdp if i > 2*self.stdp_window else np.array([j*self.dt for j in reversed(range(1,window + 1))])
    self_spiked = (self.spike_raster[:,i-window-1] == 1)#np.nonzero is giving me a headache so i will use booleans


    #step one, increase all weights of presyn->self
    for recv in self.receiver:
      #spiked,spiked_before,spiked_after are indices to which neurons spiked.
      #I am assuming that window and spike_raster for all populations line up (time-wise)
      presyn = all_populations[recv['from']]
      before = presyn.spike_raster[:,i - 2*window -1: i - window -1]
      spike_count = np.sum(before,axis=1)#this needs to be added to each row
      pre_spiked = spike_count != 0.0#boolean array expressing which ones fired and which ones didnt
      #presyn_spiked_before = np.nonzero(np.sum(before,axis=1))
      time_diff_before = before * i_to_dt
      #compute synapse increase vectors
      #only filter out the positive counts, a.k.a. the ones that spiked
      recv['syn'][np.ix_(self_spiked,pre_spiked) + (1,)] += spike_count[np.ix_(pre_spiked)]/np.float(window)
      #reset counts for anything that has spiked more than 70 times! Avoids crazy oscillations
      count_reset = np.nonzero(recv['syn'][:,:,1] > 70)
      recv['syn'][count_reset[0],count_reset[1],1] = 0
      w_plus = np.sum(stdp(before, mode="LTP"),axis=1)#should be the same as applying sigmoid, then summing
      #apply the synapse changes
      #if pre_spiked and self_spiked: pdb.set_trace()
      recv['syn'][np.ix_(self_spiked,pre_spiked) + (0,) ] += repetition_sigmoid(recv['syn'][np.ix_(self_spiked,pre_spiked) + (1,)]) * w_plus[np.ix_(pre_spiked)]
      #increment the spike coincidence count in the third synapse dimension
      recv['syn'][(recv['syn'][:,:,0] > w_max),0] = w_max#advanced indexing
      if recv['from'] == self.name:
        np.fill_diagonal(recv['syn'][:,:,0],0)

    #generate post_spiked (self) so that decrease own weights from these to all other populations that spike at time i-window - 1
    after = self.spike_raster[:,i-window:i]
    self_spike_count = np.sum(after,axis=1)
    self_post_spiked = self_spike_count != 0.0
    time_diff_after = after * -i_to_dt[::-1]
    w_minus = np.sum(stdp(time_diff_after, mode="LTD"),axis=1)

    for name, postsyn in all_populations.items():
      for recv in postsyn.receiver:
        if recv['from'] == self.name:#self feeds into this target population!
          postsyn_spiked = postsyn.spike_raster[:,i-window-1] == 1
          recv['syn'][np.ix_(postsyn_spiked,self_post_spiked) + (1,)] += self_spike_count[np.ix_(self_post_spiked)][np.newaxis,:]/np.float(window)
          count_reset = np.nonzero(recv['syn'][:,:,1] > 70)
          recv['syn'][count_reset[0],count_reset[1],1] = 0
          #give unlearning a bit of an advantage over learning
          recv['syn'][np.ix_(postsyn_spiked,self_post_spiked) + (0,)] += repetition_sigmoid(recv['syn'][np.ix_(postsyn_spiked,self_post_spiked) + (1,)]) * w_minus[np.ix_(self_post_spiked)][np.newaxis,:] * 2.0
          recv['syn'][(recv['syn'][:,:,0] < w_min),0] = w_min #advanced indexing because synapses has 3 dimensions
          if name == self.name:
            np.fill_diagonal(recv['syn'][:,:,0],0)
    #for recv in self.receiver:
      #print str(recv['from']) + '-->' + self.name + '\t' + str(recv['syn'])

  def init_save(self, now, save_data, properties_to_save):
    """
    Set up files to write to
    """
    self.files = []
    for prop in properties_to_save:
      self.files.append({'property':prop,'file':open(save_data + now + '-' + self.name + '-' + prop, 'ab')})

  def write_files(self,i):
    """
    Append population states to files. Different populations produce different write behavior - for some variables we only want the last column, etc.
    """
    for file in self.files:
      prop = file['property']
      if (prop in ['v','u','w','I_ext','I_syn','I_rec']):
        vector = getattr(self, prop)
      elif (prop in ['psc','spike_raster']):
        vector = getattr(self,prop)[:,i]
      np.savetxt(file['file'], vector, fmt='%-7.4f')


  def close(self):
    """
    Close the files at the end of the simulation.
    """
    #close files
    if (self.save_data):
      for file in self.files: file['file'].close()
