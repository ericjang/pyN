'''
contains DopaNetwork class as well as a DopaController Class for the actual motor simulation project.
'''
import numpy as np

from synapse import *
from Network import Network
from datetime import datetime
import pickle
from random import randint

import networkx as nx
import matplotlib.pyplot as plt

try:
  import bge
except:
  pass

class DopaNetwork(Network):
    """Custom DopaNetwork class for running the simulation."""
    def __init__(self, populations=[]):
      Network.__init__(self, populations)

    #we are only modifying the simulate() method so that certain parameters are saved at every time step.
    def simulate(self, experiment_name='My Reinforcement Learning Experiment', T=50,dt=0.125,integration_time=30, I_ext={}, spike_delta=50,save_data='./',properties_to_save=[],stdp=True):
        """Parameters are the same as Network.simulate(), except this has built-in actor-critic logic for dishing out reward from SNc"""
        params = self.setup(experiment_name, T,dt,integration_time, I_ext,spike_delta,save_data,properties_to_save,stdp)

        self.mode_lock = np.int(5.0/dt)#allows dopamine bursts to be sustained over a period of 5msec in order for propagation of dopaminergic effect
        self.foobar = 0#hopefully this should decrease
        self.foobar_prev = 0
        self.I_ext = I_ext

        foofile = open(save_data + self.now + '-foobar', 'a')

        if (save_data):
          #draw the NetworkX graphs
          self.draw_graph(save_data,self.now,mode='Go')
          self.draw_graph(save_data,self.now,mode='NoGo')
          self.set_mode('Go')#import to reset back to state!

        #run the simulation
        for i, t in enumerate(self.time_trace[1:],1):
          #update state variables
          for name, p in self.populations.items():
            p.update_currents(all_populations=self.populations, I_ext=self.I_ext, i=i, t=t, dt=self.dt)
            p.update_state(i=i, T=self.T, t=t, dt=self.dt)
            if self.stdp:
              p.update_synapses(all_populations=self.populations, i=i, w_min=-.3,w_max=.3)
          self.update_environment(i)
          #write to file
          foofile.write(str(self.foobar)+'\n')

          if (save_data):
            #we don't want to update synapses of one population after saving te data of another so that's why we do save_data after simulation
            #step is finished
            for name, p in self.populations.items():
              p.write_files(i)
          print("%0.3f%% done. t=%d msec foobar=%d" % ((float(i)/len(self.time_trace)*100.0),t,self.foobar))

        #simulation done - close the files
        if (save_data):
          for name, p in self.populations.items():
            p.close()
        if (save_data): return params#can be called by load_data right away
        else: return True

    def set_mode(self,mode):
      """
      Switch the BG network between Go and NoGo states.
      """
      if mode=='Go':
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
      if mode=='NoGo':
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

    def draw_graph(self,parent_path,now,mode):
       """Draws the network graph using NetworkX and pyplot."""
       self.set_mode(mode)
       plt.figure(figsize=(8,8))
       pos=nx.circular_layout(self.graph)
       nx.draw_networkx_nodes(self.graph,pos=pos,node_size=[self.populations[p].N*30 for p in self.graph])
       nx.draw_networkx_labels(self.graph,pos=pos)
       E_edges=[(u,v) for (u,v,d) in self.graph.edges(data=True) if d['mode']=='excitatory']
       I_edges=[(u,v) for (u,v,d) in self.graph.edges(data=True) if d['mode']=='inhibitory']
       nx.draw_networkx_edges(self.graph,pos=pos,edgelist=E_edges,width=1)
       nx.draw_networkx_edges(self.graph,pos=pos,edgelist=I_edges,width=1,alpha=0.5,edge_color='blue',style='dashed')
       plt.axis('off')
       plt.savefig(parent_path+now+mode+'network.png')
       plt.close()

    def update_environment(self, i):
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

      #tonically active populations - give them new random input!
      tonic = [self.get('snc'),self.get('gpe+'),self.get('gpe-')]
      for tnc in tonic:
        x = randint(0,tnc.N-5)
        tnc.I_ext[x:x+4] += 10

      if np.sum(thal_add.spike_raster[:,i]) > np.sum(thal_sub.spike_raster[:,i]):
        print('\t\t\t\tincreasing...')
        self.foobar += 1#increase state variable

      if np.sum(thal_add.spike_raster[:,i]) < np.sum(thal_sub.spike_raster[:,i]):
        print('\t\t\t\tdecreasing...')
        self.foobar += -1#decrease state variable
      #diff = distance from target relative to prev
      diff = np.abs(100 - self.foobar_prev) - np.abs(100 - self.foobar)
      #action update
      if diff > 0 and self.mode_lock < 0:
        #we are closer to target -> dopamine burst
        print('dopa burst')
        self.set_mode('Go')
        self.mode_lock = np.int(5.0/self.dt)
      elif diff < 0 and self.mode_lock < 0:
        #we are farther from target -> dopamine dip
        print('dopa dip')
        self.set_mode('NoGo')
        self.mode_lock = np.int(5.0/self.dt)
      elif diff == 0:
        #neutral state. Give some random input to a couple neurons
        #should we switch back to 'Go' mode so actions can happen?
        print('neutral')
        x = randint(0,thal_in.N-4)
        thal_in.I_ext[x:x+3] += 20
      self.mode_lock -= 1#decrease the mode_lock counter
      self.foobar_prev = self.foobar


