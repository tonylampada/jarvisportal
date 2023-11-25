#!/bin/bash

rm -Rf build/ dist/
python3 setup.py sdist bdist_wheel
twine upload dist/*
