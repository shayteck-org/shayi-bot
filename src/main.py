import logging
from bot import app

from db import create_db, create_tables, read_db, get_weekly_users
from logger import configure_logger


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Configurations...")
    configure_logger()

    create_db()
    create_tables()
    read_db()

    for user in get_weekly_users():
        logger.info(f"User: {user}")

    logger.info("Starting Bot...")

    app.run()

    logger.info("Bot has stopped.")
