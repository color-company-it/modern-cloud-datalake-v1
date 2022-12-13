"""
This script sets up a pre-commit hook for automatically creating a Python lambda layer from a
specified input directory.

To set up:
    1. Install pre-commit: pip install pre-commit
    2. Install the pre-commit hook: pre-commit install

At every commit and push, this script will run and create a lambda layer
from the specified input directory.
"""

import argparse
import os
import shutil

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        help="Path to the directory to be used as the source for the lambda layer",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="Path to the directory where the lambda layer will be created",
    )
    parser.add_argument(
        "-n",
        "--module_name",
        type=str,
        help="Name of the Python module for the lambda layer",
    )
    args, _ = parser.parse_known_args()

    # Create the output directory if it doesn't exist, or delete and re-create it if it does
    try:
        os.makedirs(f"{args.output_dir}/python")
    except FileExistsError:
        shutil.rmtree(f"{args.output_dir}/")

    # Copy the input directory to the output directory
    shutil.copytree(args.input_dir, f"{args.output_dir}/python/{args.module_name}")

    # Can be run via cmd from root:
    #     python scripts/cicd/lambda_layer.py -i codebase/ -o codebase_layer/ -n codebase
