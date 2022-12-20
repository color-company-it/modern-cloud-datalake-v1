import logging
import sys

from pyspark.sql.types import *

__all__ = ["aws", "config", "etl"]
__version__ = "v0.0.1"

SDLC_SAGES: list = ["dev", "int", "qa", "prod"]
EXTRACT_TYPES: list = ["FE", "PE"]

JDBC_TO_PYSPARK_TYPES: dict = {
    "VARCHAR": StringType,
    "CHAR": StringType,
    "LONGVARCHAR": StringType,
    "NUMERIC": DecimalType,
    "DECIMAL": DecimalType,
    "BIT": BooleanType,
    "TINYINT": ByteType,
    "SMALLINT": ShortType,
    "INTEGER": IntegerType,
    "BIGINT": LongType,
    "REAL": FloatType,
    "FLOAT": DoubleType,
    "DOUBLE": DoubleType,
    "BINARY": BinaryType,
    "VARBINARY": BinaryType,
    "LONGVARBINARY": BinaryType,
    "DATE": DateType,
    "TIME": TimestampType,
    "TIMESTAMP": TimestampType,
}

DATETIME_FMTS: dict = {
    "%Y-%m-%d": "ISO_LOCAL_DATE",
    "%Y-%m-%d %H:%M:%S": "ISO_LOCAL_DATETIME",
    "%Y-%m-%dT%H:%M:%S": "ISO_OFFSET_DATETIME",
    "%a %b %d %H:%M:%S %Y": "RFC_822",
    "%a, %d %b %Y %H:%M:%S %Z": "RFC_1123",
}

DATETIME_FMTS_REGEX: dict = {
    "%Y-%m-%d": r"\d{4}-\d{2}-\d{2}",
    "%Y-%m-%d %H:%M:%S": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
    "%Y-%m-%dT%H:%M:%S": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    "%a %b %d %H:%M:%S %Y": r"[A-Z][a-z]{2} [A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} \d{4}",
    "%a, %d %b %Y %H:%M:%S %Z": r"[A-Z][a-z]{2}, \d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} [A-Z]{3}",
}

CRITICAL_INDEX = {
    "Critical": {"dev": 10, "int": 20, "qa": 30, "prod": 40},
    "High": {"dev": 8, "int": 16, "qa": 24, "prod": 32},
    "Medium": {"dev": 6, "int": 12, "qa": 18, "prod": 24},
    "Low": {"dev": 4, "int": 8, "qa": 12, "prod": 16},
}


def get_logger(log_level: str = logging.INFO) -> logging.Logger:
    """
    A simple method that returns a logger fit
    for the PySpark environment.
    :param log_level: Set log_level, default is INFO.
    :return: logging.Logger
    """
    logger = logging.getLogger()
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(filename)s:%(lineno)s - %(funcName)10s()] %(asctime)-15s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
