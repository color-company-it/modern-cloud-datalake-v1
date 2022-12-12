"""
PySpark JDBC Load Job.
"""
import argparse

from pyspark.sql import SparkSession

from codebase import get_logger

# Set up SparkContext
SPARK = SparkSession.builder.appName("Load JDBC Source").getOrCreate()
LOGGER = get_logger()


def main():
    """
    Main entrypoint.
    """
    pass


if __name__ == "__main__":
    # Set up command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, help="Path to input data")
    parser.add_argument("--output_path", type=str, help="Path to output data")
    args = parser.parse_args()

    LOGGER.info("Starting PySpark Job.")
    try:
        main()
    except Exception as err:
        LOGGER.info(f"PySpark Job Failed with the error:\n{err}")
    LOGGER.info("PySpark Job Succeeded.")
