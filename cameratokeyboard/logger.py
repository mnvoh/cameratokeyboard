import logging
import colorlog


def getLogger() -> colorlog.getLogger:
    logger = colorlog.getLogger("c2k")
    logger.setLevel(logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "[%(log_color)s%(asctime)s %(levelname)s:%(name)s] %(message)s"
        )
    )
    logger.addHandler(handler)
    return logger
