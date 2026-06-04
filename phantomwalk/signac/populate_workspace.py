"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [100,1000,10000],
    "num_mon": [2,100,500],
    "density": [0.85],
    "k": [20000,22500,25000],
    "bond_l": [1.0],
    "r_cut": [0.9,1.0,1.2],
    "kT": [2.0,3.0,4.0],
    "A": [1000,5000,7500,10000],
    "gamma": [800],
    "dt": [0.001],
    "particle_spacing": [1.1],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
