import logging
import sys


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
