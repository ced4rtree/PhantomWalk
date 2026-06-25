#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import plotly
import plotly.graph_objects as go
import signac
import gsd, gsd.hoomd
import os
import math

# Value is the key used to index into the parameter dictionary
variables = sys.argv[1:]
assert len(variables) == 2

constants = {
    "num_pol": 100,
    "num_mon": 100,
    "density": 0.85,
    "k": 60000,
    "bond_l": 1.0,
    "r_cut": 1.0,
    "kT": 1.0,
    "A": 60000,
    "gamma": 2250,
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

xs = []
ys = []
walltimes = []
walltime_errs = []

NUM_RUNS = 5

for job in jobs:
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
        walltime_mean = 60 * 5 # 5 minute timout
        walltime_sem = 0
    walltimes = np.append(walltimes, walltime_mean)
    walltime_errs = np.append(walltime_errs, walltime_sem)

xs_sorted = np.sort(np.unique(xs))
ys_sorted = np.sort(np.unique(ys))

walltime_grid = np.zeros((len(ys_sorted), len(xs_sorted)))

for (x, y, z) in zip(xs, ys, walltimes):
    x_idx = np.where(xs_sorted == x)[0][0]
    y_idx = np.where(ys_sorted == y)[0][0]
    walltime_grid[y_idx][x_idx] = z

Z_UPPER_LIM=min([10, max(walltimes)])
Z_LOWER_LIM=min(walltimes)

fig = go.Figure(data=[go.Surface(z=walltime_grid, x=xs_sorted, y=ys_sorted)])
fig.update_layout(
    title=dict(text=f"Walltime (s) vs {variables[0]} & {variables[1]}"),
    scene = {
        "xaxis": {
            "title": f'{variables[0]}',
            "tickvals": xs_sorted
        },
        "yaxis": {
            "title": f'{variables[1]}',
            "tickvals": ys_sorted
        },
        "zaxis": {
            "title": 'Walltime (s)',
            "range": [Z_LOWER_LIM, Z_UPPER_LIM]
        }
    }
)
fig.update_traces(
    cmax=Z_UPPER_LIM,
    cmin=Z_LOWER_LIM
)
plotly.offline.plot(
    fig,
    auto_open=False,
    filename=f'time-plots/{variables[0]}-{variables[1]}.html'
)