class UnsegDopaNetwork(DopaNetwork):
    def __init__(self, populations=[]):
      DopaNetwork.__init__(self, populations)

    def set_mode(self,mode):
      if mode=='Go':
        self.reconnect(pre='snc',post='Go+')
        self.reconnect(pre='snc',post='Go-')
        self.reconnect(pre='snc',post='NoGo+')
        self.reconnect(pre='snc',post='NoGo-')

        self.disconnect(pre='NoGo+',post='gpe')
        self.disconnect(pre='NoGo-',post='gpe')
        self.reconnect(pre='Go+',post='gpi')
        self.reconnect(pre='Go-',post='gpi')

        self.reconnect(pre='gpe',post='gpi')
        self.disconnect(pre='gpi',post='thal+')
        self.disconnect(pre='gpi',post='thal-')
      if mode=='NoGo':
        self.disconnect(pre='snc',post='Go+')
        self.disconnect(pre='snc',post='Go-')
        self.disconnect(pre='snc',post='NoGo+')
        self.disconnect(pre='snc',post='NoGo-')

        self.reconnect(pre='NoGo+',post='gpe')
        self.reconnect(pre='NoGo-',post='gpe')
        self.disconnect(pre='Go+',post='gpi')
        self.disconnect(pre='Go-',post='gpi')

        self.disconnect(pre='gpe',post='gpi')
        self.reconnect(pre='gpi',post='thal+')
        self.reconnect(pre='gpi',post='thal-')

    def update_environment(self,i):
      '''
      Actor-Critic architecture is implemented here. Not that input reality space to network is unlikely to be truly homomorphic to the actor's output space unless
      it is embodied.

      #Reward-based learning & Dopamine Detection -> if average activity of Go+ population > threshold,
        #then increase Network score and switch state -> Go and inject dopamine
      #if average activity of Go- activity > threshold, decrease the Network score
        #then switch state -> NoGo

      Thalamus decides action???
      '''
      thal_add = self.get('thal+')
      thal_sub = self.get('thal-')

      #tonically active populations - give them new random input!
      tonic = [self.get('snc'),self.get('gpe'),self.get('thal_in')]
      for tnc in tonic:
        x = randint(0,tnc.N-10)
        tnc.I_ext[x:x+9] += 20

      if np.sum(thal_add.spike_raster[:,i]) > np.sum(thal_sub.spike_raster[:,i]):
        print('\t\t\t\tincreasing...')
        self.foobar += 1#increase state variable

      if np.sum(thal_add.spike_raster[:,i]) < np.sum(thal_sub.spike_raster[:,i]):
        print('\t\t\t\tdecreasing...')
        self.foobar += -1#decrease state variable
      #diff = distance from target relative to prev
      diff = np.abs(100 - self.foobar_prev) - np.abs(100 - self.foobar)
      #action update
      if diff > 0 and self.mode_lock < 0:
        #we are closer to target -> dopamine burst
        print('dopa burst')
        self.set_mode('Go')
        self.mode_lock = np.int(5.0/self.dt)
      elif diff < 0 and self.mode_lock < 0:
        #we are farther from target -> dopamine dip
        print('dopa dip')
        self.set_mode('NoGo')
        self.mode_lock = np.int(5.0/self.dt)
      elif diff == 0:
        #neutral state. Give some random input to a couple neurons
        #should we switch back to 'Go' mode so actions can happen?
        print('neutral')

      #deliver to tonic thal_in
      self.mode_lock -= 1#decrease the mode_lock counter
      self.foobar_prev = self.foobar

