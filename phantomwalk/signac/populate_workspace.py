"""Populate the workspace."""

import signac

import itertools

project = signac.get_project()

parameters = {
    "num_pol": [100,500,1000,10000],
    "num_mon": [500],
    "density": [0.85],
    "k": [15000,20000,25000],
    "bond_l": [1.0],
    "r_cut": [0.9,1.0,1.8,2.5],
    "kT": [0.5,1.0,3.0],
    "A": [500,1000,5000,10000],
    "gamma": [200,400,1000,2000],
    "dt": [0.01, 0.001, 0.0001],
    "particle_spacing": [1.1],
    "seed": [35,125,240]
}

keys, values = zip(*parameters.items())
for v in itertools.product(*values):
    experiment = dict(zip(keys, v))
    job = project.open_job(experiment).init()
