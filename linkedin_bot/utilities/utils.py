from logging import Logger


def log_writer(logger: Logger, lvl: int, log: str) -> None:
    """
    Write a log message using the provided logger.

    :param logger: Logger instance to use
    :param lvl: Log level
    :param log: Log message
    """
    logger.log(lvl, log)
