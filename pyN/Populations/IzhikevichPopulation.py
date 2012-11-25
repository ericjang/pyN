from Base_Population import Base_Population
import numpy as np
import ipdb as pdb

class IzhikevichPopulation(Base_Population):
  def __init__(self, name, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None, N=10, synapses=None, mode="Excitatory", tau_psc=5.0, connectivity=None, spike_delta=30):
    Base_Population.__init__(self, name, N, synapses, mode, tau_psc, connectivity, spike_delta, v0)
    self.a  = a
    self.b  = b
    self.c  = c
    self.d  = d
    self.v  = np.ones(self.N) * v0
    self.u  = np.ones(self.N) * u0 if u0 is not None else np.ones(self.N) * b*v0
    self.du = lambda a, b, v, u: a*(b*v - u)
    self.v_thresh = 30 #mV

  def update_state(self, i, T, t, dt):
    #compute v and adaptation resets
    print i
    prev_spiked = np.nonzero(self.spike_raster[:,i-1] == True)
    self.v[prev_spiked] = self.c
    self.u[prev_spiked] += self.d
    #compute deltas and apply to state variables
    dv = (0.04*self.v**2 + 5 * self.v + 140 - self.u + self.I_ext + self.I_rec)
    self.v += dv * dt
    self.u += dt * self.du(self.a, self.b, self.v, self.u)
    #decide whether to spike or not
    spiked = np.nonzero(self.v > self.v_thresh)
    self.v[spiked] = self.spike_delta
    self.spike_raster[spiked,i] = 1
    #update self.psc
    self.update_psc(i)
    #update synapses