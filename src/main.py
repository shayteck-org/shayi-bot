import logging
from bot import app

from db import start_db
from utils import getWeeklyUsers
from logger import configure_logger


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    configure_logger()

    start_db()

    print(getWeeklyUsers())

    logger.info("Starting Bot...")
    app.run()
    logger.info("Bot has stopped.")
