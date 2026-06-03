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
print('0')
x_axis = log[args.x_axis]
print('1')
y_axis = log[args.y_axis]
print('2')
plt.plot(x_axis[args.domain_min:args.domain_max])
print('3')
plt.plot(y_axis[args.range_min:args.range_max])
print('4')
plt.xlabel(args.x_axis_name)
print('5')
plt.ylabel(args.y_axis_name)
print('6')
plt.legend()
print('7')
plt.savefig("~/phantom-graph.png")
print('8')
