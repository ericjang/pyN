import numpy as np

def generate_synapses(pre_population, post_population, connectivity="sparse-random",delay=0.25,std=0.25):
  '''
  returns synapse matrix
  pre_population and post_population can either be a Population object OR dimensions (int) of population objects
  '''
  if type(pre_population) == int:
    M = pre_population
  else:
    M = pre_population.N
  if type(post_population) == int:
    N = post_population
  else:
    N = post_population.N

  if connectivity == "none":
    synapses = np.zeros([N,M])
  elif connectivity == "full-random":
    synapses = np.random.random([N,M])
  elif connectivity == "sparse-random":
    synapses = np.random.random([N,M])
    syn_filter = (np.random.random([N,M]) < 0.1)#randomly filter out 90% of synapses, so only a 10th have weights
    synapses *= syn_filter
  else:
    raise Exception("connectivity type not recognized! Check your spelling...")
  #we don't want neurons to recurrently excite themselves! so we set them to zero
  np.fill_diagonal(synapses,0)

  #generate appropriate distance matrices
  delays = generate_delay_matrix(N,M,delay=delay,std=std) #distance matrix
  return (synapses,delays)

def generate_delay_matrix(pre_population, post_population, delay=0.25, std=0.1):
  '''
  given delay time (msec), return a random, symmetric delay matrix with diagonal = 0. random entries normally distributed around delay.
  std = standard deviation of delay time
  '''
  if type(pre_population) == int:
    M = pre_population
  else:
    M = pre_population.N
  if type(post_population) == int:
    N = post_population
  else:
    N = post_population.N

  distances = np.random.normal(loc=delay,scale=std,size=(N,M))

  if pre_population == post_population and type(pre_population) == type(post_population):
    #if pre_population identical to post_population (recurrent), then make matrix symmmetric with zeros in diagonal
    distances += distances.T - np.diag(distances.diagonal())
    np.fill_diagonal(distances,0)
  return distances