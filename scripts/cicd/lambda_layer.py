import argparse
import os
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", type=str)
    parser.add_argument("-o", "--output_dir", type=str)
    parser.add_argument("-n", "--module_name", type=str)
    args, _ = parser.parse_known_args()

    """
     Can be run via cmd from root:
         python scripts/cicd/lambda_layer.py -i codebase/ -o codebase_layer/ -n codebase
     """
    try:
        os.makedirs(f"{args.output_dir}/python")
    except FileExistsError:
        shutil.rmtree(f"{args.output_dir}/")

    shutil.copytree(args.input_dir, f"{args.output_dir}/python/{args.module_name}")
