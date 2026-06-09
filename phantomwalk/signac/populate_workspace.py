"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    # BEGIN PARAMETERS
    "num_pol": [50, 100, 500],
    "num_mon": [2,10,100,500],
    "density": [0.85],
    "k": [20000,21250,22500,23750,25000],
    "bond_l": [1.0],
    "r_cut": [1.0,1.1,1.2],
    "kT": [2.0,3.0,4.0],
    "A": [4000,5000,6000],
    "gamma": [600,800,1000],
    "dt": [0.001],
    "particle_spacing": [1.1],
    "seed": [125]
    # END PARAMETERS
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
