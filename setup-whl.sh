#!/bin/bash

# Clean up the project's build artifacts and create a wheel distribution.
#
# This script deletes the 'build/', 'codebase.egg-info/', and 'dist/' folders
# and all their contents, ignoring nonexistent files.
# It then runs the 'python setup.py bdist_wheel' command to build a wheel
# distribution with python.
# If this command fails, it runs the 'python3 setup.py bdist_wheel' command as a fallback.

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
