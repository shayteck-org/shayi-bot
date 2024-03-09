from mysql.connector import connect

from constants import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


def create_db():
    connection = connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD)
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS downloader")
    connection.commit()

    cursor.close()
    connection.close()


def create_tables():
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
        "CREATE TABLE if not exists user (telegramID BIGINT,firstMessage TIMESTAMP,lastMessage TIMESTAMP,userName TEXT)"
    )
    cursor.execute("CREATE TABLE if not exists admin (ID BIGINT)")
    cursor.execute(
        "CREATE TABLE if not exists link (telegramID BIGINT, linkType TEXT,link TEXT)"
    )

    connection.commit()
    cursor.close()
    connection.close()


def read_db():
    connection = connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    print(users)
    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()
    print(admins)
    if len(admins) == 0:
        pass
        cursor.execute("INSERT INTO admin VALUES (%s);", (368783021,))
    cursor.execute("SELECT * FROM link")
    links = cursor.fetchall()
    print(links)
    # cursor.execute("INSERT INTO user VALUES (%s, %s, %s,%s);",(10000000000,datetime.datetime.now(),datetime.datetime.now(),"@test1",))

    connection.commit()
    cursor.close()
    connection.close()


def start_db():
    create_db()
    create_tables()
    read_db()