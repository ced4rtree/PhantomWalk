"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [100,1000],
    "num_mon": [50,100],
    "density": [0.85],
    "k": [20000, 30000, 40000],
    "bond_l": [1.0],
    "r_cut": [1.0],
    "kT": [1.0],
    "A": [800, 1000, 1200, 30000], # 30000 is just for you, eric <3
    "gamma": [1000, 1250, 1500],
    "dt": [0.001, 0.0015],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
