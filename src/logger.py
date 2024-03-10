import logging

USER_LEVEL = 15
ADMIN_LEVEL = 25


class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.DEBUG: "\033[34m",  # Blue
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
        USER_LEVEL: "\033[37m",  # Gray
        ADMIN_LEVEL: "\033[36m",  # Cyan
    }

    def format(self, record):
        color_code = self.COLOR_CODES.get(record.levelno, "\033[0m")
        message = super().format(record)
        return f"{color_code}{message}\033[0m"  # Reset color


def configure_logger():
    logging.addLevelName(USER_LEVEL, "USER")
    logging.addLevelName(ADMIN_LEVEL, "ADMIN")

    logger_handlers = [
        logging.StreamHandler(),
        logging.FileHandler("downloader-bot.log"),
    ]

    for handler in logger_handlers:
        handler.setFormatter(
            ColoredFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    logging.basicConfig(
        handlers=logger_handlers,
        encoding="utf-8",
        level=logging.INFO,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("WDM").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)

    logger.debug("Logger configured.")

    return logger


def user_log(message, *args, **kwargs):
    logger = logging.getLogger(__name__)
    if logger.isEnabledFor(USER_LEVEL):
        logger.log(USER_LEVEL, message, *args, **kwargs)
    else:
        logger.warn("User log level is not enabled.")
        logger.log(logging.INFO, message, *args, **kwargs)


def admin_log(message, *args, **kwargs):
    logger = logging.getLogger(__name__)

    if logger.isEnabledFor(ADMIN_LEVEL):
        logger.log(ADMIN_LEVEL, message, *args, **kwargs)
    else:
        logger.warn("Admin log level is not enabled.")

        logger.log(logging.INFO, message, *args, **kwargs)
