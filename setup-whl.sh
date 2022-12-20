#!/bin/bash

# delete the build/ folder and all its contents, ignoring nonexistent files
rm -rf build/

# delete the codebase.egg-info/ folder and all its contents, ignoring nonexistent files
rm -rf codebase.egg-info/

# delete the dist/ folder and all its contents, ignoring nonexistent files
rm -rf dist/

# run the command to build a wheel distribution with python
python setup.py bdist_wheel ||

# if the previous command failed, run the command to build a wheel distribution with python3
python3 setup.py bdist_wheel
