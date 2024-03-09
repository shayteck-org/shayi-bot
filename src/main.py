import logging
from bot import app

from db import create_db, create_tables, read_db
from utils import getWeeklyUsers
from logger import configure_logger


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    configure_logger()

    create_db()
    create_tables()
    read_db()

    for user in getWeeklyUsers():
        logger.info(f"User: {user}")

    logger.info("Starting Bot...")

    app.run()

    logger.info("Bot has stopped.")
