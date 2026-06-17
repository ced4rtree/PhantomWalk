"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [100,1000],
    "num_mon": [50,100],
    "density": [0.85],
    "k": [10000, 30000, 50000],
    "bond_l": [1.0],
    "r_cut": [1.0],
    "kT": [1.0],
    "A": [300, 500, 800, 1000],
    "gamma": [1500, 2000, 2500],
    "dt": [0.001, 0.002],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
