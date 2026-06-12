"""Compute phantom walk data and output to file."""

import argparse
import os

import signac

import freud
import gsd.hoomd

import importlib.machinery
import importlib.util

import multiprocessing

import numpy as np
import math
import matplotlib.pyplot as plt

from phantomwalk.lib import create_system_dpd

import contextlib
import sys

GSD_FILE = 'trajectory.gsd'
LOG_FILE = 'log.txt'
SUMMARY_FILE = 'summary.txt'

POTENTIAL_ENERGY_GRAPH = 'pe.svg'

RDF_FILE = 'rdf.svg'

def stringify_statepoints(job):
    ret = ""
    for key, value in job.cached_statepoint.items():
        ret += f"{key} = {value}, "
    ret = ret[:-2] # remove trailing ', '
    return ret

def fail_svg(fn, msg):
    with open(fn, 'w') as fail_file:
        fail_file.write('<svg height="30" width="200" xmlns="http://www.w3.org/2000/svg">')
        fail_file.write(f'<text x="5" y="15" fill="red">{msg}</text>')
        fail_file.write('</svg>')
        fail_file.flush()

def rdf(job):
    "Output a graph of the radial distribution function for the last 3 frames"
    if job.isfile(RDF_FILE):
        return

    try:
        traj = gsd.hoomd.open(job.fn(GSD_FILE), 'r')
        # Get the smallest box length for calculating our r_max.
        # Minimum shouldn't matter since this is a cube, but good practice
        box_l = min(traj[-1].configuration.box[0:3])
    except (FileNotFoundError, IndexError) as e:
        fail_svg(job.fn(RDF_FILE), f'Failed to read trajectory.gsd!\n{e}')
        return
    r_max = min(box_l/2 - 0.01, 3.0)
    # raise RuntimeError(f"BOX_L: {box_l}")

    rdf = freud.density.RDF(bins=400, r_max=r_max)
    for frame in traj[-1:]:
        rdf.compute(frame, reset=False)

    fig, ax = plt.subplots()
    rdf.plot(ax=ax)
    plt.savefig(job.fn(RDF_FILE))

def potential_energy_graph(job):
    "Output a graph of potential energy per particle vs. timestep"
    if job.isfile(POTENTIAL_ENERGY_GRAPH):
        return

    try:
        log = np.genfromtxt(job.fn('log.txt'), names=True)
    except (FileNotFoundError, IndexError) as e:
        # Exit since the log doesn't exist
        fail_svg(job.fn(POTENTIAL_ENERGY_GRAPH), f'Failed to read log.txt!\n{e}')
        return

    num_pol = job.cached_statepoint['num_pol']
    num_mon = job.cached_statepoint['num_mon']
    num_particles = num_pol * num_mon

    try:
        x_axis = log["Simulationtimestep"]
        y_axis = log["mdcomputeThermodynamicQuantitiespotential_energy"]/num_particles
    except IndexError:
        fail_svg(job.fn(POTENTIAL_ENERGY_GRAPH))

    plt.plot(x_axis, y_axis)

    axes = plt.gca()

    # None values are here mainly for convenience later down the line
    axes.set_xlim([None, None])
    axes.set_ylim([0, 200])

    plt.xlabel("Timestep")
    plt.ylabel("Potential Energy Per Particle")
    plt.savefig(job.fn(POTENTIAL_ENERGY_GRAPH))
    plt.clf()

def redirect_output(action, job):
    with contextlib.redirect_stderr(sys.stdout):
        with contextlib.redirect_stdout(open(job.fn(f'output.txt'), 'w')):
            action(job)

def compute_data(job):
    redirect_output(compute_data_internal, job)

def compute_data_internal(job):
    """Initializes each system, allows it to equilibrate, and writes out the
    resulting data."""

    with open(job.fn("output.txt"), 'w') as sys.stdout:
        print(f"Processing with {stringify_statepoints(job)}")
        # skip computation if log files are already present
        if job.isfile(SUMMARY_FILE):
            return

        try:
            num_pol = job.cached_statepoint['num_pol']
            num_mon = job.cached_statepoint['num_mon']

            # bigger sims take much longer, so writing should happen in proportion
            # with the system size to prevent writing a crazy large log file.
            write_freq = int(50)

            snap, time = create_system_dpd.create_polymer_system_dpd(
                num_pol = num_pol,
                num_mon = num_mon,
                density = job.cached_statepoint['density'],
                gsd_file_name = job.fn(GSD_FILE),
                gsd_write_freq = write_freq,
                log_file_name = job.fn(LOG_FILE),
                log_write_freq = write_freq,
                k = job.cached_statepoint['k'],
                bond_l = job.cached_statepoint['bond_l'],
                r_cut = job.cached_statepoint['r_cut'],
                kT = job.cached_statepoint['kT'],
                A = job.cached_statepoint['A'],
                gamma = job.cached_statepoint['gamma'],
                dt = job.cached_statepoint['dt'],
                sim_seed = job.cached_statepoint['seed'],
                np_seed = job.cached_statepoint['seed'],
                loop_timeout = 60 * 20 # 20 minutes
            )
            with open(job.fn(SUMMARY_FILE), 'w') as summary_file:
                summary_file.write(f'total_time: {time}\n')
                summary_file.flush()
        except Exception as e: 
            with open(job.fn(SUMMARY_FILE), 'w') as summary_file:
                summary_file.write('FAILURE\n\n')
                summary_file.write(str(e))
                summary_file.flush()

def run_jobs(action, *jobs):
    """Process any number of jobs in parallel with the multiprocessing package."""
    processes = int(os.environ.get('ACTION_THREADS_PER_PROCESS', multiprocessing.cpu_count()))
    if hasattr(os, 'sched_getaffinity'):
        processes = len(os.sched_getaffinity(0))

    if len(jobs) < processes:
        processes = len(jobs)

    print(f"Num processes: {processes}")
    print(f"Jobs: {list(map(lambda job: job._id, jobs))}")

    with multiprocessing.Pool(processes=processes) as p:
        p.map(action, jobs)

if __name__ == '__main__':
    # Parse the command line arguments: python action.py --action ACTION [DIRECTORIES]
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True)
    parser.add_argument('directories', nargs='+')
    args = parser.parse_args()

    # Open the signac jobs
    project = signac.get_project()
    jobs = [project.open_job(id=directory) for directory in args.directories]

    # Call the action
    run_jobs(globals()[args.action], *jobs)
