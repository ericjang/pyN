#!/usr/bin/env python

'''
Recurrent network of Adaptive-Exponential Integrate-and-Fire neurons

Author: Eric Jang
'''

import numpy as np
import pylab as py
import ipdb as pdb
from datetime import datetime
import pickle

class Population():
  def __init__(self, name, N=10, synapses=None, mode="Excitatory", cm=0.281, tau_psc=-5.0, tau_refrac=0.1, v_spike=-40.0, v_reset=-70.6, v_rest=-70.6, tau_m=9.3667, i_offset=0.0, a=4.0, b=0.0805, delta_T=2.0,tau_w=144.0,v_thresh=-50.4,e_rev_E=0.0, tau_syn_E=5.0, e_rev_I=-80.0, tau_syn_I=5.0, connectivity=None):
    '''
    static network of AdEx Neurons. Performs no
    '''
    self.name = name
    self.N         = N           # Number of neurons in population
    # other variables (traces) can be conveniently set up during simulation...
    self.receiver = [] #stored list of synapse weight matrices from other populations
    '''
    configure neuron parameters
    '''
    self.mode       = mode       # EPSP or IPSP
    self.cm         = cm         # Capacitance of the membrane in nF
    self.tau_refrac = tau_refrac # Duration of refractory period in ms.
    self.v_spike    = v_spike    # Spike detection threshold in mV.
    self.v_reset    = v_reset    # Reset value for V_m after a spike. In mV.
    self.v_rest     = v_rest     # Resting membrane potential (Leak reversal potential) in mV.
    self.tau_m      = tau_m      # Membrane time constant in ms
    self.i_offset   = i_offset   # Offset current in nA
    self.a          = a          # Subthreshold adaptation conductance in nS.
    self.b          = b          # Spike-triggered adaptation in nA
    self.delta_T    = delta_T    # Slope factor in mV
    self.tau_w      = tau_w      # Adaptation time constant in ms
    self.tau_psc    = tau_psc    # post synaptic current filter time constant
    self.v_thresh   = v_thresh   # Spike initiation threshold in mV
    self.e_rev_E    = e_rev_E    # Excitatory reversal potential in mV.
    self.tau_syn_E  = tau_syn_E  # Decay time constant of excitatory synaptic conductance in ms.
    self.e_rev_I    = e_rev_I    # Inhibitory reversal potential in mV.
    self.tau_syn_I  = tau_syn_I  # Decay time constant of the inhibitory synaptic conductance in ms.
    '''
    state variables for each population
    The system is memoryless so there is no need to recall more than one previous value
    '''
    self.I_inj = None#no injection current yet
    self.v = np.ones(N) * v_rest
    self.ge = np.ones(N)
    self.gi = np.ones(N)
    self.w = np.ones(N)
    self.prev_spiked = (np.zeros(N) == 1) #boolean array
    self.last_spike = np.zeros(N)
    '''
    configure synapses
    '''
    if (synapses == None and connectivity == None):
      print 'generating empty connectivity'
      self.synapses = generate_synapses(N,N,connectivity="none")
    elif connectivity != None:
      print 'generating connectivity = ', connectivity
      #connectivity is when you want to pass a high-level string that automatically generates the synapses.
      self.synapses = generate_synapses(N,N,connectivity=connectivity)
    elif (N == synapses.shape[0] == synapses.shape[1]):
      print 'using user-defined synapses'
      #if user created their own synapses, then check to make sure it is ok
      self.synapses = synapses
    else:
      raise Exception("Synapse matrix wrong dimensions!")
  #configure EPSP or IPSPs
  def Isyn(self,t):
    '''
    Excitatory or Inhibitory postsynaptic current model
    - t is an array of every neuron's last spike time
    - returns current beginning at that last spike time
    - e.g. if a neuron fires at time 1 but not at time 2, the decaying current from time 1 will still be applied
    '''
    t[np.nonzero(t < 0)] = 0
    I = t*np.exp(-t/self.tau_psc)
    if self.mode == "Excitatory": return I
    elif self.mode == "Inhibitory": return -I

def generate_synapses(pre_population, post_population, connectivity="sparse-random"):
  '''
  returns synapse matrix
  pre_population and post_population can either be a Population object OR dimensions (int) of population objects
  '''
  if type(pre_population) == int:
    M = pre_population
  else:
    M = pre_population.N
  if type(post_population) == int:
    N = post_population
  else:
    N = post_population.N

  if connectivity == "none":
    #empty recurrent weights
    synapses = np.zeros([M,N])
  elif connectivity == "full-random":
    #shortcut for setting up full connectivity with random weights
    synapses = np.random.random([M,N])
  elif connectivity == "sparse-random":
    #shortcut for setting up sparse connectivity with random weights
    #TODO : need to adjust scaling of sparsity - exponential distribution? logarithms?
    synapses = np.random.random([M,N])
    syn_filter = (synapses < float(5)/N)
    synapses *= syn_filter
  else:
    raise Exception("connectivity type not recognized! Check your spelling...")
  #we don't want neurons to recurrently excite themselves! so we set them to zero
  np.fill_diagonal(synapses,0)
  return synapses

