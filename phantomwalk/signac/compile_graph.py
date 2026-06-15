#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import signac
import gsd, gsd.hoomd
import os

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
walltimes = []

for job in jobs:
    log = np.genfromtxt(job.fn("log.txt"), names=True)
    timestep = log["Simulationtimestep"]
    timesteps = np.append(timesteps, timestep)

    for variable in variables:
        variable_value = job.statepoint[variable]
        if variable in variables[0]:
            xs.append(variable_value)
        else:
            ys.append(variable_value)

    with open(job.fn("summary.txt"), 'r') as summary_file:
        summary = summary_file.read()
        if "total_time: " in summary:
            walltime = float(summary.split(" ")[1])
        else:
            walltime = 0
    walltimes = np.append(walltimes, walltime)

xs_sorted = np.sort(np.unique(xs))
ys_sorted = np.sort(np.unique(ys))
timesteps_sorted = np.sort(np.unique(timesteps))
walltimes_sorted = np.sort(np.unique(timesteps))

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

print(f"x_grid: {x_grid}")
print(f"y_grid: {y_grid}")
print(f"timestep_grid: {timestep_grid}")
print(f"walltime_grid: {walltime_grid}")

timestep_plot.plot_wireframe(x_grid, y_grid, timestep_grid)
walltime_plot.plot_wireframe(x_grid, y_grid, walltime_grid)

timestep_plot.set(zlabel="Timesteps", xlabel=f"{variables[0]}", ylabel=f"{variables[1]}")
walltime_plot.set(zlabel="Walltime (s)", xlabel=f"{variables[0]}", ylabel=f"{variables[1]}")

walltime_plot.set_zlim(zmax=1.5)

# plt.legend()

output_dir = "./time-plots"
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
# plt.savefig(f"{output_dir}/{variables[0]}-{variables[1]}.png")
plt.show()
