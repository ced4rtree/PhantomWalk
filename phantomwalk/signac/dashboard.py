#!/usr/bin/env python3

from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, DocumentList, ImageViewer, Schema, TextDisplay

def job_failure(job):
    summary_filename = 'summary.txt' 
    try:
        with open(job.fn(summary_filename), 'r') as summary_file:
            summary = summary_file.read().split()
            if "FAILURE" in summary[0]:
                return "Job Failed."
            else:
                return "Job Succeeded."
    except:
        return f"Failed to read failure status of {summary_filename}."

modules = [
    StatepointList(),
    DocumentList(context="JobContext"),
    DocumentList(context="ProjectContext"),
    ImageViewer(context="JobContext"),
    ImageViewer(context="ProjectContext"),
    TextDisplay(message=job_failure),
    Schema(),
]

if __name__ == "__main__":
    Dashboard(modules=modules).main()
