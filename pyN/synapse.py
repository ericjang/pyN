import numpy as np
import ipdb as pdb


def generate_synapses(pre_population, post_population, connectivity="sparse-random",delay=0.25,std=0.05):
  '''
  returns synapse matrix
  pre_population and post_population can either be a Population object OR dimensions (int) of population objects
  '''
  if type(pre_population) == int:
    N = pre_population
  else:
    N = pre_population.N
  if type(post_population) == int:
    M = post_population
  else:
    M = post_population.N

  if connectivity == "none":
    synapses = np.zeros([M,N])
  elif connectivity == "full-random":
    synapses = np.random.random([M,N])
  elif connectivity == "sparse-random":
    synapses = np.random.random([M,N])
    syn_filter = (np.random.random([M,N]) < 0.1)#randomly filter out 90% of synapses, so only a 10th have weights
    synapses *= syn_filter
  else:
    raise Exception("connectivity type not recognized! Check your spelling...")
  #we don't want neurons to recurrently excite themselves! so we set them to zero
  np.fill_diagonal(synapses,0)

  #generate appropriate distance matrices
  delays = generate_delay_matrix(N,M,delay=delay,std=std) #distance matrix
  return (synapses, delays)

def generate_delay_matrix(pre_population, post_population, delay=0.25, std=0.1):
  '''
  given delay time (msec), return a random, symmetric delay matrix with diagonal = 0. random entries normally distributed around delay.
  std = standard deviation of delay time
  '''
  if type(pre_population) == int:
    N = pre_population
  else:
    N = pre_population.N
  if type(post_population) == int:
    M = post_population
  else:
    M = post_population.N

  distances = np.random.normal(loc=delay,scale=std,size=(M,N))

  if pre_population == post_population and type(pre_population) == type(post_population):
    #if pre_population identical to post_population (recurrent), then make matrix symmmetric with zeros in diagonal
    distances += distances.T - np.diag(distances.diagonal())
    np.fill_diagonal(distances,0)
  return distances


def stdp(time_diff, mode, A=0.01, tau=20):
  '''
  STDP function
  time_diff is a N x ~200 matrix of time delays of spikes leading up to time i
  values are positive if time_diff came from spikes preceding time i, and negative if following time i

  returns delta_w value. However, values still need to be scaled according to how many times repeat took place, which requires
  access to the population's synapse matrix. That will be applied AFTER stdp()

  be careful here -> I am only performing exp on the nonzero parts, but that means that the returned array won't line up across time-row. That is
  okay though, because

  '''
  repeat_scaling = np.float(1.0/50)#the LTP equations actually only manifest after ~50 repetitions
  #this may not perform as well, may have to model sigmoid based on repetitions
  #note, if repeat_scaling = 1 (stdp curve applied after 1 repetition, then the network goes nuts. Be careful!)
  mask = (time_diff != 0)
  if mode == "LTP":
    time_diff[mask] = A * np.exp(-1 * time_diff[mask]/tau)
  elif mode == "LTD":
    time_diff[mask] = -A * np.exp(time_diff[mask]/tau)
  return time_diff * repeat_scaling