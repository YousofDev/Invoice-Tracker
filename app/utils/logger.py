import logging as logger


class CustomFormatter(logger.Formatter):

    white = "\x1b[97;20m"
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    fmt = "%(asctime)s - {}%(levelname)-8s{} - %(name)s.%(funcName)s - %(message)s"

    FORMATS = {
        logger.DEBUG: white + fmt + reset,
        logger.INFO: cyan + fmt + reset,
        logger.WARNING: yellow + fmt + reset,
        logger.ERROR: red + fmt + reset,
        logger.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logger.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


handler = logger.StreamHandler()
handler.setFormatter(CustomFormatter())

logger.basicConfig(level=logger.DEBUG, handlers=[handler])
