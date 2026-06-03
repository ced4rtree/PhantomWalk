#!/usr/bin/env python3

import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    prog="Graph Generator",
    description="Generate graphs about the specified log file"
)

arg_names = [
    '--range-min',
    '--range-max',
    '--domain-min',
    '--domain-max',
    '--y-axis-key',
    '--y-axis-name',
    '--x-axis-key',
    '--x-axis-name',
    '--log-file'
]
for arg in arg_names:
    parser.add_argument(arg)

args = parser.parse_args()
print(f"ARGS: {args}")

log = np.genfromtxt(args.log_file, names=True)
x_axis = log[args.x_axis_key]
y_axis = log[args.y_axis_key]

plt.plot(x_axis[args.domain_min:args.domain_max], y_axis[args.range_min:args.range_max])
plt.xlabel(args.x_axis_name)
plt.ylabel(args.y_axis_name)
plt.legend()
plt.savefig("/bsuhome/cooperpiehl/phantom-graph.png")
