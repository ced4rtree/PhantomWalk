"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [100,1000,10000],
    "num_mon": [2,100,500],
    "density": [0.85],
    "k": [15000,20000,25000],
    "bond_l": [1.0],
    "r_cut": [0.9,1.0,2.0],
    "kT": [0.5,1.0,3.0],
    "A": [500,1000,5000],
    "gamma": [200,800,1600],
    "dt": [0.01, 0.001, 0.0001],
    "particle_spacing": [1.1],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
