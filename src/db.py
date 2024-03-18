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

    try:
        connection = connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
        cursor = connection.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS downloader")
        connection.commit()

        logger.info("Database created successfully.")

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")


def create_tables():
    logger.info("Creating tables if not exists...")

    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS user (
                    telegramID BIGINT,
                    firstMessage TIMESTAMP,
                    lastMessage TIMESTAMP,
                    userName TEXT
                    state TEXT
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

        cursor.execute(
            "UPDATE user SET state = 'start' where state is NULL or state = '';"
        )

        connection.commit()

        logger.info("Tables created successfully.")

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error creating tables: {e}")


def drop_tables():
    logger.info("Dropping tables if exists...")

    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS user")
        cursor.execute("DROP TABLE IF EXISTS admin")
        cursor.execute("DROP TABLE IF EXISTS link")

        connection.commit()

        logger.info("Tables dropped successfully.")

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")


def read_db():
    logger.info("Reading the database...")

    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        logger.info("Reading the user table:")

        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        for user in users:
            logger.info(
                f"User={{telegramID: {user[0]}, firstMessage: {user[1]}, lastMessage: {user[2]}, userName: {user[3]}}}"
            )
        logger.info("Finished reading the user table.")

        logger.info("Reading the admin table:")

        cursor.execute("SELECT * FROM admin")
        admins = cursor.fetchall()

        for admin in admins:
            logger.info(f"Admin={{ID: {admin[0]}}}")

        logger.info("Finished reading the admin table.")

        if len(admins) == 0:
            cursor.execute("INSERT INTO admin VALUES (%s);", (368783021,))
            logger.info(
                "Admin={{ID: 368783021}} inserted into the admin table as the first admin"
            )

        logger.info("Reading the link table:")

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
    except Exception as e:
        logger.error(f"Error reading the database: {e}")


def get_user_id(message):
    logger.info(f"Getting the user id for the message: {message.text}")

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

        logger.info(f"Fetched user: {user}")

        cursor.close()
        connection.close()

        # Extract the username from the message text
        if user is None:
            return None

        return user[0]
    except Exception as e:
        # Handle cases where the username is missing or incorrect

        logger.error(f"Error getting the user id: {e}")

        return None


def get_all_links(message, client: Client):
    logger.info(f"Getting all links for the message: {message.text}")

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

        for user_links in saved_links:
            logger.info(f"User: {user_links['username']}")
            for link in user_links["links"]:
                logger.info(f"Link: {link['link']}")

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
    logger.info(f"Adding link for the message: {message.text}")

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

        logger.info(f"Link added successfully: {message.text}")

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error adding link: {e}")


def update_users(message):
    logger.info(f"Updating the user table for the message: {message.text}")

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
                "INSERT INTO user VALUES (%s, %s, %s,%s,%s);",
                (
                    message.from_user.id,
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                    message.from_user.username,
                    "start",
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


def update_user_state(id, state):
    logger.info(f"Updating the user state for the user:{id}")

    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE user SET state = %s WHERE telegramID = %s",
            (state, id),
        )

        connection.commit()

        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error updating the user state: {e}")

def get_single_user_state(id):
    logger.info(f"Getting the user state for the user:{id}")

    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user WHERE telegramID = %s", (id,))
        user = cursor.fetchone()

        connection.commit()

        cursor.close()
        connection.close()

        return user[4]
    except Exception as e:
        logger.error(f"Error getting the user state: {e}")

def get_all_users_state():
    logger.info("Getting all user state from db...")

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

        logger.info("Finished getting all user state from db.")

        cursor.close()
        connection.close()

        users_state: dict[int, str] = {}
        for user in users:
            users_state[user[0]] = user[4]

        return users_state
    except Exception as e:
        logger.error(f"Error getting all user state: {e}")
        r: dict[int, str] = {}
        return r


def get_all_users():
    logger.info("Getting all users from db...")

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

        logger.info("Finished getting all users from db.")

        cursor.close()
        connection.close()

        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")


def get_weekly_users():
    logger.info("Getting weekly users from db...")

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

        logger.info("Finished getting weekly users from db.")

        weekly_users = []

        for user in users:
            if days_between(datetime.datetime.now(), user[2]) <= 7:
                weekly_users.append(user)

        for user in weekly_users:
            logger.info(f"User: {user}")

        cursor.close()
        connection.close()

        return weekly_users
    except Exception as e:
        logger.error(f"Error getting weekly users: {e}")


def get_monthly_users():
    logger.info("Getting monthly users from db...")

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

        logger.info("Finished getting monthly users from db.")

        monthly_users = []

        for user in users:
            if days_between(datetime.datetime.now(), user[2]) <= 30:
                monthly_users.append(user)

        for user in monthly_users:
            logger.info(f"User: {user}")

        cursor.close()
        connection.close()

        return monthly_users
    except Exception as e:
        logger.error(f"Error getting monthly users: {e}")


def get_weekly_new_users():
    logger.info("Getting weekly new users from db...")

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

        logger.info("Finished getting weekly new users from db.")

        weekly_users = []
        for user in users:
            if days_between(datetime.datetime.now(), user[1]) <= 7:
                weekly_users.append(user)

        for user in weekly_users:
            logger.info(f"User: {user}")

        cursor.close()
        connection.close()

        return weekly_users
    except Exception as e:
        logger.error(f"Error getting weekly users: {e}")


def get_monthly_new_users():
    logger.info("Getting monthly new users from db...")

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

        logger.info("Finished getting monthly new users from db.")

        monthly_users = []
        for user in users:
            if days_between(datetime.datetime.now(), user[1]) <= 30:
                monthly_users.append(user)

        for user in monthly_users:
            logger.info(f"User: {user}")

        cursor.close()
        connection.close()

        return monthly_users
    except Exception as e:
        logger.error(f"Error getting monthly new users: {e}")


def check_admin(id):
    logger.info(f"Checking if the user is an admin: {id}")

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
            logger.info(f"User: {id} is not an admin.")

            return False

        logger.info(f"User: {user} is an admin.")

        return True
    except Exception as e:
        logger.error(f"Error in check_admin: {e}")


def get_all_admins():
    logger.info("Getting all admins from db...")

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

        logger.info("Finished getting all users from db.")

        cursor.execute("SELECT * FROM admin")
        rows2 = cursor.fetchall()

        logger.info("Finished getting all admins from db.")

        text = "ادمین ها"
        text += "\n"
        for admin in rows2:
            for user in rows:
                if admin[0] == user[0]:
                    text += str(admin[0])
                    text += " : "
                    text += "@" + user[3]
                    text += "\n"

        logger.info(f"Admins list to be returned: {text}")

        cursor.close()
        connection.close()

        return text
    except Exception as e:
        logger.error(f"Error in get_all_admins: {e}")


def promote_to_admin(message: Message, client: Client):
    try:
        logger.info(f"Promoting the user to admin: {message.from_user.id}")

        user_id = get_user_id(message)

        if user_id is None:
            logger.info(f"User {user_id} was not found in db.")

            message.reply("بات ما یوزری با این ای دی ندارد")

            return False

        if check_admin(user_id):
            logger.info(f"User {user_id} is already an admin.")

            message.reply("این یوزر از قبل ادمین است")

            return True

        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()

        cursor.execute("INSERT INTO admin VALUES (%s);", (user_id,))
        connection.commit()

        logger.info(f"User {user_id} was promoted to admin.")

        cursor.close()
        connection.close()

        message.reply("یوزر با موفقیت ادمین شد")

        return True
    except Exception as e:
        logger.error(f"Error in promote_to_admin: {e}")


def remove_admin(message):
    try:
        logger.info(f"Removing the user {message.from_user.id} from admin.")

        user_id = get_user_id(message)

        if user_id is None:
            logger.info(f"User {user_id} was not found in db.")

            message.reply("بات ما یوزری با این ای دی ندارد")

            return False

        if check_admin(user_id):
            connection = connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
            )
            cursor = connection.cursor()

            cursor.execute("DELETE FROM admin WHERE ID = %s", (user_id,))
            connection.commit()

            logger.info(f"User {user_id} was removed from admin.")

            cursor.close()
            connection.close()

            message.reply("یوزر با موفقیت از ادمینی درآمد")

            return True

        logger.info(f"User {user_id} is not an admin.")

        message.reply("این یوزر ادمین نیست")

        return True
    except Exception as e:
        logger.error(f"Error in remove_admin: {e}")


def send_global_message(message: Message, client: Client):
    logger.info(f"Sending global message: {message.text}")

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

        logger.info(f"Sending message to {len(users)} users")

        for user in users:
            try:
                client.copy_message(int(user[0]), message.from_user.id, message.id)
            except Exception as e:
                logger.error(f"Error in send_global_message while copying message: {e}")

        logger.info("Finished sending global message.")

        cursor.close()
        connection.close()

    except Exception as e:
        logger.error(f"Error in send_global_message: {e}")
