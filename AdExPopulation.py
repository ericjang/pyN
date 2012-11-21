from Population import Population
from synapse import *

class AdExPopulation(Population):
  def __init__(self, name, N=10, synapses=None, mode="Excitatory", cm=0.281, tau_psc=-5.0, tau_refrac=0.1, v_spike=-40.0, v_reset=-70.6, v_rest=-70.6, tau_m=9.3667, i_offset=0.0, a=4.0, b=0.0805, delta_T=2.0,tau_w=144.0,v_thresh=-50.4,e_rev_E=0.0, tau_syn_E=5.0, e_rev_I=-80.0, tau_syn_I=5.0, connectivity=None):
    '''
    static network of AdEx Neurons. Performs no
    '''
    self.name = name
    self.N         = N           # Number of neurons in population
    # other variables (traces) can be conveniently set up during simulation...
    self.receiver = [] #stored list of synapse weight matrices from other populations
    '''
    configure neuron parameters
    '''
    self.mode       = mode       # EPSP or IPSP
    self.cm         = cm         # Capacitance of the membrane in nF
    self.tau_refrac = tau_refrac # Duration of refractory period in ms.
    self.v_spike    = v_spike    # Spike detection threshold in mV.
    self.v_reset    = v_reset    # Reset value for V_m after a spike. In mV.
    self.v_rest     = v_rest     # Resting membrane potential (Leak reversal potential) in mV.
    self.tau_m      = tau_m      # Membrane time constant in ms
    self.i_offset   = i_offset   # Offset current in nA
    self.a          = a          # Subthreshold adaptation conductance in nS.
    self.b          = b          # Spike-triggered adaptation in nA
    self.delta_T    = delta_T    # Slope factor in mV
    self.tau_w      = tau_w      # Adaptation time constant in ms
    self.v_thresh   = v_thresh   # Spike initiation threshold in mV
    self.e_rev_E    = e_rev_E    # Excitatory reversal potential in mV.
    self.tau_syn_E  = tau_syn_E  # Decay time constant of excitatory synaptic conductance in ms.
    self.e_rev_I    = e_rev_I    # Inhibitory reversal potential in mV.
    self.tau_syn_I  = tau_syn_I  # Decay time constant of the inhibitory synaptic conductance in ms.
    '''
    state variables for each population
    The system is memoryless so there is no need to recall more than one previous value
    '''
    self.I_inj = None#no injection current yet
    self.v = np.ones(N) * v_rest
    self.ge = np.ones(N)
    self.gi = np.ones(N)
    self.gl = 0.9#? leak conductance - will this work?
    self.w = np.ones(N)
    self.prev_spiked = (np.zeros(N) == 1) #boolean array
    self.last_spike = np.zeros(N)
    self.spike_raster = np.zeros(N) * np.nan
    '''
    configure synapses
    '''
    if (synapses == None and connectivity == None):
      print 'generating empty connectivity'
      self.synapses = generate_synapses(N,N,connectivity="none")
    elif connectivity != None:
      print 'generating connectivity = ', connectivity
      #connectivity is when you want to pass a high-level string that automatically generates the synapses.
      self.synapses = generate_synapses(N,N,connectivity=connectivity)
    elif (N == synapses.shape[0] == synapses.shape[1]):
      print 'using user-defined synapses'
      #if user created their own synapses, then check to make sure it is ok
      self.synapses = synapses
    else:
      raise Exception("Synapse matrix wrong dimensions!")
  #configure EPSP or IPSPs
  def Isyn(self,t):
    '''
    Excitatory or Inhibitory postsynaptic current model
    - t is an array of every neuron's last spike time
    - returns current beginning at that last spike time
    - e.g. if a neuron fires at time 1 but not at time 2, the decaying current from time 1 will still be applied
    '''
    t[np.nonzero(t < 0)] = 0
    #in order for a good modicum of current to even be applied, t must be negative!
    if self.mode == "Excitatory": return t*np.exp(-t/self.tau_syn_E)
    elif self.mode == "Inhibitory": return -t*np.exp(-t/self.tau_syn_I)
  def update(dt=0.125):
    #if prev_spiked for a neuron, then it becomes v_reset
    p.v[np.nonzero(p.prev_spiked == True)] = p.v_reset
    #compute current input from neurons within population as well as neurons from other populations
    #a better idea would have been to have rows be presynaptic and columns be postsynaptic. but this transpose scheme should work.
    p.I_proj = np.transpose(np.transpose(p.synapses).dot(p.Isyn(t - p.last_spike))) #intra-population currents
    #add currents from other populations that project to p (interpopulation)
    for proj in p.receiver:
      proj_last_spike = self.populations[proj['from']].last_spike
      #unlike the neurdon example, I am using transposed version of connectivity matrix. that was not a good idea
      p.I_proj += np.transpose(np.transpose(proj['syn']).dot(self.populations[proj['from']].Isyn(t-proj_last_spike)))
    #compute deltas
    #dv  = (((p.v_rest-p.v) + p.delta_T*np.exp((p.v - p.v_thresh)/p.delta_T))/p.tau_m + (p.ge*(p.e_rev_E-p.v) + p.gi*(p.e_rev_I-p.v) + p.i_offset + p.I_inj[:,i] + p.I_proj - p.w)/p.cm) *dt
    dv  = (((p.v_rest-p.v) + p.delta_T*np.exp((p.v - p.v_thresh)/p.delta_T))/p.tau_m + (p.i_offset + p.I_inj[:,i] + p.I_proj - p.w)/p.cm) *dt
    dge = -p.ge/p.tau_syn_E * dt
    dgi = -p.gi/p.tau_syn_I * dt
    #dv = p.gl * ((p.delta_T*np.exp((p.v - p.v_thresh)/p.delta_T) - (p.v -p.v_rest)) - p.w + p.I_inj[:,i] + p.I_proj)/p.cm * dt
    dw  = (p.a*(p.v-p.v_rest) - p.w)/p.tau_w * dt

    p.ge += dge
    p.gi += dgi
    p.v += dv
    p.w += dw

    #detect spike thresholds
    spiked = np.nonzero(p.v >= p.v_thresh)
    no_spike = np.nonzero(p.v < p.v_thresh)
    p.v[spiked] += spike_delta
    p.w[spiked] += p.b #adjust adaptation weight
    p.last_spike[spiked] = t #spiked now!
    p.prev_spiked[spiked] = True
    p.prev_spiked[no_spike] = False

    #for the raster
    p.spike_status = np.zeros(p.N) * np.nan
    p.spike_status[spiked] = spiked[0] + 1