#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import signac
import gsd, gsd.hoomd
import os
import math

# Value is the key used to index into the parameter dictionary
variables = ["A", "k"]

constants = {
    "num_pol": 100,
    "num_mon": 100,
    "density": 0.85,
    "k": 1000,
    "bond_l": 1.0,
    "r_cut": 1.0,
    "kT": 1.0,
    "A": 5000,
    "gamma": 1000,
    "dt": 0.001,
    "seed": 125,
}

for variable in variables:
    if variable in constants:
        del constants[variable]
    else:
        raise RuntimeError(f"Specified variable {variable} not in parameter set!")

def fmt_dict(diction, signac=True):
    ret = ""
    for key, val in diction.items():
        if signac:
            ret += f"{key} {val}"
        else:
            ret += f"{key}: {val}, "
    if not signac:
        ret = ret[:-2]
    return ret

project = signac.Project()
jobs = project.find_jobs(constants)

fig = plt.figure()
timestep_plot = fig.add_subplot(121, projection='3d')
walltime_plot = fig.add_subplot(122, projection='3d')

xs = []
ys = []
timesteps = []
timestep_errs = []
walltimes = []
walltime_errs = []

NUM_RUNS = 5

for job in jobs:
    # get the average timestep
    job_timesteps = []
    for i in range(NUM_RUNS):
        log = np.genfromtxt(job.fn(f"log-{i}.txt"), names=True)
        job_timesteps.append(log["Simulationtimestep"][-1])
    timestep_mean = sum(job_timesteps)/len(job_timesteps)
    timestep_stddev = np.std(job_timesteps)
    timestep_sem = timestep_stddev / math.sqrt(len(job_timesteps))
    timesteps = np.append(timesteps, timestep_mean)
    timestep_errs = np.append(timestep_errs, timestep_sem)

    for variable in variables:
        variable_value = job.statepoint[variable]
        if variable in variables[0]:
            xs.append(variable_value)
        else:
            ys.append(variable_value)

    with open(job.fn("summary.txt"), 'r') as summary_file:
        summary = summary_file.read()
        job_walltimes = [ txt.split(" ")[1] for txt in summary.split('\n') if 'total_time' in txt ]
    job_walltimes = [ float(t) for t in job_walltimes ]
    walltime_mean = sum(job_walltimes)/len(job_walltimes)
    walltime_stddev = np.std(job_walltimes)
    walltime_sem = walltime_stddev / math.sqrt(len(job_walltimes))
    walltimes = np.append(walltimes, walltime_mean)
    walltime_errs = np.append(walltime_errs, walltime_sem)

xs_sorted = np.sort(np.unique(xs))
ys_sorted = np.sort(np.unique(ys))
timesteps_sorted = np.sort(np.unique(timesteps))
walltimes_sorted = np.sort(np.unique(walltimes))

grid_shape = (len(xs_sorted), len(ys_sorted))
x_grid = np.zeros(grid_shape)
y_grid = np.zeros(grid_shape)
timestep_grid = np.zeros(grid_shape)
walltime_grid = np.zeros(grid_shape)

for zs, z_grid in [(timesteps, timestep_grid), (walltimes, walltime_grid)]:
    for (x, y, z) in zip(xs, ys, zs):
        x_idx = np.where(xs_sorted == x)
        y_idx = np.where(ys_sorted == y)
        for val, grid in [(x, x_grid), (y, y_grid), (z, z_grid)]:
            grid[y_idx, x_idx] = val

timestep_plot.plot_wireframe(x_grid, y_grid, timestep_grid)
walltime_plot.plot_wireframe(x_grid, y_grid, walltime_grid)

timestep_plot.set(zlabel="Timesteps", xlabel=f"{variables[0]}", ylabel=f"{variables[1]}")
walltime_plot.set(zlabel="Walltime (s)", xlabel=f"{variables[0]}", ylabel=f"{variables[1]}")

timestep_plot.errorbar(xs, ys, timesteps, zerr=timestep_errs, fmt='none', ecolor='r')
walltime_plot.errorbar(xs, ys, walltimes, zerr=walltime_errs, fmt='none', ecolor='r')

# walltime_plot.set_zlim(zmax=1.5)

# plt.legend()

output_dir = "./time-plots"
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
plt.savefig(f"{output_dir}/{variables[0]}-{variables[1]}.png")
