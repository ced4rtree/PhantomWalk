#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import gsd

args = ' '.join(sys.argv[1:])

# Should probably use the signac python api, but it's way easier to do this
# since `signac find` interprets simplified syntax automatically.
# Side note: I hate python so much. I am not allowed to format this line to be
# prettier unless I split it into a million variables
dirs = subprocess.run(f"signac find {args}".split(), capture_output=True).stdout.decode('utf-8').split()

fig, [timestep_plot, walltime_plot] = plt.subplots(1, 2, sharey=True)

for dire in dirs:
    log = np.genfromtxt(f"workspace/{dire}/log.txt", names=True)
    timesteps = log["Simulationtimestep"]
    potential_energy = log["mdcomputeThermodynamicQuantitiespotential_energy"]

    traj = gsd.open(f"workspace/{dire}/trajectory.gsd", 'r')
    num_particles = traj[0].particles.N

    scaled_energy = potential_energy/num_particles

    timestep_plot.plot(timesteps, scaled_energy, label=dire)

    with open(f"workspace/{dire}/summary.txt") as summary_file:
        summary = summary_file.read()
        if "total_time: " in summary:
            walltime = summary.split(" ")[1]
        else:
            break

    walltime_plot.plot(walltime, scaled_energy, label=dire)
walltime_plot.ylabel("Potential Energy Per Particle")
timestep_plot.ylabel("Potential Energy Per Particle")
walltime_plot.xlabel("Walltime (s)")
timestep_plot.xlabel("Timesteps")
