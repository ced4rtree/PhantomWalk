"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [10, 50, 100],
    "num_mon": [2,10,100],
    "density": [0.85,1.4],
    "k": [1000, 10000, 30000],
    "bond_l": [1.0],
    "r_cut": [1.0,1.1,1.2],
    "kT": [1.0],
    "A": [1000, 5000, 10000],
    "gamma": [500, 1000, 1500],
    "dt": [0.001, 0.002, 0.003],
    "particle_spacing": [1.1],
    "seed": [125,250]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
