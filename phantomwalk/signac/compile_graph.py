#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import signac
import gsd, gsd.hoomd
import os

# Value is the key used to index into the parameter dictionary
variable = "dt"

constants = {
    "num_pol": 100,
    "num_mon": 100,
    "density": 0.85,
    "k": 10000,
    "bond_l": 1.0,
    "r_cut": 1.0,
    "kT": 1.0,
    "A": 5000,
    "gamma": 1000,
    "dt": 0.001,
    "seed": 125,
}
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

fig, [timestep_plot, walltime_plot] = plt.subplots(1, 2)

for job in jobs:
    log = np.genfromtxt(job.fn("log.txt"), names=True)
    timesteps = log["Simulationtimestep"]

    traj = gsd.hoomd.open(job.fn("trajectory.gsd"), 'r')
    num_particles = traj[0].particles.N

    variable_value = job.statepoint[variable]
    point_label = f"{variable}: {variable_value}"

    timestep_plot.plot(variable_value, timesteps[-1], 'o', label=point_label)

    with open(job.fn("summary.txt"), 'r') as summary_file:
        summary = summary_file.read()
        if "total_time: " in summary:
            walltime = float(summary.split(" ")[1])
        else:
            continue

    walltime_plot.plot(variable_value, walltime, 'o', label=point_label)
timestep_plot.set(ylabel="Timesteps", xlabel=f"{variable}")
walltime_plot.set(ylabel="Walltime (s)", xlabel=f"{variable}")

plt.legend(loc='upper right')

output_dir = "./time-plots"
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
plt.savefig(f"{output_dir}/{variable}.png")
