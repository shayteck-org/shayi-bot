import os
import logging
import datetime
import json

from mysql.connector import connect

from pyrogram import Client
from pyrogram.types import Message

from constants import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

logger = logging.getLogger(__name__)


class SavedLink:
    def __init__(self, linkType, link):
        self.linkType = linkType
        self.link = link


class AllUserLinks:
    def __init__(self, telegramID, userName):
        self.telegramID = telegramID
        self.userName = userName
        self.links = []
        pass


def days_between(d1, d2):
    return ((d1 - d2).total_seconds()) / 86400


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
        cursor.execute("INSERT INTO admin VALUES (%s);", (368783021,))
        logger.info(
            "Admin={{ID: 5804331708}} inserted into the admin table as the first admin"
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


def get_user_id(message):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user WHERE username = %s", (message.text[1:],))
        user = cursor.fetchone()

        # Extract the username from the message text
        if user is None:
            return None

        return user[0]
    except Exception as e:
        # Handle cases where the username is missing or incorrect

        logger.error(f"Error getting the user id: {e}")

        return None


def get_all_links(message, client: Client):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user ")
        users = cursor.fetchall()

        saved_links = []
        for user in users:
            user_links = {}
            user_links["userID"] = user[0]
            user_links["username"] = user[3]
            user_links["links"] = []
            # user_links = AllUserLinks(user[0],user[3])

            cursor.execute("SELECT * FROM link WHERE telegramID = %s ", (user[0],))
            my_links = cursor.fetchall()

            for link in my_links:
                my_link = {}
                my_link["linkType"] = link[1]
                my_link["link"] = link[2]
                user_links["links"].append(my_link)
                # my_link = SavedLink(link[1],link[2])
                # user_links.links.append(my_link)

            saved_links.append(user_links)

        json_string = json.dumps(saved_links, indent=4)

        with open("links.json", "w") as outfile:
            outfile.write(json_string)

        client.send_document(message.chat.id, open("links.json", "rb"))
        os.remove("links.json")
        # Extract the username from the message text
    except Exception as e:
        # Handle cases where the username is missing or incorrect
        logger.error(f"Error getting all links: {e}")


def add_link(message, linkType):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO link VALUES (%s, %s,%s);",
            (
                message.chat.id,
                linkType,
                message.text,
            ),
        )

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error adding link: {e}")


def update_users(message):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM user WHERE telegramID  = %s", (message.from_user.id,)
        )
        user = cursor.fetchone()

        if user is None:
            cursor.execute(
                "INSERT INTO user VALUES (%s, %s, %s,%s);",
                (
                    message.from_user.id,
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                    message.from_user.username,
                ),
            )

            logger.info(f"User {message.from_user.id} added to the database")
        else:
            cursor.execute(
                "UPDATE user SET firstMessage = %s WHERE telegramID = %s",
                (datetime.datetime.now(), message.from_user.id),
            )
            cursor.execute(
                "UPDATE user SET username = %s WHERE telegramID  = %s",
                (message.from_user.username, message.from_user.id),
            )

            logger.info(f"User {message.from_user.id} updated in the database")

        connection.commit()

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error updating the user table: {e}")


def get_all_users():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        connection.commit()
        cursor.close()
        connection.close()

        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")


def get_weekly_users():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        weeklyUsers = []

        for user in users:
            if days_between(datetime.datetime.now(), user[2]) <= 7:
                weeklyUsers.append(user)

        cursor.close()
        connection.close()

        return weeklyUsers
    except Exception as e:
        logger.error(f"Error getting weekly users: {e}")


def get_monthly_users():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        weeklyUsers = []

        for user in users:
            if days_between(datetime.datetime.now(), user[2]) <= 30:
                weeklyUsers.append(user)

        cursor.close()
        connection.close()

        return weeklyUsers
    except Exception as e:
        logger.error(f"Error getting monthly users: {e}")


def get_weekly_new_users():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        weeklyUsers = []
        for user in users:
            if days_between(datetime.datetime.now(), user[1]) <= 7:
                weeklyUsers.append(user)

        cursor.close()
        connection.close()

        return weeklyUsers
    except Exception as e:
        logger.error(f"Error getting weekly users: {e}")


def get_monthly_new_users():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        weeklyUsers = []
        for user in users:
            if days_between(datetime.datetime.now(), user[1]) <= 30:
                weeklyUsers.append(user)

        cursor.close()
        connection.close()

        return weeklyUsers
    except Exception as e:
        logger.error(f"Error getting monthly new users: {e}")


def check_admin(id):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM admin WHERE ID = %s", (id,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is None:
            return False

        return True
    except Exception as e:
        logger.error(f"Error in check_admin: {e}")


def get_all_admins():
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()

        cursor.execute("SELECT * FROM admin")
        rows2 = cursor.fetchall()

        text = "ادمین ها"
        text += "\n"
        for admin in rows2:
            for user in rows:
                if admin[0] == user[0]:
                    text += str(admin[0])
                    text += " : "
                    text += "@" + user[3]
                    text += "\n"

        cursor.close()
        connection.close()

        return text
    except Exception as e:
        logger.error(f"Error in get_all_admins: {e}")


def promote_to_admin(message: Message, client: Client):
    try:
        id = get_user_id(message)
        if id is None:
            message.reply("بات ما یوزری با این ای دی ندارد")
            return False

        if check_admin(id):
            message.reply("این یوزر از قبل ادمین است")
            return True

        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("INSERT INTO admin VALUES (%s);", (id,))
        connection.commit()

        cursor.close()
        connection.close()

        message.reply("یوزر با موفقیت ادمین شد")

        return True
    except Exception as e:
        logger.error(f"Error in promote_to_admin: {e}")


def remove_admin(message):
    try:
        id = get_user_id(message)

        if id is None:
            message.reply("بات ما یوزری با این ای دی ندارد")
            return False

        if check_admin(id):
            connection = connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
            )
            cursor = connection.cursor()

            cursor.execute("DELETE FROM admin WHERE ID = %s", (id,))
            connection.commit()

            cursor.close()
            connection.close()

            message.reply("یوزر با موفقیت از ادمینی درآمد")

            return True

        message.reply("این یوزر ادمین نیست")

        return True
    except Exception as e:
        logger.error(f"Error in remove_admin: {e}")


def send_global_message(message: Message, client: Client):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        for user in users:
            try:
                client.copy_message(int(user[0]), message.from_user.id, message.id)
            except Exception as e:
                logger.error(f"Error in send_global_message while copying message: {e}")

        cursor.close()
        connection.close()

    except Exception as e:
        logger.error(f"Error in send_global_message: {e}")
