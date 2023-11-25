#!/bin/bash

# Build the package
python3 setup.py sdist bdist_wheel

# Upload the package to PyPI using twine
twine upload dist/*
