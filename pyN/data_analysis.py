'''
will need to be changed significantly.
Given a params object or a results string, plot any data needed
'''

import numpy as np
import pickle
import matplotlib.pyplot as plt
import ipdb as pdb

def process_data(params):
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
  #quick fix:

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
      trace = np.loadtxt(path + params['time_stamp'] + '-' + name + '-' + prop).reshape((-1,N))
      if num_populations == 1:
        #matplotlib handles single-dimension subplots in a 1D array instead of a nested 2D array.
        ax = axarr[i]
      else:
        ax = axarr[i,j]
      ax.set_title(name + ' - ' + prop)
      if prop == 'spike_raster':
        trace[trace == 0] = np.nan
        #scaling vector to separate out the dots from all = 1
        scale = np.array([k for k in range(trace.shape[1])])
        ax.plot(time_trace[1:],trace * scale[np.newaxis,:],'.')
      else:
        ax.plot(time_trace[1:],trace)
    j += 1
  #plt.autoscale(enable=False)
  plt.tight_layout()
  plt.suptitle(params['experiment_name'],fontsize=18)
  plt.subplots_adjust(top=0.85)
  fname = params['time_stamp'] + '-' + params['experiment_name'] + '.png'
  return (f, fname)


def show_data(params):
  process_data(params)
  plt.show()

def save_data(params,path):
  #for computational efficiency reasons, save each plot separately! (also because old matplotlib doesn't support 'subplots')
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
  #display the trace for each population
  num_populations = len(params['populations'].keys())#number of populations
  num_properties = len(params['properties_to_save'])
  path = params['save_data']

  for name, N in params['populations'].items():
    for i, prop in enumerate(params['properties_to_save']):
      fig = plt.figure()
      plt.title(name + ' - ' + prop)
      if prop == 'spike_raster':
        trace = np.loadtxt(path + params['time_stamp'] + '-' + name + '-' + prop).reshape((-1,N))
        trace[trace == 0] = np.nan
        #scaling vector to separate out the dots from all = 1
        scale = np.array([k for k in range(trace.shape[1])])
        plt.plot(time_trace[1:],trace * scale[np.newaxis,:],'.')
      elif prop == 'I_ext':
        if name in params['I_ext']:
          trace = np.zeros([params['populations'][name], time_trace[1:].shape[0]])
          for j in range(1,time_trace.shape[0]):
            for stim in params['I_ext'][name]:
              if stim['start'] <= j * params['dt'] <= stim['stop']:
                #drive only neurons specified in stim['neurons']
                current = np.zeros(params['populations'][name])
                current[stim['neurons']] = stim['mV']
                trace[:,j] += current
          plt.plot(time_trace[1:],trace.T)
      else:
        trace = np.loadtxt(path + params['time_stamp'] + '-' + name + '-' + prop).reshape((-1,N))
        plt.plot(time_trace[1:],trace)
        #plt.tight_layout()
        #plt.subplots_adjust(top=0.85)
      fname = params['time_stamp'] + '-' + params['experiment_name'] + name + prop + '.png'
      print fname
      fig.savefig(path + fname)
      #clear it?
      plt.close('all')
