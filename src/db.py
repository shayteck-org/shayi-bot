import logging
from mysql.connector import connect

from constants import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

logger = logging.getLogger(__name__)


def create_db():
    logger.info("Creating database if not exists...")

    connection = connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS downloader")
    connection.commit()

    cursor.close()
    connection.close()


def create_tables():
    logger.info("Creating tables if not exists...")

    connection = connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
    cursor = connection.cursor()

    # cursor.execute("DROP TABLE user")
    # cursor.execute("DROP TABLE userData")
    # cursor.execute("DROP TABLE admin")
    # cursor.execute("DROP TABLE savedFile")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS user (
                telegramID BIGINT,
                firstMessage TIMESTAMP,
                lastMessage TIMESTAMP,
                userName TEXT
            )
        """
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS admin (
            ID BIGINT
        )
        """
    )
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS link (
            telegramID BIGINT,
            linkType TEXT,
            link TEXT
        )
        """
    )

    connection.commit()
    cursor.close()
    connection.close()


def read_db():
    logger.info("Reading the database...")

    connection = connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
    cursor = connection.cursor()

    logger.info("User Table:")
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    for user in users:
        logger.info(
            f"User={{telegramID: {user[0]}, firstMessage: {user[1]}, lastMessage: {user[2]}, userName: {user[3]}}}"
        )
    logger.info("Finished reading the user table.")

    logger.info("Admin Table:")
    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()
    for admin in admins:
        logger.info(f"Admin={{ID: {admin[0]}}}")
    logger.info("Finished reading the admin table.")

    if len(admins) == 0:
        pass
        cursor.execute("INSERT INTO admin VALUES (%s);", (368783021,))
        logger.info(
            "Admin={{ID: 368783021}} inserted into the admin table as the first admin"
        )

    logger.info("Link Table:")
    cursor.execute("SELECT * FROM link")
    links = cursor.fetchall()
    for link in links:
        logger.info(
            f"Link={{telegramID: {link[0]}, linkType: {link[1]}, link: {link[2]}}}"
        )
    logger.info("Finished reading the link table.")

    # cursor.execute("INSERT INTO user VALUES (%s, %s, %s,%s);",(10000000000,datetime.datetime.now(),datetime.datetime.now(),"@test1",))

    connection.commit()
    cursor.close()
    connection.close()
