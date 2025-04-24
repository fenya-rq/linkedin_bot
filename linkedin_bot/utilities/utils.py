from logging import Logger


def log_writer(logger: Logger, lvl: int, log: str) -> None:
    logger.log(lvl, log)
