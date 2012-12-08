'''
Initialization script for Motor Controller
'''

from __future__ import division
import bge
from pyN import *

def main():
    print('initializing network...')
    cont = bge.logic.getCurrentController()
    brain = cont.owner

    SNc      = IzhikevichPopulation(name='snc',N=60,a=0.02,b=0.25, c=-50,d=2,v0=-70, connectivity="sparse-random")

    #Go Populations
    go1   = IzhikevichPopulation(name='go_1', N=10, connectivity="sparse-random")
    go2   = IzhikevichPopulation(name='go_2', N=10, connectivity="sparse-random")
    go3   = IzhikevichPopulation(name='go_3', N=10, connectivity="sparse-random")
    go4   = IzhikevichPopulation(name='go_4', N=10, connectivity="sparse-random")
    go5   = IzhikevichPopulation(name='go_5', N=10, connectivity="sparse-random")
    go6   = IzhikevichPopulation(name='go_6', N=10, connectivity="sparse-random")

    nogo1   = IzhikevichPopulation(name='nogo_1', N=10, connectivity="sparse-random")
    nogo2   = IzhikevichPopulation(name='nogo_2', N=10, connectivity="sparse-random")
    nogo3   = IzhikevichPopulation(name='nogo_3', N=10, connectivity="sparse-random")
    nogo4   = IzhikevichPopulation(name='nogo_4', N=10, connectivity="sparse-random")
    nogo5   = IzhikevichPopulation(name='nogo_5', N=10, connectivity="sparse-random")
    nogo6   = IzhikevichPopulation(name='nogo_6', N=10, connectivity="sparse-random")

    #thalamic input populations -> these should sort of mush together in the cortex and then feed back to the output populations
    thal_in_1 = IzhikevichPopulation(name='thal_in_1',N=20, connectivity="sparse-random")
    thal_in_2 = IzhikevichPopulation(name='thal_in_2',N=20, connectivity="sparse-random")
    thal_in_3 = IzhikevichPopulation(name='thal_in_3',N=20, connectivity="sparse-random")
    thal_in_4 = IzhikevichPopulation(name='thal_in_4',N=20, connectivity="sparse-random")
    thal_in_5 = IzhikevichPopulation(name='thal_in_5',N=20, connectivity="sparse-random")
    thal_in_6 = IzhikevichPopulation(name='thal_in_6',N=20, connectivity="sparse-random")


    #thalamic output populations -> where motor output comes out
    thal_out_1 = IzhikevichPopulation(name='thal_out_1',N=20, connectivity="sparse-random")
    thal_out_2 = IzhikevichPopulation(name='thal_out_2',N=20, connectivity="sparse-random")
    thal_out_3 = IzhikevichPopulation(name='thal_out_3',N=20, connectivity="sparse-random")
    thal_out_4 = IzhikevichPopulation(name='thal_out_4',N=20, connectivity="sparse-random")
    thal_out_5 = IzhikevichPopulation(name='thal_out_5',N=20, connectivity="sparse-random")
    thal_out_6 = IzhikevichPopulation(name='thal_out_6',N=20, connectivity="sparse-random")


    GPi = IzhikevichPopulation(name='gpi',N=60, connectivity="sparse-random")
    GPe  = IzhikevichPopulation(name='gpe',N=60, connectivity="sparse-random")


    PFC  = IzhikevichPopulation(name='pfc', N=340, connectivity="sparse-random")
    #gain modulator for PFC
    PFC_inhib = IzhikevichPopulation(name='pfc_inhib',N=60,connectivity="sparse-random")



    net = DopaController(populations=[SNc, GPi, GPe, PFC, PFC_inhib, go1, go2, go3, go4, go5, go6, nogo1, nogo2, nogo3, nogo4, nogo5, nogo6, thal_in_1, thal_in_2, thal_in_3, thal_in_4, thal_in_5, thal_in_6, thal_out_1, thal_out_2, thal_out_3, thal_out_4, thal_out_5, thal_out_6])
    for i in range(1,7):
      #SNc -> excitatory"to "G"o+/- and inhibitory to NoGo +/-
      """
      Striatal stuff
      """
      go = "go_" + str(i)
      nogo = "nogo_" + str(i)
      net.connect(pre="snc", post=go, synapses="sparse-random", mode="excitatory", delay=2.25,std=0.25)
      net.connect(pre="snc", post=nogo, synapses="sparse-random", mode="inhibitory", delay=2.25,std=0.25)
      #frontal cortex ->"excitatory connections to all the striatal populations
      net.connect(pre="pfc", post=go, synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
      net.connect(pre="pfc", post=nogo, synapses="sparse-random", mode='excitatory', delay=2.25,std=0.25)
      #Go inhibits GPi
      net.connect(pre=go, post="gpi", synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
      #NoGo inhibits Gpe (disinhibited)
      net.connect(pre=nogo, post='gpe', synapses='sparse-random', mode='inhibitory', delay=2.25, std=0.25)
      net.disconnect(pre=nogo, post='gpe')
      """
      Thalamic I/O stuff
      """
      #GPi inhibits Thalamus (disinhibited)
      thal_in = "thal_in_" + str(i)
      thal_out = "thal_out_" + str(i)
      net.connect(pre='gpi', post=thal_out, synapses="sparse-random", mode='inhibitory', delay=3.25,std=1.25)
      net.disconnect(pre='gpi', post=thal_out)
      #Thalamic bidirectional activity to PFC
      net.connect(pre='pfc', post=thal_in, synapses="sparse-random", mode='excitatory', delay=3.25,std=0.25)
      net.connect(pre='pfc', post=thal_out, synapses="sparse-random", mode='excitatory', delay=3.25,std=0.25)
      net.connect(pre=thal_in, post='pfc', synapses="sparse-random", mode='excitatory', delay=3.25,std=0.25)
      net.connect(pre=thal_out, post='pfc', synapses="sparse-random", mode='excitatory', delay=3.25,std=0.25)

    """
    other non-repetitive connections
    """

    #GPe inhibits GPi
    net.connect(pre='gpe', post='gpi', synapses="sparse-random", mode='inhibitory', delay=2.25,std=0.25)

    #PFC 15% inhibition gain modulation
    net.connect(pre='pfc', post='pfc_inhib', synapses="sparse-random", mode='excitatory')
    net.connect(pre='pfc_inhib', post='pfc', synapses="sparse-random", mode='inhibitory')


    #simulate is NOT called Otherwise this would be a blocking process.

    #run the network -> this should run independently?
    params = net.setup(experiment_name='seg-iz-unsegregated', T=6, dt=0.25, save_data='/Users/eric/Documents/College/CLPS1492/final/data/prelim/', properties_to_save=['v','spike_raster','I_rec'],stdp=True)

    #IMPORTANT, WE ARE KEEPING TRACK OF OUR OWN LOGIC TICKS WITHIN NETWORK
    #THESE NEED TO BE MANUALLY UPDATED in step_net.py
    self.i = 1
    self.t = self.time_trace[1]

    self.mode_lock = np.int(5.0/dt)
    #draw the NetworkX graphs
    if (save_data):
      #draw the NetworkX graphs
      self.draw_graph(save_data,now,mode='Go')
      self.draw_graph(save_data,now,mode='NoGo')
      self.set_mode('Go')#import to reset back to state!

    brain['net'] = net

    #####
    print('network successfully initialized')
main()