class DopaController(DopaNetwork):
  """even-more custom class for the BGE simulation of Motor Control"""
  def __init__(self, populations=[]):
    Network.__init__(self, populations)
  def set_mode(self,mode):
    """
    Switch the BG network between Go and NoGo states.
    """
    if mode=='Go':
      for i in range(1,7):
        go = "go_" + str(i)
        nogo = "nogo_" + str(i)
        thal_out = "thal_out_" + str(i)
        self.reconnect(pre='snc', post=go)
        self.reconnect(pre='snc', post=nogo)
        self.disconnect(pre=nogo, post='gpe')
        self.reconnect(pre=go, post='gpi')
        self.reconnect(pre='gpe',post='gpi')
        self.disconnect(pre='gpi',post=thal_out)
    elif mode=='NoGo':
      for i in range(1,7):
        go = "go_" + str(i)
        nogo = "nogo_" + str(i)
        thal_out = "thal_out_" + str(i)
        self.disconnect(pre='snc', post=go)
        self.disconnect(pre='snc', post=nogo)
        self.reconnect(pre=nogo, post='gpe')
        self.disconnect(pre=go, post='gpi')
        self.disconnect(pre='gpe',post='gpi')
        self.reconnect(pre='gpi',post=thal_out)
    elif mode=='Neutral':
      #disconnect dopaminergic bursting...
      for i in range(1,7):
        go = "go_" + str(i)
        nogo = "nogo_" + str(i)
        self.disconnect(pre='snc', post=go)
        self.disconnect(pre='snc', post=nogo)

  def update_environment(self,i,):
    """
    code here switches robot into go or nogo state depending on whether they

    go mode -> when robot touches (approaches?) food
    nogo mode -> when robot touches poison
    neutral mode -> needs to somehow facilitate exploration... perhaps switch to go mode after set time.


    rewarded when:
      - touches food

    neutral when:
      - no longer in contact with food
      - no longer in contact with poison

    punished when:
      - touches poison

    """

    #print('applying actuators...')
    """
    Blender sensor code is in trigger_sensor, not here

    Robot applies any actuators that are active enough
    """
    scene = bge.logic.getCurrentScene()
    brain = scene.objects['brain']
    for t in range(1,7):
      thal_out = self.get("thal_out_" + str(t))
      if np.sum(thal_out.spike_raster[:,i])/thal_out.N > 0.3:
        #more than half the neurons are active, move the effector called "arm"+str(t)!
        arm = scene.objects['arm'+str(t)]
        opp_arm = scene.objects['arm'+str(7-t)]#it so happens that the arms mirror their complement so they add up to 7.
        arm.localScale.x += 0.1
        #shrink the other effector
        opp_arm.localScale.x -= 0.1
        #the sensor shell should naturally follow in the same direction!
        print('moving arm%s' % str(t))





