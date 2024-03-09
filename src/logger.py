import logging

USER = 15
ADMIN = 25

logging.addLevelName(USER, "USER")
logging.addLevelName(ADMIN, "ADMIN")


class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.DEBUG: "\033[34m",  # Blue
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
        USER: "\033[37m",  # Gray
        ADMIN: "\033[35m",  # Magenta
    }

    def format(self, record):
        color_code = self.COLOR_CODES.get(record.levelno, "\033[0m")
        message = super().format(record)
        return f"{color_code}{message}\033[0m"  # Reset color


def configure_logger():
    logger_handlers = [
        logging.StreamHandler(),
        logging.FileHandler("dreaming-bot.log"),
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

    return logging.getLogger(__name__)
