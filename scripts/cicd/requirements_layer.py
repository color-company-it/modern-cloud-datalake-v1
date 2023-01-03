import subprocess


def create_zip_file(target_folder: str, zip_file: str, requirements_file: str):
    # Install the requirements from the requirements file
    subprocess.run(
        ["pip", "install", "-t", target_folder, "-r", requirements_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    subprocess.run(
        ["pip3", "install", "-t", target_folder, "-r", requirements_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    # Create the zip file
    subprocess.run(
        ["zip", "-r", zip_file, target_folder],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    # Remove the target folder
    subprocess.run(
        ["rm", "-rf", target_folder],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


if __name__ == "__main__":
    create_zip_file(
        target_folder="datalake_layer/python",
        requirements_file="lambda_requirements.txt",
        zip_file="datalake_layer",
    )
