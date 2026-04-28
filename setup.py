#!/usr/bin/env python
"""Backward-compatible setup.py shim.

All project metadata has been moved to pyproject.toml.
This file is kept only for compatibility with legacy tooling
(e.g. `python setup.py install`).
"""
from setuptools import setup

setup()