class Network():
    def __init__(self, populations):
      #adds population to network or connects populations together
      #this allows us to join populations with different AdEx properties
      #populations = array of population objects
      self.populations = {}
      for p in populations:
        self.populations[p.name] = p#so we can access by reference to name

    def connect(self, pre, post, synapses):
      '''
      connect to populations together in a network
      pre - presynaptic group
      post - postsynaptic group
      synapses - single directional synapse connections from pre to post.

      Let us see for now what happens when one region drives another without getting feedback...
      '''
      self.populations[post].receiver.append({'from':pre,'syn':synapses})
      return True

    def simulate(self, T=50,dt=0.125,I_inj=None,spike_delta=100,saveData=True,plotData=True):
        '''
        simulate a single population or group of connected populations
        unlike the Neurdon reccurrent.py example, this does not store the entire spike raster and state variables in memory.

        I_inj = dictionary containing driving currents for each population.
        example:
        I = zeros(len(time))
        for i, t in enumerate(time):
          if 5 <= t <= 30: I[i] = 10 # uA/cm2
          elif 35 <= t <= 40: I[i] = 10
        I_inj = {'thalamus':I}
        '''
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.T = T
        self.dt = dt
        self.spike_delta = spike_delta
        time_trace = np.arange(0,T+dt,dt)#time array

        #set up the injected current for each population.
        for name, p in self.populations.items():
          p.I_inj = np.zeros((p.N,len(time_trace)))

        for name, inj in I_inj.items():
          #I_inj is a dictionary containing stim objects for each population
          #stim is an array of dictionaries containing start, stop, and mV vals -
          #[{'start':10,'stop':20,'mV':10},{'start':30,'stop':40,'mV':20}]
          #stimulus is only applied to the first neuron.
          self.populations[name].I_inj = np.zeros((self.populations[name].N,len(time_trace)))
          for stim in inj:
            #individual stimulus events
            for i, t in enumerate(time_trace):
              if stim['start'] <= t <= stim['stop']:
                self.populations[name].I_inj[0,i] += stim['mV'] #inputs allowed to accumulate if badly entered by users

        if saveData:
          '''
          params need to be re-shaped later
          params = {
            T : ,
            dt : ,
            spike_delta: ,

            populations : {
              'cortex' : N <-- probably should save other population parameters here too
              'thalamus' : M
            }
            weights : { <---TODO : track the weight matrices & projections (save data to file and plot)
              {
                pre: cortex
                post: cortex

              }
            }
          }

          '''
          #parameters (later serialized to object)
          params = {
            'time_stamp' : now,
            'T' : self.T,
            'dt' : self.dt,
            'spike_delta' : self.spike_delta,
            'populations' : {},
            'weights' : {}
          }

          #data files to write to
          v_dataFiles = {}
          ge_dataFiles = {}
          gi_dataFiles = {}
          w_dataFiles = {}


          params_file = open('../data/' + now + '-' + 'experiment.pkl','w')
          for name, p in self.populations.items():
            params['populations'][name] = p.N
            #write I_inj to file right away (provided that stim exists)
            with file('../data/' + now + '-' + name + '-' + 'stim' + '.txt', 'w') as outputfile:
              np.savetxt(outputfile, p.I_inj)
            #prep other files
            v_dataFiles[name]  = '../data/' + now + '-' + name + '-' + 'v'  + '.txt'
            ge_dataFiles[name] = '../data/' + now + '-' + name + '-' + 'ge' + '.txt'
            gi_dataFiles[name] = '../data/' + now + '-' + name + '-' + 'gi' + '.txt'
            w_dataFiles[name]  = '../data/' + now + '-' + name + '-' + 'w'  + '.txt'

        pickle.dump(params, params_file)
        params_file.close()
        #run the simulation
        for i, t in enumerate(time_trace[1:],1):
          print("%0.3f%% done..." % (float(i)/len(time_trace)))#make sure to run this in python3
          #compute change in state variables for each population
          for name, p in self.populations.items():
            #if prev_spiked for a neuron, then it becomes v_reset
            p.v[np.nonzero(p.prev_spiked == True)] = p.v_reset
            #compute current input from neurons within population as well as neurons from other populations
            p.I_proj = p.synapses.dot(p.Isyn(t - p.last_spike)) #intra-population currents

            print '###############', i
            print p.I_proj
            #add currents from other populations that project to p (interpopulation)
            for proj in p.receiver:
              proj_last_spike = self.populations[proj['from']].last_spike
              p.I_proj += self.populations[proj['from']].Isyn(t-proj_last_spike).dot(proj['syn'])#unlike the neurdon example, I am using transposed version of connectivity matrix
            #compute deltas
            dv  = (((p.v_rest-p.v) + p.delta_T*np.exp((p.v - p.v_thresh)/p.delta_T))/p.tau_m + (p.ge*(p.e_rev_E-p.v) + p.gi*(p.e_rev_I-p.v) + p.i_offset + p.I_inj[:,i] + p.I_proj - p.w)/p.cm) *dt
            dge = -p.ge/p.tau_syn_E * dt
            dgi = -p.gi/p.tau_syn_I * dt
            dw  = (p.a*(p.v-p.v_rest) - p.w)/p.tau_w * dt

            p.v += dv
            p.ge += dge
            p.gi += dgi
            p.w += dw

            #detect spike thresholds
            spiked = np.nonzero(p.v >= p.v_thresh)
            no_spike = np.nonzero(p.v < p.v_thresh)
            p.v[spiked] += spike_delta
            p.w[spiked] += p.b #adjust adaptation weight
            p.last_spike[spiked] = t #spiked now!
            p.prev_spiked[spiked] = True
            p.prev_spiked[no_spike] = False

          #save the data
          if (saveData):
            for name,p in self.populations.items():
              vfile = open(v_dataFiles[name], 'a')
              gefile = open(ge_dataFiles[name], 'a')
              gifile = open(gi_dataFiles[name], 'a')
              wfile = open(w_dataFiles[name], 'a')
              vfile.write('# New slice\n')
              gefile.write('# New slice\n')
              gifile.write('# New slice\n')
              wfile.write('# New slice\n')
              np.savetxt(vfile,p.v,fmt='%-7.4f')
              np.savetxt(gefile,p.ge,fmt='%-7.4f')
              np.savetxt(gifile,p.gi,fmt='%-7.4f')
              np.savetxt(wfile,p.w,fmt='%-7.4f')
              #close the files!
              vfile.close()
              gefile.close()
              gifile.close()
              wfile.close()
        #simulation done.
        #can only plot data if saveData is true - simulation only stores previous and current state variables.
        if (saveData):
          return params#can be called by load_data
        else:
          return True

