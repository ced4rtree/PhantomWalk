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
from dataclasses import dataclass
from dash import Output, Input, html, dcc, Dash
import pandas as pd

### Define app parameters ###
variables = ["A", "k", "gamma"]

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

class Data:
    name: str
    collection: np.ndarray = np.array([])
    global_axes = []

    def _globalize(self):
        Data.global_axes.append(self)

    '''
    Return a sorted array containing all unique values of this data
    '''
    def unique(self):
        return np.sort(np.unique(self.collection))

class JobInput(Data):
    def __init__(self, name, jobs):
        self.name = name
        for job in jobs:
            self.collection = np.append(self.collection, job.statepoint[name])
        self._globalize()

class JobOutput(Data):
    errors: np.ndarray = np.array([])

    def __init__(self, name, key, default, jobs):
        self.name = name
        for job in jobs:
            try:
                with open(job.fn("summary.txt"), 'r') as summary_file:
                    summary = summary_file.read()
                    job_outputs = [ txt.split(",")[1].split(' ')[1] for txt in summary.split('\n') if key in txt ]
            except FileNotFoundError:
                job_outputs = np.array([ 0 ])
                print(f"summary.txt not found for {job.id}")
            try:
                job_outputs = [ float(t) for t in job_outputs ]
            except ValueError:
                print(f"Failed to read summary.txt of {job.id}")
                job_outputs = np.array([0])
            if len(job_outputs) > 0:
                output_mean = sum(job_outputs)/len(job_outputs)
                output_stddev = np.std(job_outputs)
                output_sem = output_stddev / math.sqrt(len(job_outputs))
            else:
                output_mean = default
                output_sem = 0
            self.collection = np.append(self.collection, output_mean)
            self.errors = np.append(self.errors, output_sem)
        self._globalize()

### Retrieve Data ###
project = signac.Project(path='../')
jobs = project.find_jobs(constants)

print(f"Collecting {variables[0]}...")
xs = JobInput(variables[0], jobs)

print(f"Collecting {variables[1]}...")
ys = JobInput(variables[1], jobs)

print(f"Collecting {variables[2]}...")
zs = JobInput(variables[2], jobs)

print("Collecting walltimes...")
walltimes = JobOutput("Walltime (s)", "total_time", 60 * 5, jobs)

### Create app layout ###
print("Creating app layout...")
app = Dash(__name__)

data = pd.DataFrame({a.name: a.collection for a in Data.global_axes})
ranges = {a.name: a.unique() for a in Data.global_axes}

def generate_div(label, dropdown_id, value, slider=False, extra_style={}):
    elements = [
        html.Label(f'{label}: '),
        dcc.Dropdown(id=f'{dropdown_id}-dropdown', options=[{'label': ax.name, 'value': ax.name} for ax in Data.global_axes], value=value),
    ]
    if slider:
        elements.append(dcc.Slider(id='slice-slider', min=0, max=0, step=1, value=0, marks={}, allow_direct_input=False))

    style = {'width': '24%', 'display': 'inline-block', 'margin': '4px', 'verticalAlign': 'top'}

    ret = html.Div(elements, style={**style, **extra_style}) 
    return ret

app.title = "DPD Data Viewer"
app.layout = html.Div([
    html.Div([
        generate_div('X-axis', 'xaxis', Data.global_axes[0].name),
        generate_div('Y-axis', 'yaxis', Data.global_axes[1].name),
        generate_div('Z-axis', 'zaxis', walltimes.name)
    ]),
    generate_div('Slice Along', 'slice', Data.global_axes[2].name, slider=True, extra_style={'width': '73%'}),

    # 3D Surface Plot
    dcc.Graph(id='3d-surface-plot', style={'height': '100%'})
], style={
    'height': '85vh',
})

# Add callback to update the slider when a new 4th axis is selected
@app.callback(
    [Output('slice-slider', 'min'),
     Output('slice-slider', 'max'),
     Output('slice-slider', 'marks'),
     Output('slice-slider', 'value')],
    Input('slice-dropdown', 'value')
)
def update_slice_slider(slice_axis):
    unique_values = ranges[slice_axis]
    marks = {i: str(v) for i, v in enumerate(unique_values)}
    return 0, len(unique_values)-1, marks, 0

Z_UPPER_LIM=min([6, max(walltimes.collection)])
Z_LOWER_LIM=min(walltimes.collection)

# Add callback to update graph when any axis is changed
@app.callback(
    Output('3d-surface-plot', 'figure'),
    [Input('xaxis-dropdown', 'value'),
     Input('yaxis-dropdown', 'value'),
     Input('zaxis-dropdown', 'value'),
     Input('slice-dropdown', 'value'),
     Input('slice-slider', 'value')]
)
def update_graph(xaxis, yaxis, zaxis, slice_axis, slice_idx):
    # Ensure all axes are unique
    if len({xaxis, yaxis, zaxis, slice_axis}) < 4:
        print(f"len(asdf): {len({xaxis, yaxis, zaxis, slice_axis})}")
        return go.Figure()

    print(f'xaxis: {xaxis}')
    print(f'yaxis: {yaxis}')
    print(f'zaxis: {zaxis}')
    print(f'slice_axis: {slice_axis}')

    # Get current slice value
    waxis_value = ranges[slice_axis][slice_idx]

    # Filter data
    subData = data[(data[slice_axis] == waxis_value)]

    # Create 3D surface plot
    x_uniq = ranges[xaxis]
    y_uniq = ranges[yaxis]
    z_grid = np.zeros((len(y_uniq), len(x_uniq)))

    for (x, y, z) in zip(subData[xaxis], subData[yaxis], subData[zaxis]):
        x_idx = np.where(x_uniq == x)[0][0]
        y_idx = np.where(y_uniq == y)[0][0]
        z_grid[y_idx][x_idx] = z
        print(f'{slice_axis}: {waxis_value}, {xaxis}: {x}, {yaxis}: {y}, {zaxis}: {z}')
    
    fig = go.Figure(data=[go.Surface(
        x=x_uniq,
        y=y_uniq,
        z=z_grid
    )])
    print(f'figure: {fig}')
    # print(f'subData[zaxis]: {subData[zaxis]}')
    # print(f'subData[yaxis]: {subData[yaxis]}')
    # print(f'subData[xaxis]: {subData[xaxis]}')
    fig.update_layout(
        title=dict(text=f"{xaxis} & {yaxis} vs. {zaxis} @ {slice_axis}={waxis_value}"),
        uirevision = xaxis + yaxis + zaxis + slice_axis,
        scene = {
            "xaxis": {
                "title": xaxis,
                "tickvals": x_uniq
            },
            "yaxis": {
                "title": yaxis,
                "tickvals": y_uniq
            },
            "zaxis": {
                "title": zaxis,
                "range": [Z_LOWER_LIM, Z_UPPER_LIM]
            }
        }
    )
    fig.update_traces(
        # cmax=Z_UPPER_LIM,
        cmax=3,
        # cmin=Z_LOWER_LIM
        cmin=0.8
    )
    return fig

PORT = 8888
if __name__ == '__main__':
    print(f"Server running on port {PORT}")
    app.run(debug=True, port=PORT)
