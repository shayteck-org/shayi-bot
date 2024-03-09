# Importing dependencies
import os
import time
import datetime
import json

import requests

from pytube import YouTube

from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from mysql.connector import connect

from constants import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

temp_message = dict()


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


def get_user_id(message):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()
        # print(message.text)
        cursor.execute("SELECT * FROM user WHERE username = %s", (message.text[1:],))
        user = cursor.fetchone()
        # Extract the username from the message text
        if user is None:
            return None

        return user[0]
    except Exception as e:
        # Handle cases where the username is missing or incorrect
        print(e)
        return None


def days_between(d1, d2):
    return ((d1 - d2).total_seconds()) / 86400


def getAllLinks(message, client: Client):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()
        # print(message.text)
        cursor.execute("SELECT * FROM user ")
        users = cursor.fetchall()
        savedlinks = []
        for user in users:
            userlinks = {}
            userlinks["userID"] = user[0]
            userlinks["username"] = user[3]
            userlinks["links"] = []
            # userlinks = AllUserLinks(user[0],user[3])
            cursor.execute("SELECT * FROM link WHERE telegramID = %s ", (user[0],))
            mylinks = cursor.fetchall()
            for link in mylinks:
                mylink = {}
                mylink["linkType"] = link[1]
                mylink["link"] = link[2]
                userlinks["links"].append(mylink)
                # mylink = SavedLink(link[1],link[2])
                # userlinks.links.append(mylink)
            savedlinks.append(userlinks)

        json_string = json.dumps(savedlinks, indent=4)
        print(json_string)
        with open("links.json", "w") as outfile:
            outfile.write(json_string)
        client.send_document(message.chat.id, open("links.json", "rb"))
        os.remove("links.json")
        # Extract the username from the message text
    except Exception as e:
        # Handle cases where the username is missing or incorrect
        print(e)


def addLink(message, linkType):
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
        print(e)
        pass


def updateUsers(message):
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
        else:
            cursor.execute(
                "UPDATE user SET firstMessage = %s WHERE telegramID = %s",
                (datetime.datetime.now(), message.from_user.id),
            )
            cursor.execute(
                "UPDATE user SET username = %s WHERE telegramID  = %s",
                (message.from_user.username, message.from_user.id),
            )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)
        pass


def getAllUsers():
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
        print(e)
        pass


def getWeeklyUsers():
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
        print(e)


def getMonthlyUsers():
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
        print(e)


def getWeeklyNewUsers():
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
        print(e)


def getMonthlyNewUsers():
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
        print(e)


def checkAdmin(id):
    try:
        connection = connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = connection.cursor()
        print(id)
        cursor.execute("SELECT * FROM admin WHERE ID = %s", (id,))
        user = cursor.fetchone()
        print("ok")
        print(user)
        cursor.close()
        connection.close()
        print("ok")
        if user is None:
            return False
        return True
    except Exception as e:
        print(e)


def promoteToAdmin(message: Message, client: Client):
    try:
        id = get_user_id(message)
        if id is None:
            message.reply("بات ما یوزری با این ای دی ندارد")
            return False
        if checkAdmin(id) == True:
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
        print(e)
        pass


def removeAdmin(message):
    try:
        id = get_user_id(message)

        if id is None:
            message.reply("بات ما یوزری با این ای دی ندارد")
            return False
        if checkAdmin(id) == True:
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
        print(e)
        pass


def getAllAdmins():
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
        # print(rows)
        cursor.execute("SELECT * FROM admin")
        rows2 = cursor.fetchall()
        # print(rows2)
        print(rows)
        print(rows2)
        text = "ادمین ها"
        text += "\n"
        for admin in rows2:
            for user in rows:
                if admin[0] == user[0]:
                    text += str(admin[0])
                    text += " : "
                    text += "@" + user[3]
                    text += "\n"
        print(text)
        cursor.close()
        connection.close()
        return text
    except Exception as e:
        print(e)


