#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import os
import subprocess
import sys

BORAH_USERNAME = "cooperpiehl"

@dataclass
class Parameter:
    name: str
    values: [float]

parameters = []

# read parameters from populate_workspace.py and use those as arguments to this script
with open("../populate_workspace.py", 'r') as parameters_file:
    parameters_file_txt = parameters_file.read()
    start_parameters_dict = parameters_file_txt.find("# BEGIN PARAMETERS")
    end_parameters_dict = parameters_file_txt.find("# END PARAMETERS")
    parameters_dict_txt = parameters_file_txt[start_parameters_dict:end_parameters_dict]

    # `1:-1` is to get rid of "# BEGIN PARAMETERS" and "# END PARAMETERS"
    parameters_dict_lines = parameters_dict_txt.splitlines()[1:-1]
    for line in parameters_dict_lines:
        split_param = line.strip(' ,').split(": ")
        name = split_param[0].strip('\"')
        values = eval(split_param[1])
        parameters.append(Parameter(name=name, values=values))

parser = argparse.ArgumentParser(
    prog='Data Parser',
    description='Parse data from Borah using the local parameters in populate_workspace.py'
)

for param in parameters:
    parser.add_argument(f'--{param.name}')

args = parser.parse_args()

# exit early if any values are not correct
failed_values = []
for key, value in zip(args.__dict__.keys(), args.__dict__.values()):
    param = list(filter(lambda arg: arg.name == key, parameters))[0]
    value_str = f'{value}'
    if value_str == 'None' or float(value_str) not in param.values:
        failed_values.append(f"<p>Error: value {key} is {value}. Expected one of {param.values}</p>")

if len(failed_values) > 0:
    print("\n".join(failed_values))
    sys.exit()

# Handle errors in running commands for us, exiting early with some info about
# the failed process
def run_cmd(cmd):
    cmd_data = subprocess.run(cmd, capture_output=True)
    print(f"CMD STDOUT: {cmd_data.stdout.decode('utf-8')}")
    print(f"CMD STDERR: {cmd_data.stderr.decode('utf-8')}")

    if cmd_data.returncode != 0:
        print(f"""<p>
Failed to run <code>{' '.join(cmd_data.args)}</code> on the Borah cluster.
Process exited with return code {cmd_data.returncode}.

Process stdout:
<pre>
{cmd_data.stdout.decode('utf-8')}
</pre>

Process stderr:
<pre>
{cmd_data.stderr.decode('utf-8')}
</pre>
        </p>""")
        sys.exit()

log_file = "".join([
    f"/bsuhome/{BORAH_USERNAME}/scratch/PhantomWalk/phantomwalk/signac/view/"
    f"A/{args.A}/"
    f"dt/{args.dt}/"
    f"gamma/{args.gamma}/"
    f"k/{args.k}/"
    f"kT/{args.kT}/"
    f"num_mon/{args.num_mon}/"
    f"num_pol/{args.num_pol}/"
    f"r_cut/{args.r_cut}/"
    "job/log.txt"
])
gen_graph_cmd = " ".join([
    "conda activate phantomwalk-dev &&",
    f"python /bsuhome/{BORAH_USERNAME}/scratch/PhantomWalk/phantomwalk/signac/data_parser/gen_graph.py",
    "--y-axis-key mdcomputeThermodynamicQuantitiespotential_energy",
    "--y-axis-name Potential\\ Energy",
    "--x-axis-key Simulationtimestep",
    "--x-axis-name Timestep",
    f"--log-file {log_file}"
])
borah_gen_graph_cmd = ["ssh", "-C", f"{BORAH_USERNAME}@borah-login.boisestate.edu", f"{gen_graph_cmd}"]
run_cmd(borah_gen_graph_cmd)

GRAPH_FILE_NAME = "phantom-graph.png"

# grab the image from borah and bring it onto this computer
run_cmd(f"scp {BORAH_USERNAME}@borah-login.boisestate.edu:~/{GRAPH_FILE_NAME} .".split())

print(f"<img src=\"{os.getcwd()}/{GRAPH_FILE_NAME}\">")
