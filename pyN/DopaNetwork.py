'''
Custom DopaNetwork class for running the simulation.

'''
import numpy as np

from synapse import *
from Network import Network
from datetime import datetime
import pickle

class DopaNetwork(Network):
    def __init__(self, populations=[]):
      Network.__init__(self, populations)

    #we are only modifying the simulate() method so that certain parameters are saved at every time step.
    def simulate(self, experiment_name='My Reinforcement Learning Experiment', T=50,dt=0.125,integration_time=30, I_ext=None, spike_delta=100,save_data='./',properties_to_save=[],stdp=True):
        now             = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.T          = T
        self.dt         = dt
        self.time_trace = np.arange(0,T+dt,dt)#time array
        self.stdp = stdp

        self.foobar = 0#hopefully this should decrease
        self.foobar_prev = 0

        #open a file for writing to
        foofile = open(save_data + now + '-foobar', 'a')

        params = {
          'experiment_name' : experiment_name,
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
          p.initialize(T, len(self.time_trace), integration_time, save_data, now, properties_to_save, dt)

        #run the simulation
        for i, t in enumerate(self.time_trace[1:],1):
          #update state variables
          for name, p in self.populations.items():
            p.update_currents(all_populations=self.populations, I_ext=I_ext, i=i, t=t, dt=self.dt)
            p.update_state(i=i, T=self.T, t=t, dt=self.dt)
            if self.stdp:
              p.update_synapses(all_populations=self.populations, i=i)
          '''
          #Reward-based learning & Dopamine Detection -> if average activity of Go+ population > threshold,
            #then increase Network score and switch state -> Go and inject dopamine
          #if average activity of Go- activity > threshold, decrease the Network score
            #then switch state -> NoGo

          Thalamus decides action???
          '''
          thal = self.get('Thalamus')
          half = thal.N/2
          if np.sum(thal.spike_raster[50:75,i])/half >= 0.5:
            #dopamine burst
            print '\t\t\t\tincreasing...'
            self.foobar = self.foobar_prev + 1#update state variable
            self.foobar_prev = self.foobar
            thal.I_ext[20:35] += 14

          if np.sum(thal.spike_raster[75:100,i])/half >= 0.5:
            print '\t\t\t\tdecreasing...'
            self.foobar = self.foobar_prev - 1#update state variable
            self.foobar_prev = self.foobar
            thal.I_ext[35:50] += 14

          #action update
          if np.abs(100 - self.foobar) < np.abs(100 - self.foobar_prev):
            #we are closer to target!
            #dopamine burst
            print 'dopa burst'
            self.reconnect(pre='Substantia Nigra Complex',post='Go+')
            self.reconnect(pre='Substantia Nigra Complex',post='Go-')
            self.reconnect(pre='Substantia Nigra Complex',post='NoGo+')
            self.reconnect(pre='Substantia Nigra Complex',post='NoGo-')
            self.disconnect(pre='NoGo+',post='Globus Pallidus-External Segment')
            self.disconnect(pre='NoGo-',post='Globus Pallidus-External Segment')
            self.reconnect(pre='Go+',post='Globus Pallidus-Internal Segment')
            self.reconnect(pre='Go-',post='Globus Pallidus-Internal Segment')
            self.reconnect(pre='Globus Pallidus-External Segment',post='Globus Pallidus-Internal Segment')
            self.disconnect(pre='Globus Pallidus-Internal Segment',post='Thalamus')
          else:
            #dopamine dip
            print 'dopa dip'
            self.disconnect(pre='Substantia Nigra Complex',post='Go+')
            self.disconnect(pre='Substantia Nigra Complex',post='Go-')
            self.disconnect(pre='Substantia Nigra Complex',post='NoGo+')
            self.disconnect(pre='Substantia Nigra Complex',post='NoGo-')
            self.reconnect(pre='NoGo+',post='Globus Pallidus-External Segment')
            self.reconnect(pre='NoGo-',post='Globus Pallidus-External Segment')
            self.disconnect(pre='Go+',post='Globus Pallidus-Internal Segment')
            self.disconnect(pre='Go-',post='Globus Pallidus-Internal Segment')
            self.disconnect(pre='Globus Pallidus-External Segment',post='Globus Pallidus-Internal Segment')
            self.reconnect(pre='Globus Pallidus-Internal Segment',post='Thalamus')
            #ought to inspect state of network here...
            #pdb.set_trace()

          #encode environment (foobar) into thalamus
          thal.I_ext[0:20] += np.abs(self.foobar)/10#5 corresponds to the input feeding to 5 neurons

          #write to file
          foofile.write(str(self.foobar))

          if (save_data):
            #we don't want to update synapses of one population after saving te data of another so that's why we do save_data after simulation
            #step is finished
            for name, p in self.populations.items():
              p.save_data(i)
          print("%0.3f%% done. t=%d msec foobar=%d" % ((float(i)/len(self.time_trace)*100.0),t,self.foobar))

        #simulation done - close the files
        if (save_data):
          for name, p in self.populations.items():
            p.close()
        if (save_data): return params#can be called by load_data right away
        else: return True