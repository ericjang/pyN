import numpy as np


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
    synapses = np.zeros([M,N,2])#the second layer is for the pre->then->post spike count
  elif connectivity == "full-random":
    synapses = np.zeros([M,N,2])
    synapses[:,:,0] = np.random.random([M,N])
  elif connectivity == "sparse-random":
    synapses = np.zeros([M,N,2])
    synapses[:,:,0] = np.random.random([M,N])
    syn_filter = (np.random.random([M,N]) < 0.1)#randomly filter out 90% of synapses, so only a 10th have weights
    synapses[:,:,0] *= syn_filter
  else:
    raise Exception("connectivity type not recognized! Check your spelling...")
  #we don't want neurons to recurrently excite themselves! so we set them to zero
  np.fill_diagonal(synapses[:,:,0],0)

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


def repetition_sigmoid(M):
  return 1/(1+np.exp(-0.2*M+10))

def stdp(time_diff, mode, A=0.01, tau=20):
  '''
  STDP function
  time_diff is a N x ~200 matrix of time delays of spikes leading up to time i
  values are positive if time_diff came from spikes preceding time i, and negative if following time i

  returns delta_w value. However, values still need to be scaled according to how many times repeat took place, which requires
  access to the population's synapse matrix. That will be applied AFTER stdp()


  '''
  temp = np.copy(time_diff)#we don't want to modify the original!
  mask = (temp != 0)
  if mode == "LTP":
    temp[mask] = A * np.exp(-1 * temp[mask]/tau)
  elif mode == "LTD":
    temp[mask] = -A * np.exp(temp[mask]/tau)
  return temp