def load_data(params):
  #given a string timestamp (embedded in a parmas object), re-load into memory and plot.
  if type(params) == str:#we can pass in just the timestamp if we like and the params will automatically -> time_stamp
    time_stamp = params
  else:
    time_stamp = params['time_stamp']
  params_file = open('../data/' + time_stamp + '-' + 'experiment.pkl','r')
  params = pickle.load(params_file)

  #rebuild the time trace (for x axis plotting)
  time_trace = np.arange(0,params['T']+params['dt'],params['dt'])

  #display the trace for each population
  i = 0
  for name, N in params['populations'].items():
    v_trace  = np.loadtxt('../data/' + time_stamp + '-' + name + '-' + 'v'  + '.txt').reshape((-1,N))
    ge_trace = np.loadtxt('../data/' + time_stamp + '-' + name + '-' + 'ge' + '.txt').reshape((-1,N))
    gi_trace = np.loadtxt('../data/' + time_stamp + '-' + name + '-' + 'gi' + '.txt').reshape((-1,N))
    w_trace  = np.loadtxt('../data/' + time_stamp + '-' + name + '-' + 'w'  + '.txt').reshape((-1,N))

    #a figure + 4 subplots for each trace
    f, axarr = py.subplots(4)
    axarr[0].plot(time_trace[1:],v_trace)
    axarr[1].plot(time_trace[1:],ge_trace)
    axarr[2].plot(time_trace[1:],gi_trace)
    axarr[3].plot(time_trace[1:],w_trace)

    axarr[0].set_title('membrane potential (mV)')
    axarr[1].set_title('ge')
    axarr[2].set_title('gi')
    axarr[3].set_title('adaptation variable w')

    py.show()
    # py.plot(time_trace[1:], v_trace)
    #     py.title(name + ' membrane potential')
    #     py.ylabel('membrane potential (mV)')
    #     py.xlabel('Time (msec)')
    #     py.show()
    #
    #     py.plot(time_trace[1:], w_trace)
    #     py.title(name + ' adaptation variable (w)')
    #     py.ylabel('adaptation variable')

def demo():
    cortex = Population(N=100,name='cortex',connectivity="sparse-random")
    thalamus = Population(N=50,name='thalamus',connectivity="sparse-random")
    #connectivity is represented by a N by M matrix where N is #neurons in pre-synaptic
    #population and M is #neurons in post-synaptic population (columns)
    fibers = generate_synapses(thalamus, cortex, connectivity="sparse-random")
    brain = Network(populations=[thalamus, cortex])
    brain.connect('thalamus','cortex',fibers)#do NOT call connect more than once!
    #make up some input and feed it to the thalamus
    stim = [{'start':10,'stop':20,'mV':10},{'start':30,'stop':40,'mV':20}]
    results = brain.simulate(T=100,dt=0.25,I_inj={'thalamus':stim})#simulate for 50 msec, stimulating the thalamus
    load_data(results)

def small_net():
  group = Population(N=10,name='bob',connectivity="sparse-random")
  pdb.set_trace()
  brain = Network(populations=[group])
  stim = [{'start':10,'stop':100,'mV':10},{'start':30,'stop':40,'mV':20}]
  results = brain.simulate(T=10,dt=0.125,I_inj={'bob':stim})#simulate for 50 msec, stimulating the thalamus
  load_data(results)

if __name__ == "__main__":
    #if we are running this script by itself (as opposed to inheriting, set up an example network)
    small_net()
