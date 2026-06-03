#!/usr/bin/env python3

import argparse
import cgi
from dataclasses import dataclass
import os
import subprocess
import sys

BORAH_USERNAME = "cooperpiehl"
GRAPH_FILE_NAME = "phantom-graph.png"

user_input = cgi.FieldStorage()

# Used for bailing early if the form responses have been read before user has
# had the chance to do anything
exit_after_form = False

def is_checked(name, value):
    return 'checked' if user_input.getfirst(name) == value else ''

def get_input_val(key):
    ret = user_input.getvalue(key)

    if ret == None:
        exit_after_form = True
        return ''

    if ret == '':
        return None

    ret = ret.replace('\\', '')
    ret = ret.replace(' ', '\\ ')

    return ret

print("Content-Type: text/html")
print(f"""
<!DOCTYPE html>
<html lang="en">
  <body>
    <h1>Borah Data Parser</h1>
    <form>
      X Axis Key: <input type="text" name="x_axis_key" value="{get_input_val('x_axis_key')}">
      <br>
      X Axis Name: <input type="text" name="x_axis_name" value="{get_input_val('x_axis_name')}">
      <br>

      Y Axis Key: <input type="text" name="y_axis_key" value="{get_input_val('y_axis_key')}">
      <br>
      Y Axis Name: <input type="text" name="y_axis_name" value="{get_input_val('y_axis_name')}">
      <br>

      Domain Min: <input placeholder="optional" type="text" name="domain_min" value="{get_input_val('domain_min')}">
      <br>
      Domain Max: <input placeholder="optional" type="text" name="domain_max" value="{get_input_val('domain_max')}">
      <br>

      Range Min: <input placeholder="optional" type="text" name="range_min" value="{get_input_val('range_min')}">
      <br>
      Range Min: <input placeholder="optional" type="text" name="range_max" value="{get_input_val('range_max')}">
      <br>

      Number of Polymers:
      <input type="radio" name="num_pol" value="100" {is_checked('num_pol', '100')}> 100
      <input type="radio" name="num_pol" value="1000" {is_checked('num_pol', '1000')}> 1000
      <input type="radio" name="num_pol" value="10000" {is_checked('num_pol', '10000')}> 10000
      <br>

      Number of Monomers:
      <input type="radio" name="num_mon" value="2" {is_checked('num_mon', '2')}> 2
      <input type="radio" name="num_mon" value="100" {is_checked('num_mon', '100')}> 100
      <input type="radio" name="num_mon" value="500" {is_checked('num_mon', '500')}> 500
      <br>

      Number Density:
      <input type="radio" name="density" value="0.85" checked> 0.85
      <br>

      K Value:
      <input type="radio" name="k" value="15000" {is_checked('k', '15000')}> 15000
      <input type="radio" name="k" value="20000" {is_checked('k', '20000')}> 20000
      <input type="radio" name="k" value="25000" {is_checked('k', '25000')}> 25000
      <br>

      Bond Length:
      <input type="radio" name="bond_l" value="1.0" checked> 1.0
      <br>

      R<sub>cut</sub> Value:
      <input type="radio" name="r_cut" value="0.9" {is_checked('r_cut', '0.9')}> 0.9
      <input type="radio" name="r_cut" value="1.0" {is_checked('r_cut', '1.0')}> 1.0
      <input type="radio" name="r_cut" value="2.0" {is_checked('r_cut', '2.0')}> 2.0
      <br>

      kT Value:
      <input type="radio" name="kT" value="0.5" {is_checked('kT', '0.5')}> 0.5
      <input type="radio" name="kT" value="1.0" {is_checked('kT', '1.0')}> 1.0
      <input type="radio" name="kT" value="3.0" {is_checked('kT', '3.0')}> 3.0
      <br>

      A Value:
      <input type="radio" name="A" value="500" {is_checked('A', '500')}> 500
      <input type="radio" name="A" value="1000" {is_checked('A', '1000')}> 1000
      <input type="radio" name="A" value="5000" {is_checked('A', '5000')}> 5000
      <br>

      &gamma; Value:
      <input type="radio" name="gamma" value="200" {is_checked('gamma', '200')}> 200
      <input type="radio" name="gamma" value="800" {is_checked('gamma', '800')}> 800
      <input type="radio" name="gamma" value="1600" {is_checked('gamma', '1600')}> 1600
      <br>

      dt Value:
      <input type="radio" name="dt" value="0.01" {is_checked('dt', '0.01')}> 0.01
      <input type="radio" name="dt" value="0.001" {is_checked('dt', '0.001')}> 0.001
      <input type="radio" name="dt" value="0.0001" {is_checked('dt', '0.0001')}> 0.0001
      <br>

      Particle Spacing:
      <input type="radio" name="particle_spacing" value="1.1" checked> 1.1
      <br>

      Seed:
      <input type="radio" name="seed" value="125" checked> 125
      <br>

      <input type="submit" value="Process">
    </form>
  </body>
</html>
""")

if exit_after_form:
    sys.exit()

# Handle errors in running commands for us, exiting early with some info about
# the failed process
def run_cmd(cmd):
    cmd_data = subprocess.run(cmd, capture_output=True)

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
</p>
        """)
        sys.exit()

log_file = "".join([
    f"/bsuhome/{BORAH_USERNAME}/scratch/PhantomWalk/phantomwalk/signac/view/"
    f"A/{get_input_val('A')}/"
    f"dt/{get_input_val('dt')}/"
    f"gamma/{get_input_val('gamma')}/"
    f"k/{get_input_val('k')}/"
    f"kT/{get_input_val('kT')}/"
    f"num_mon/{get_input_val('num_mon')}/"
    f"num_pol/{get_input_val('num_pol')}/"
    f"r_cut/{get_input_val('r_cut')}/"
    "job/log.txt"
])

domain_min = get_input_val('domain_min')
domain_max = get_input_val('domain_max')
range_min = get_input_val('range_min')
range_max = get_input_val('range_max')

gen_graph_cmd = " ".join([
    "conda activate phantomwalk-dev &&",
    f"python /bsuhome/{BORAH_USERNAME}/scratch/PhantomWalk/phantomwalk/signac/data_parser/gen_graph.py",
    f"--y-axis-key {get_input_val('y_axis_key')}",
    f"--y-axis-name {get_input_val('y_axis_name')}",
    f"--x-axis-key {get_input_val('x_axis_key')}",
    f"--x-axis-name {get_input_val('x_axis_name')}",
    (f"--domain-min {domain_min}" if domain_min is not '' else ""),
    (f"--domain-max {domain_max}" if domain_max is not '' else ""),
    (f"--range-min {range_min}" if range_min is not '' else ""),
    (f"--range-max {range_max}" if range_max is not '' else ""),
    f"--log-file {log_file}"
])
borah_gen_graph_cmd = ["ssh", "-C", f"{BORAH_USERNAME}@borah-login.boisestate.edu", f"{gen_graph_cmd}"]
run_cmd(borah_gen_graph_cmd)

# grab the image from borah and bring it onto this computer
run_cmd(f"scp {BORAH_USERNAME}@borah-login.boisestate.edu:~/{GRAPH_FILE_NAME} .".split())

print(f"<img src=\"../{GRAPH_FILE_NAME}\">")
