'''
Network class for running populations.
Should be agnostic for population type
'''
import numpy as np

from synapse import *
from datetime import datetime
import pickle
import ipdb as pdb

class Network():
    def __init__(self, name='My Network', populations=[]):
      self.name        = name
      self.populations = {}
      for p in populations:
        self.populations[p.name] = p

    def connect(self, pre, post, synapses, delay_matrix=None):
      '''
      connect to populations together in a network
      pre - presynaptic group
      post - postsynaptic group
      synapses - single directional synapse connections from pre to post. Supports string-based shortcut generation of synapses if desired
      delay_matrix - delay matrix times.
      Let us see for now what happens when one region drives another without getting feedback...
      '''
      if type(synapses) == str:
        (gen_synapses, gen_delay_matrix) = generate_synapses(pre_population=pre, post_population=post, connectivity=synapses)
        synapses = gen_synapses

      if delay_matrix == None: delay_matrix = gen_delay_matrix

      self.populations[post].receiver.append({'from':pre,'syn':synapses, 'delay':delay_matrix})
      return True

    def simulate(self, T=50,dt=0.125,I_ext=None,spike_delta=100,save_data='./',properties_to_save=[]):
        now             = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.T          = T
        self.dt         = dt
        self.time_trace = np.arange(0,T+dt,dt)#time array

        params = {
          'time_stamp' : now,
          'T' : self.T,
          'dt' : self.dt,
          'populations' : {},
          'properties_to_save' : properties_to_save,
          'I_ext' : I_ext,
          'save_data' : save_data#the save path
        }

        for name, p in self.populations.items(): params['populations'][name] = p.N

        if (save_data):
          params_file = open(save_data + now + '-' + 'experiment.pkl','w')
          pickle.dump(params, params_file)
          params_file.close()

        #initialize populations for simulation.
        for name, p in self.populations.items():
          p.initialize(len(self.time_trace), save_data, now, properties_to_save, dt)


        #run the simulation
        for i, t in enumerate(self.time_trace[1:],1):
          #update state variables
          for name, p in self.populations.items(): p.update_currents(all_populations=self.populations, I_ext=I_ext, t=t)
          for name, p in self.populations.items(): p.update_state(i=i, T=self.T, t=t, dt=self.dt)
          #TODO : move this to be called by populations
          if (save_data):
            for name, p in self.populations.items():
              p.save_data(i)
          print("%0.3f%% done. t=%d msec" % ((float(i)/len(self.time_trace)*100.0),t))
        #simulation done - close the files
        if (save_data):
          for name, p in self.populations.items():
            p.close()
        if (save_data): return params#can be called by load_data right away
        else: return True