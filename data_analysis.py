'''
will need to be changed significantly.
Given a params object or a results string, plot any data needed
'''

import numpy as np
import pickle
import matplotlib.pyplot as plt
import ipdb as pdb

def show_data(params):
  #given a file path string or simulation results (embedded in a parmas object), re-load into memory and plot.
  if type(params) == str:
    #recover params from file
    params_file = open(params,'r')
    params = pickle.load(params_file)
    params_file.close()
  else:
    time_stamp = params['time_stamp']

  #rebuild the time trace (for x axis plotting)
  time_trace = np.arange(0, params['T']+params['dt'],params['dt'])
  #TODO : rebuild the stim trace

  #display the trace for each population
  num_populations = len(params['populations'].keys())#number of populations
  num_properties = len(params['properties_to_save'])
  path = params['save_data']

  f, axarr = plt.subplots(nrows=num_properties, ncols=num_populations)

  #load and plot each property saved for each population
  #this may require custom plotting based on the proeprty
  #populations plotted across columns (j), properties across rows (i)
  j = 0#population index
  for name, N in params['populations'].items():
    for i, prop in enumerate(params['properties_to_save']):
      #j = property index
      trace = np.loadtxt(path + params['time_stamp'] + '-' + name + '-' + prop)
      if num_populations == 1:
        #matplotlib handles single-dimension subplots in a 1D array instead of a nested 2D array.
        ax = axarr[i]
      else:
        ax = axarr[i,j]
      ax.set_title(name + '-' + prop)
      ax.plot(time_trace[1:],trace)
    j += 1
  plt.autoscale(enable=False)
  plt.show()
    #
    # stim_trace   = np.loadtxt(path + time_stamp + '-' + name + '-' + 'stim').reshape((N,-1))
    # v_trace      = np.loadtxt(path + time_stamp + '-' + name + '-' + 'v').reshape((N,-1))
    # w_trace      = np.loadtxt(path + time_stamp + '-' + name + '-' + 'w').reshape((N,-1))
    # I_trace      = np.loadtxt(path + time_stamp + '-' + name + '-' + 'I').reshape((N,-1))
    # spike_raster = np.loadtxt(path + time_stamp + '-' + name + '-' + 'raster').reshape((N,-1))


    # stim_trace   = np.transpose(stim_trace)
    #     v_trace      = np.transpose(v_trace)
    #     w_trace      = np.transpose(w_trace)
    #     I_trace      = np.transpose(I_trace)
    #     spike_raster = np.transpose(spike_raster)
    #     #figure + 3 subplots for each trace
    #     if numpop == 1:
    #       #use 1D plotting
    #       axarr[0].plot(time_trace[1:],spike_raster,'.')
    #       axarr[1].plot(time_trace[1:],v_trace)
    #       axarr[2].plot(time_trace[1:],stim_trace[1:])
    #       axarr[3].plot(time_trace[1:],w_trace)
    #
    #       axarr[0].set_title(name + ' spike raster')
    #       axarr[1].set_title(name + ' membrane potential')
    #       axarr[2].set_title(name + ' input current (minus injected)')
    #       axarr[3].set_title(name + ' adaptation')
    #     else:
    #       axarr[0,i].plot(time_trace[1:],spike_raster,'.')
    #       axarr[1,i].plot(time_trace[1:],I_trace,time_trace[1:],stim_trace[1:])#also include the external stimuli
    #       axarr[2,i].plot(time_trace[1:],stim_trace[1:])
    #       axarr[3,i].plot(time_trace[1:],w_trace)
    #
    #       axarr[0,i].set_title(name + ' spike raster')
    #       axarr[1,i].set_title(name + ' membrane potential')
    #       axarr[2,i].set_title(name + ' input current (minus injected)')
    #       axarr[3,i].set_title(name + ' adaptation')
    #     i+=1
    #   plt.autoscale(enable=False)
    #   #plt.tight_layout()#no overlapping labels!
    #   plt.show()