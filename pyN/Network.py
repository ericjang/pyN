'''
Network class for running populations.
Should be agnostic for population type
'''
import numpy as np

from synapse import *
from datetime import datetime

import os, sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import networkx as nx
import pickle


#import ipdb as pdb

class Network():
    def __init__(self, populations=[]):
      """
      The constructor
      @params populations array Array of Population Instances to be added to the Network
      """
      self.populations = {}
      self.graph = nx.DiGraph()
      for p in populations:
        self.populations[p.name] = p
        self.graph.add_node(p.name,size=p.N)

    def connect(self, pre, post, synapses, mode="excitatory", delay_matrix=None, delay=0.25, std=0.05, scale=1.0):
      """
      Connect two populations together in a network
      @param pre str String pointing to Population in network.
      @param post str String pointing to Population in network.
      @synapses str|np.ndarray
      @delay_matrix np.ndarray
      @return Boolean
      """
      if type(pre) == str:
        pre = self.populations[pre]
      if type(post) == str:
        post = self.populations[post]

      if type(synapses) == str:
        (gen_synapses, gen_delay_matrix) = generate_synapses(pre_population=pre, post_population=post, connectivity=synapses,delay=delay,std=std, scale=scale)
        if mode == "excitatory":
          synapses = gen_synapses
        elif mode == "inhibitory":
          synapses = -1.0 * gen_synapses#since gen_synapses[:,:,0] is initially all zero we are still ok


      if delay_matrix == None: delay_matrix = gen_delay_matrix#use the one previously generated

      post.receiver.append({'from':pre.name,'syn':synapses, 'mode':mode,'delay':delay_matrix, 'delay_indices':None, 'connected':True, 'disabled_syn':None})
      self.graph.add_edge(pre.name,post.name,mode=mode)
      return True

    def disconnect(self, pre, post):
      """
      Toggles the connection off between presynaptic and postsynaptic populations. Useful in disinhibition mechanisms
      @param pre str String pointing to Population in network.
      @param post str String pointing to Population in network.
      """
      if type(pre) == str:
        pre = self.populations[pre]
      if type(post) == str:
        post = self.populations[post]
      for recv in post.receiver:
        if (recv['from'] == pre.name and recv['connected'] == True):
          recv['disabled_syn'] = np.copy(recv['syn'])
          recv['syn'] = np.zeros(recv['syn'].shape)#zero it out!
          recv['connected'] = False
          self.graph.remove_edge(pre.name,post.name)
          break#we only need to find the first one
    def reconnect(self, pre, post):
      """
      Toggles the connection off between presynaptic and postsynaptic populations. Useful in disinhibition mechanisms
      @param pre str String pointing to Population in network.
      @param post str String pointing to Population in network.
      """
      if type(pre) == str:
        pre = self.populations[pre]
      if type(post) == str:
        post = self.populations[post]
      for recv in post.receiver:
        if (recv['from'] == pre.name and recv['connected'] == False):
          recv['syn'] = np.copy(recv['disabled_syn'])#restore the synapses
          recv['connected'] = True
          self.graph.add_edge(pre.name,post.name,mode=recv['mode'])
          break

    def get(self,pname):
      """
      Returns a Population if it is in class, None otherwise
      @param pname str
      """
      if self.populations[pname]:
        return self.populations[pname]
      else:
        print("%s not found!" % pname)
        return None
    def setup(self, experiment_name='My Experiment', T=50,dt=0.125,integration_time=30, I_ext={},spike_delta=50,save_data='./',properties_to_save=[],stdp=True):
      """
      Setup simulation state variables prior to running it
      @param experiment_name str String pointing to Population in network.
      @param T int Total time to simulate (milliseconds).
      @param dt float Time step in difference equation (milliseconds).
      @param integration_time float Number of milliseconds to integrate over when convolving spike rasters with postsynaptic current decay function
      @param I_ext dict Dictionary containing key-value pairs of Population names to stimulate and associated array of stimulus dictionaries.
      @param spike_delta Height of voltage spike. Not relevant for postsynaptic potential but may affect change in adaptation variable.
      @param save_data str Path to save data to
      @param properties_to_save array Array of which Population properties to save
      @param stdp Boolean Whether to use spike-time-dependent plasticity
      """
      self.now             = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
      self.T          = T
      self.dt         = dt
      self.time_trace = np.arange(0,T+dt,dt)#time array
      self.stdp = stdp
      self.I_ext = I_ext

      self.params = {
        'experiment_name' : experiment_name,
        'time_stamp' : self.now,
        'T' : self.T,
        'dt' : self.dt,
        'populations' : {},
        'properties_to_save' : properties_to_save,
        'I_ext' : I_ext,
        'save_data' : save_data,
        'experiment_log' : save_data + self.now + '-' + 'experiment.pkl'
      }

      for name, p in self.populations.items(): self.params['populations'][name] = p.N

      if (save_data):
        params_file = open(self.params['experiment_log'],'wb')
        pickle.dump(self.params, params_file)
        params_file.close()

      #initialize populations for simulation.
      for name, p in self.populations.items():
        p.initialize(T, len(self.time_trace), integration_time, save_data, self.now, properties_to_save, dt)
      return self.params

    def simulate(self, experiment_name='My Experiment', T=50,dt=0.125,integration_time=30, I_ext={},spike_delta=50,save_data='./',properties_to_save=[],stdp=True):
      """
      Simulate the Network
      """
      params = self.setup(experiment_name, T,dt,integration_time, I_ext,spike_delta,save_data,properties_to_save,stdp)
      #pdb.set_trace()
      #check spike_raster size and time_trace size...
      #run the simulation
      for i, t in enumerate(self.time_trace[1:],1):
        #update state variables
        print(str(i) + " - " + str(t) + " - " + str(self.time_trace.shape[0]))
        print('i=%d'%i)
        for name, p in self.populations.items():
          #if i==96:pdb.set_trace()
          p.update_currents(all_populations=self.populations, I_ext=I_ext, i=i, t=t, dt=self.dt)
          p.update_state(i=i, T=self.T, t=t, dt=self.dt)
          if self.stdp:
            p.update_synapses(all_populations=self.populations, i=i)
        #TODO : move this to be called by populations
        if (save_data):
          #we don't want to update synapses of one population after saving te data of another so that's why we do save_data after simulation
          #step is finished for all populations
          for name, p in self.populations.items():
            p.write_files(i)
        print("%0.3f%% done. t=%d msec" % ((float(i)/len(self.time_trace)*100.0),t))
      #simulation done - close the files
      #pdb.set_trace()#check
      if (save_data):
        for name, p in self.populations.items():
          p.close()
      if (save_data): return params#can be called by load_data right away
      else: return True
