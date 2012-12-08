from Base_Population import Base_Population
import numpy as np

class HHPopulation(Base_Population):
  """
  Hogdkin-Huxley Population Class. Still a work-in-progress
  """
  def __init__(self, name, N=1, synapses=None, mode="Excitatory", tau_psc=5.0, connectivity=None, spike_delta=30):
    Base_Population.__init__(self, name, N, synapses, mode, tau_psc, connectivity, spike_delta, v_reset)
    ## Functions
    # K channel
    self.alpha_n = np.vectorize(lambda v: 0.01*(-v + 10)/(exp((-v + 10)/10) - 1) if v != 10 else 0.1)
    self.beta_n  = lambda v: 0.125*np.exp(-v/80)
    self.n_inf   = lambda v: alpha_n(v)/(alpha_n(v) + beta_n(v))
    # Na channel (activating)
    self.alpha_m = vectorize(lambda v: 0.1*(-v + 25)/(np.exp((-v + 25)/10) - 1) if v != 25 else 1)
    self.beta_m  = lambda v: 4*np.exp(-v/18)
    self.m_inf   = lambda v: alpha_m(v)/(alpha_m(v) + beta_m(v))
    # Na channel (inactivating)
    self.alpha_h = lambda v: 0.07*np.exp(-v/20)
    self.beta_h  = lambda v: 1/(np.exp((-v + 30)/10) + 1)
    self.h_inf   = lambda v: alpha_h(v)/(alpha_h(v) + beta_h(v))


    ## HH Parameters
    self.V_rest  = 0      # mV
    self.Cm      = 1      # uF/cm2
    self.gbar_Na = 120    # mS/cm2
    self.gbar_K  = 36     # mS/cm2
    self.gbar_l  = 0.3    # mS/cm2
    self.E_Na    = 115    # mV
    self.E_K     = -12    # mV
    self.E_l     = 10.613 # mV
    self.
    self.Vm      = zeros(len(time)) # mV
    self.Vm[0]   = V_rest
    self.m       = m_inf(V_rest)
    self.h       = h_inf(V_rest)
    self.n       = n_inf(V_rest)

  def update_state(self, i, T, t, dt):
    #compute v and adaptation resets. No such thing as 'spike raster?'
    g_Na = gbar_Na*(self.m**3)*self.h
    g_K  = gbar_K*(self.n**4)
    g_l  = gbar_l

    m += dt*(self.alpha_m(self.Vm[i-1])*(1 - self.m) - self.beta_m(self.Vm[i-1])*self.m)
    h += dt*(self.alpha_h(self.Vm[i-1])*(1 - self.h) - self.beta_h(self.Vm[i-1])*self.h)
    n += dt*(self.alpha_n(self.Vm[i-1])*(1 - self.n) - self.beta_n(self.Vm[i-1])*self.n)

    self.Vm[i] += (I[i-1] - g_Na*(Vm[i-1] - E_Na) - g_K*(Vm[i-1] - E_K) - self.g_l*(self.Vm[i-1] - E_l)) / self.Cm * dt

    #self.update_psc(i, dt)
