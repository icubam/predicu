import numpy as np
import os
import os.path as op

fig_path = './fig'
data_path = './data'
model_path = './model'

'''
s: Susceptible
e: Exposed
i: Infected
c: in intensive Care unit (with two sub-compartments: c1, c2)
x: eXit
'''
def compute_model_seir(pop, params, n_days):
    s0 = pop
    n_days_pre, alpha_e, beta, wei, wiout, wic, wcc, wcx = params
    s = [s0]
    e = [alpha_e*s0]
    i = [5]
    c1 = [0]
    c2 = [0]
    x = [0]
    n = s0
    n_days_pre = int(np.round(n_days_pre))
    for _ in range(n_days_pre+n_days-1):
        s.append(s[-1] - beta*e[-1]*s[-1]/n)
        e.append(e[-1] + beta*e[-1]*s[-1]/n - wei*e[-1])
        i.append(i[-1] + wei*e[-1] - wic*i[-1] - wiout*i[-1])
        c1.append(c1[-1] + wic*i[-1] - wcc*c1[-1])
        c2.append(c2[-1] + wcc*c1[-1] - wcx*c2[-1])
        x.append(x[-1] + wcx*c2[-1])
    return (np.array(c1[n_days_pre:])+np.array(c2[n_days_pre:]),
            np.array(x[n_days_pre:]))


# helpers
def make_dir(directory):
    if not op.exists(directory):
        os.makedirs(directory)
