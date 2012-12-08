import numpy as np


def generate_synapses(pre_population, post_population, connectivity="sparse-random",delay=0.25,std=0.05,scale=1.0):
  """
  Return MxNx2 synapse matrix
  @param pre_population str|Population Population instance or string pointing a Population.
  @param post_population str|Population Population instance or string pointing a Population.
  @param connectivity str Description of how the presynaptic and postsynaptic populations are connected
  @param delay float Mean Axonal delay
  @param std float Standard Deviation of Axonal Delay (normal distribution)
  @parma scale float Scale all synapses by this amount.
  """
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
    synapses[:,:,0] = np.random.random([M,N]) * scale
  elif connectivity == "sparse-random":
    synapses = np.zeros([M,N,2])
    synapses[:,:,0] = np.random.random([M,N])
    syn_filter = (np.random.random([M,N]) < 0.1)#randomly filter out 90% of synapses, so only a 10th have weights
    synapses[:,:,0] *= syn_filter
    synapses[:,:,0] *= scale#use much smaller weights to decrease epileptic/rebounding behavior of network
  else:
    raise Exception("connectivity type not recognized! Check your spelling...")
  #we don't want neurons to recurrently excite themselves! so we set them to zero
  np.fill_diagonal(synapses[:,:,0],0)

  #generate appropriate distance matrices
  delays = generate_delay_matrix(N,M,delay=delay,std=std) #distance matrix
  return (synapses, delays)

def generate_delay_matrix(pre_population, post_population, delay=0.25, std=0.1):
  """generate delay matrix between two populations"""
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
  """
  Used to model repetition-driven effects of STDP. More repetitions results in stronger increase/decrease.
  """
  return 1.0/(1+np.exp(-0.2*M+10))

def stdp(time_diff, mode, A=0.01, tau=20):
  """
  STDP function
  @params time_diff ndarray Nx~200 matrix of time delays in spikes leading up to time i. Values are positive if time_diff came from spikes preceeding time i, and negative if following time i
  @returns delta_w ndarray Values will still need to be scaled according to how many times took place. Applied after stdp()
  """
  temp = np.copy(time_diff)#we don't want to modify the original!
  mask = (temp != 0)
  if mode == "LTP":
    temp[mask] = A * np.exp(-1 * temp[mask]/tau)
  elif mode == "LTD":
    temp[mask] = -A * np.exp(temp[mask]/(tau/2))#<--let's make LTD stronger than LTP and see what happens
  return temp
