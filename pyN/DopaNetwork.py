'''
Custom DopaNetwork class for running the simulation.

'''
import numpy as np

from synapse import *
from Network import Network
from datetime import datetime
import pickle
from random import randint

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
          thal_add = self.get('thal+')
          thal_sub = self.get('thal-')
          thal_in = self.get('thal_in')


          if np.sum(thal_add.spike_raster[:,i])/(thal_add.N/2) >= 0.5:
            print '\t\t\t\tincreasing...'
            self.foobar = self.foobar_prev + 1#increase state variable
            self.foobar_prev = self.foobar

          if np.sum(thal_sub.spike_raster[:,i])/(thal_sub.N/2) >= 0.5:
            print '\t\t\t\tdecreasing...'
            self.foobar = self.foobar_prev - 1#increase state variable
            self.foobar_prev = self.foobar

          #diff = distance from target relative to prev
          diff = np.abs(100 - self.foobar_prev) - np.abs(100 - self.foobar)
          #action update
          if diff > 0:
            #we are closer to target -> dopamine burst
            print 'dopa burst'
            self.reconnect(pre='snc',post='Go+')
            self.reconnect(pre='snc',post='Go-')
            self.reconnect(pre='snc',post='NoGo+')
            self.reconnect(pre='snc',post='NoGo-')

            self.disconnect(pre='NoGo+',post='gpe+')
            self.disconnect(pre='NoGo-',post='gpe-')
            self.reconnect(pre='Go+',post='gpi+')
            self.reconnect(pre='Go-',post='gpi-')

            self.reconnect(pre='gpe+',post='gpi+')
            self.reconnect(pre='gpe-',post='gpi-')
            self.disconnect(pre='gpi+',post='thal+')
            self.disconnect(pre='gpi-',post='thal-')
          elif diff < 0:
            #we are farther from target -> dopamine dip
            print 'dopa dip'
            self.disconnect(pre='snc',post='Go+')
            self.disconnect(pre='snc',post='Go-')
            self.disconnect(pre='snc',post='NoGo+')
            self.disconnect(pre='snc',post='NoGo-')

            self.reconnect(pre='NoGo+',post='gpe+')
            self.reconnect(pre='NoGo-',post='gpe-')
            self.disconnect(pre='Go+',post='gpi+')
            self.disconnect(pre='Go-',post='gpi-')

            self.disconnect(pre='gpe+',post='gpi+')
            self.disconnect(pre='gpe-',post='gpi-')
            self.reconnect(pre='gpi+',post='thal+')
            self.reconnect(pre='gpi-',post='thal-')
          elif diff == 0:
            #neutral state. Give some random input to a couple neurons
            #should we switch back to 'Go' mode so actions can happen?
            print 'neutral'
            x = randint(0,thal_in.N-4)
            thal_in.I_ext[x:x+3]

          #encode environment (foobar) into thalamus
          #thal.I_ext[0:20] += np.abs(self.foobar)/10#5 corresponds to the input feeding to 5 neurons

          #write to file
          foofile.write(str(self.foobar)+'\n')

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
