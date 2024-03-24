import logging
import colorlog

LOGGER_NAME = "c2k"


def get_logger() -> colorlog.getLogger:
    """
    Gets the default logger for the application
    """
    logger = colorlog.getLogger(LOGGER_NAME)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "[%(log_color)s%(asctime)s %(levelname)s:%(name)s] %(message)s"
        )
    )
    logger.addHandler(handler)
    return logger
