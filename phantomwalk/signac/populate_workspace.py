"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [100],
    "num_mon": [100],
    "density": [0.85],
    "k": [20000, 30000, 40000, 50000, 60000],
    "bond_l": [1.0],
    "r_cut": [1.0],
    "kT": [1.0],
    "A": [20000, 30000, 40000, 50000, 60000], # 30000 is just for you, eric <3
    "gamma": [500, 750, 1000, 1250, 1500, 1750, 2000],
    "dt": [0.001],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
