#!/usr/bin/env python3

from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, DocumentList, ImageViewer, Schema, TextDisplay

def read_job_file(filename, job):
    try:
        with open(job.fn(filename), 'r') as the_file:
            return the_file.read()
    except Exception as e:
        return f'Failed to read {filename}. \n{e}'

def read_file(filename):
    return lambda job: read_job_file(filename, job)

modules = [
    StatepointList(),
    DocumentList(context="ProjectContext"),
    ImageViewer(context="JobContext"),
    ImageViewer(context="ProjectContext"),
    TextDisplay(name='summary.txt', message=read_file('summary.txt')),
    TextDisplay(name='Output', message=read_file('output.txt')),
    Schema(),
]

if __name__ == "__main__":
    Dashboard(modules=modules).main()
