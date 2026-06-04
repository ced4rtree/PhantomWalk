#!/usr/bin/env python3

from signac_dashboard import Dashboard
from signac_dashboard.modules import StatepointList, DocumentList, ImageViewer, Schema

modules = [
    StatepointList(),
    DocumentList(context="JobContext"),
    DocumentList(context="ProjectContext"),
    ImageViewer(context="JobContext"),
    ImageViewer(context="ProjectContext"),
    Schema(),
]

if __name__ == "__main__":
    Dashboard(modules=modules).main()