def sendGlobalMessage(message: Message, client: Client):
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
            # print(int(user[0]))
            # print(user[3])
            try:
                client.copy_message(int(user[0]), message.from_user.id, message.id)
            except Exception as e:
                # print(e)
                pass
        cursor.close()
        connection.close()

    except Exception as e:
        print(e)
        pass


def youtube_download(link, res, message: Message, client: Client):
    video_url = link
    yt = YouTube(video_url)
    title = yt.title

    selected_stream = yt.streams.filter(res=res, progressive=True).first()
    sent_message = message.reply_text("در حال دانلود...")
    selected_stream.download()
    sent_message.delete()
    return title


def instagram_download(link, message: Message, client: Client):
    global temp_message
    try:
        # OPENING THE WEBPAGE
        temp_message[message.from_user.id] = message.reply_text("در حال دانلود...")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        options.add_experimental_option("excludeSwitches", ["enable-automaion"])
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc",
            platform="Linux64",
            webgl_vendor="Intel Inc",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        driver.get("https://snapinsta.app/")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            classname = button.get_dom_attribute("class")
            print(classname)
            if classname == "fc-button fc-cta-consent fc-primary-button":
                button.click()
                break
        time.sleep(2)

        # target username
        username = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='url']"))
        )

        # enter username and password
        username.clear()
        username.send_keys(link)

        # target the login button and click it
        button = (
            WebDriverWait(driver, 2)
            .until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            .click()
        )
        time.sleep(10)
        links = driver.find_elements(By.TAG_NAME, "a")
        i = 0
        counter = 0
        for link in links:
            print(i)
            print(link.get_dom_attribute("data-event"))
            if link.get_dom_attribute("data-event") == "click_download_btn":
                try:
                    downloadLink = link.get_dom_attribute("href")
                    print(downloadLink)
                    r = requests.get(downloadLink, allow_redirects=True)
                    content = r.headers.get("content-disposition")
                    print(content)
                    filename = content[content.find("filename=") + 9 :]
                    print(filename)
                    open(filename, "wb").write(r.content)
                    if filename[-3:] == "mp4":
                        try:
                            temp_message[message.from_user.id].delete()
                        except:
                            pass
                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )
                        message.reply_video(filename)
                        try:
                            temp_message[message.from_user.id].delete()
                        except:
                            pass
                    elif filename[-3:] == "jpg":
                        try:
                            temp_message[message.from_user.id].delete()
                        except:
                            pass
                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )
                        message.reply_photo(filename)
                        try:
                            temp_message[message.from_user.id].delete()
                        except:
                            pass
                    os.remove(filename)
                except Exception as e:
                    print(e)
                    pass
                counter += 1
            i += 1
        if counter == 0:
            try:
                temp_message[message.from_user.id].delete()
            except:
                pass
            message.reply_text("نمی توان این لینک را دانلود کرد")
        else:
            addLink(message, "Instagram")
        try:
            temp_message[message.from_user.id].delete()
        except:
            pass
        print("download done")
        driver.close()
    except Exception as e:
        print(e)
        print("couldn't download this link")
        message.reply_text("نمی توان این لینک را دانلود کرد")
        try:
            temp_message[message.from_user.id].delete()
        except:
            pass
    pass


def reply_buttons(text, message: Message, client: Client):
    global temp_message
    test = message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="دانلود از اینستاگرام", callback_data="insta"
                    ),
                    InlineKeyboardButton(
                        text="دانلود از یوتوب", callback_data="youtube"
                    ),
                ]
            ]
        ),
    )
    # print(test)
    # test.delete()
    temp_message[message.from_user.id] = test
    print(message.from_user.id)
    # print(temp_message[message.from_user.id])


def reply_back_button(text, message: Message, client: Client):
    global temp_message

    temp_message[message.from_user.id] = message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="بازگشت", callback_data="back")]]
        ),
    )
