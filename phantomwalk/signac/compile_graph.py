#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import matplotlib
import matplotlib.transforms
import matplotlib.pyplot as plt
import signac
import gsd, gsd.hoomd
import os
import math

plt.rcParams.update({'font.size': 14})

# Value is the key used to index into the parameter dictionary
variables = ["k", "gamma"]

constants = {
    "num_pol": 100,
    "num_mon": 100,
    "density": 0.85,
    "k": 30000,
    "bond_l": 1.0,
    "r_cut": 1.0,
    "kT": 1.0,
    "A": 800,
    "gamma": 1250,
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
walltime_plot = fig.add_subplot(111, projection='3d')

xs = []
ys = []
walltimes = []
walltime_errs = []

NUM_RUNS = 5

for job in jobs:
    # if job.statepoint["A"] == 30000:
    #     continue
    xs.append(job.statepoint[variables[0]])
    ys.append(job.statepoint[variables[1]])

    with open(job.fn("summary.txt"), 'r') as summary_file:
        summary = summary_file.read()
        job_walltimes = [ txt.split(",")[1].split(' ')[1] for txt in summary.split('\n') if 'total_time' in txt ]
    job_walltimes = [ float(t) for t in job_walltimes ]
    if len(job_walltimes) > 0:
        walltime_mean = sum(job_walltimes)/len(job_walltimes)
        walltime_stddev = np.std(job_walltimes)
        walltime_sem = walltime_stddev / math.sqrt(len(job_walltimes))
    else:
        walltime_mean = 60 * 10 # 10 minute timout
        walltime_sem = 0
    walltimes = np.append(walltimes, walltime_mean)
    walltime_errs = np.append(walltime_errs, walltime_sem)

xs_sorted = np.sort(np.unique(xs))
ys_sorted = np.sort(np.unique(ys))
walltimes_sorted = np.sort(np.unique(walltimes))

grid_shape = (len(ys_sorted), len(xs_sorted))
x_grid = np.zeros(grid_shape)
y_grid = np.zeros(grid_shape)
walltime_grid = np.zeros(grid_shape)

for (x, y, z) in zip(xs, ys, walltimes):
    x_idx = np.where(xs_sorted == x)#[0][0]
    y_idx = np.where(ys_sorted == y)#[0][0]
    for val, grid in [(x, x_grid), (y, y_grid), (z, walltime_grid)]:
        grid[y_idx, x_idx] = val

walltime_plot.plot_wireframe(x_grid, y_grid, walltime_grid)

# NORM poster settings
# walltime_plot.set_zlabel("Walltime (s)", color='white')
# walltime_plot.set_xlabel(f"{variables[0]}", color='white', labelpad=7)
# walltime_plot.set_ylabel(f"{variables[1]}", color='white', labelpad=10)
# walltime_plot.set_yticks(ys)
# walltime_plot.set_yticklabels(ys, verticalalignment='baseline', horizontalalignment='left')
# walltime_plot.set_xticks(xs)
# walltime_plot.set_zticks([4, 5, 6])

# plt.style.use("dark_background")
# for axis in [walltime_plot.xaxis, walltime_plot.yaxis, walltime_plot.zaxis]:
#     [t.set_color('white') for t in axis.get_ticklines()]
#     [t.set_color('white') for t in axis.get_ticklabels()]

walltime_plot.errorbar(xs, ys, walltimes, zerr=walltime_errs, fmt='none', ecolor='r')

# walltime_plot.set_zlim(zmax=10)
# walltime_plot.set_zscale('log')
# walltime_plot.set_xlim(xmin=800, xmax=1500)

output_dir = "./time-plots"
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
plt.savefig(f"{output_dir}/{variables[0]}-{variables[1]}.png", dpi=700, transparent=True)
# plt.show()
