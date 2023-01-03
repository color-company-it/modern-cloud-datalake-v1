import logging


def get_logger(level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with log formatting.
    :param level: The log level. Defaults to logging.INFO.
    :returns: The logger object.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(
        level=level,
        format="[%(filename)s:%(lineno)s] %(asctime)-15s %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    return logging.getLogger(__name__)
