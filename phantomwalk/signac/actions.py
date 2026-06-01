"""Compute phantom walk data and output to file."""

import argparse
import os

import signac

import importlib.machinery
import importlib.util

import mpi4py.MPI

import sys
sys.path.append('../src')

import create_system_dpd

GSD_FILE = 'trajectory.gsd'
LOG_FILE = 'log.txt'
SUMMARY_FILE = 'summary.txt'

def stringify_statepoints(job):
    ret = ""
    for key, value in job.cached_statepoint.items():
        ret += f"{key} = {value}, "
    ret = ret[:-2] # remove trailing ', '
    return ret

def compute_data(job):
    """Initializes each system, allows it to equilibrate, and writes out the
    resulting data."""

    print(f"Processing with {stringify_statepoints(job)}")
    # skip computation if log files are already present
    if job.isfile(SUMMARY_FILE):
        return

    try:
        build_time, total_time, timesteps = create_system_dpd.create_polymer_system_dpd(
            num_pol = job.cached_statepoint['num_pol'],
            num_mon = job.cached_statepoint['num_mon'],
            density = job.cached_statepoint['density'],
            gsd_file_name = job.fn(GSD_FILE),
            log_file_name = job.fn(LOG_FILE),
            k = job.cached_statepoint['k'],
            bond_l = job.cached_statepoint['bond_l'],
            r_cut = job.cached_statepoint['r_cut'],
            kT = job.cached_statepoint['kT'],
            A = job.cached_statepoint['A'],
            gamma = job.cached_statepoint['gamma'],
            dt = job.cached_statepoint['dt'],
            particle_spacing = job.cached_statepoint['particle_spacing'],
            sim_seed = job.cached_statepoint['seed'],
        )
        with open(job.fn(SUMMARY_FILE), 'w') as summary_file:
            summary_file.write(f'build_time: {build_time}\n')
            summary_file.write(f'total_time: {total_time}\n')
            summary_file.write(f'timesteps: {timesteps}\n')
            summary_file.flush()
    except Exception as e: 
        with open(job.fn(SUMMARY_FILE), 'w') as summary_file:
            summary_file.write('FAILURE\n\n')
            summary_file.write(str(e))
            summary_file.flush()

def run_jobs(*jobs):
    "Run jobs in parallel."
    num_ranks = mpi4py.MPI.COMM_WORLD.Get_size()
    num_jobs = len(jobs)
    if num_ranks != num_jobs:
        raise RuntimeError(f"Numer of ranks ({num_ranks}) does not match number of job directories. ({num_jobs})")

    rank = mpi4py.MPI.COMM_WORLD.Get_rank()
    compute_data(jobs[rank])

if __name__ == '__main__':
    # Parse the command line arguments: python action.py [DIRECTORIES]
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True)
    parser.add_argument('directories', nargs='+')
    args = parser.parse_args()

    # Open the signac jobs
    project = signac.get_project()
    jobs = [project.open_job(id=directory) for directory in args.directories]

    # Call the action
    globals()[args.action](*jobs)
