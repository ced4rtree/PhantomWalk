#!/usr/bin/env python3

from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, DocumentList, ImageViewer, Schema, TextDisplay

def read_summary(job):
    filename = 'summary.txt'
    try:
        with open(job.fn(filename, 'r')) as summary_file:
            return summary_file.read()
    except:
        return f'Failed to read {filename}.'

modules = [
    StatepointList(),
    DocumentList(context="ProjectContext"),
    ImageViewer(context="JobContext"),
    ImageViewer(context="ProjectContext"),
    TextDisplay(message=read_summary),
    Schema(),
]

if __name__ == "__main__":
    Dashboard(modules=modules).main()
