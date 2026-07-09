#!/usr/bin/env python3

"Specifically for generating data for one statistic in the ICUR 2026 poster."

import argparse
import os

import signac

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

def compute_data(run_number):
    try:
        num_pol = 1000
        num_mon = 1500

        write_freq = int(500)

        snap, closest, time, energy_per_part = create_system_dpd.create_polymer_system_dpd(
            num_pol = num_pol,
            num_mon = num_mon,
            density = 0.85,
            gsd_file_name = "poster.gsd",
            gsd_write_freq = write_freq,
            log_file_name = "poster.txt",
            log_write_freq = write_freq,
            k = 400000,
            bond_l = 1.0,
            r_cut = 1.0,
            kT = 1.0,
            A = 235000,
            gamma = 2500,
            dt = 0.001,
            sim_seed = 125,
            np_seed = 125,
            loop_timeout = 14400
        )
        with open('poster-summary.txt', 'a') as summary_file:
            summary_file.write(f'run {run_number},')
            summary_file.write(f'total_time: {time},')
            summary_file.write(f'closest particle radius: {closest}\n')
            summary_file.flush()
    except Exception as e: 
        with open('poster-summary.txt', 'a') as summary_file:
            summary_file.write(f'FAILURE of run {run_number}\n\n')
            summary_file.write(str(e))
            summary_file.flush()

if __name__ == '__main__':
    for i in range(5):
        compute_data(i)
