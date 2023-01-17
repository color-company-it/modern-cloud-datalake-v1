from setuptools import setup

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="codebase",
    version="0.1",
    description="Modern Cloud Datalake Codebase",
    packages=["codebase", "codebase.aws", "codebase.etl", "codebase.config"],
    install_requires=requirements,
)
