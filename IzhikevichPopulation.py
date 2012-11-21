from Population import Population
import numpy as np
import ipdb as pdb

class IzhikevichPopulation(Population):
  def __init__(self, name, a=0.02, b=0.2, c=-65, d=6, v0=-70, u0=None, N=10, synapses=None, mode="Excitatory", tau_psc=5.0, connectivity=None, spike_delta=30):
    Population.__init__(self, name, N, synapses, mode, tau_psc, connectivity, spike_delta, v0)
    self.a  = np.ones(self.N) * a
    self.b  = np.ones(self.N) * b
    self.c  = np.ones(self.N) * c
    self.d  = np.ones(self.N) * d
    self.v  = np.ones(self.N) * v0
    self.u  = np.ones(self.N) * u0 if u0 is not None else np.ones(self.N) * b*v0
    self.du = lambda a, b, v, u: a*(b*v - u)
    self.v_thresh = 30 #mV

  def update_state(self, i, T, t, dt):
    #compute v and adaptation resets
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
    #if window is too big for current i or entire simulation, adjust i_to_dt.T accordingly
    window = self.integrate_window if i > self.integrate_window else i
    i_to_dt = self.i_to_dt if i > self.integrate_window else np.array([j*dt for j in reversed(range(1,window + 1))])
    #for any row (populations), get the -window previous entries all the way to the current one + 1 (for inclusivity)
    t_diff = self.spike_raster[:,i-window+1:i+1] * i_to_dt.T
    self.psc[:,i] = np.sum(t_diff * np.exp(-t_diff/self.tau_psc), axis=1)
