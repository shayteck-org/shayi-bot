import os
import time
import logging
import requests
import uuid

from instagrapi import Client as InstaClient
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    ReplyKeyboardMarkup,
)

from pytube import YouTube

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from db import (
    update_users,
    check_admin,
    get_all_users,
    get_all_links,
    get_weekly_users,
    get_monthly_users,
    get_weekly_new_users,
    get_monthly_new_users,
    get_all_admins,
    promote_to_admin,
    remove_admin,
    send_global_message,
    add_link,
)

from logger import user_log, admin_log
from constants import API_ID, API_HASH, BOT_TOKEN, INSTAUSERNAME, INSTAPASSWORD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


users = {}
links = {}
qualities = {}
temp_message = dict()

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
def start_handler(client: Client, message: Message):
    user_log(f"User {message.from_user.id} has started the bot")

    try:
        update_users(message)

        global temp_message
        users[message.from_user.id] = "start"

        text = (
            "سلام خوش اومدی! \n من میتونم برات از اینستاگرام و یوتوب دانلود کنم😎 \n"
            " کافیه لینک ویدیوی یوتوب یا هر چیزی تو اینستا مثل استوری،پست، igtv و reel رو بفرستی تا فایلشو واست بفرستم🫡🤌"
        )

        reply_buttons(text, message, client)
    except Exception as e:
        logger.error(f"Error while starting the bot: {e}")


@app.on_message(filters.command("adminpanel"))
def adminPanel(client: Client, message: Message):
    admin_log(f"User {message.from_user.id} has accessed admin panel")

    try:
        if not check_admin(message.chat.id):
            logger.warn(f"{message.from_user.id} tried to access admin panel")

            message.reply("only admins can use this command")
        else:
            #     temp_message[message.from_user.id] = message.reply_text(text="پنل ادمینی برای شما فعال شد", reply_markup=InlineKeyboardMarkup(
            # [
            #     [InlineKeyboardButton(text="اضافه کردن ادمین", callback_data="insta")],
            #     [InlineKeyboardButton(text="حذف ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            #     [InlineKeyboardButton(text="اضافه کردن ادمین",callback_data="i")],
            # ]
            # ))

            keyboard = ReplyKeyboardMarkup(
                [
                    ["تعداد تمام یوزر ها"],
                    ["تعداد یوزر های فعال هفته گذشته"],
                    ["تعداد یوزر های فعال ماه گذشته"],
                    ["تعداد یوزر های جدید هفته گذشته"],
                    ["تعداد یوزر های جدید ماه گذشته"],
                    ["لیست لینک های درخواستی"],
                    ["لیست ادمین ها"],
                    ["اضافه کردن ادمین"],
                    ["حذف ادمین"],
                    ["پیام همگانی"],
                    ["کنسل کردن درخواست"],
                ]
            )

            # client.send_message(message.from_user.id,"پنل ادمینی برای شما فعال شد" , reply_markup = keyboard,reply_to_message_id=message.id)

            message.reply("پنل ادمینی برای شما فعال شد", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error while accessing admin panel: {e}")


@app.on_callback_query()
def call_back_handler(client: Client, callback: CallbackQuery):
    user_log(f"User {callback.from_user.id} has clicked on {callback.data}")
    try:
        global temp_message

        if callback.data == "youtube":
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            users[callback.from_user.id] = callback.data

            temp_message[callback.message.chat.id] = callback.message.reply_text(
                "لطفا لینک ویدیوی یوتوب رو بفرست🙏"
            )
        elif callback.data == "insta":
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            users[callback.from_user.id] = callback.data

            temp_message[callback.message.chat.id] = callback.message.reply_text(
                "لطفا لینک ویدیوی اینستاگرام رو بفرست🙏"
            )
        elif callback.data == "back":
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            users[callback.from_user.id] = ""
            text = "چه کار دیگه ای میتونم برات انجام بدم؟🤔"

            reply_buttons(text, callback.message, client)
        else:
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            ID = callback.from_user.id
            users[ID] = "download"

            user_log(
                f"User {ID} has selected {callback.data} resolution for YouTube video. Attempting to download..."
            )

            title = youtube_download(
                link=links[ID],
                res=callback.data,
                message=callback.message,
                client=client,
            )

            if title == "":
                callback.message.reply_text(
                    "مشکلی پیش آمده است، لطفا دوباره تلاش کنید."
                )

            logger.debug(f"Video has been successfully downloaded as {title}")

            sent_message = callback.message.reply_text(
                "با موفقیت دانلود شد، در حال ارسال..."
            )

            path = title
            # special_characters = r'\/:*?"<>|#'
            # path = (
            #     "".join(char for char in title if char not in special_characters)
            #     + ".mp4"
            # )

            logger.info(f"Sending {path} to user {ID}")

            callback.message.reply_video(video=path)

            logger.info(
                "Video has been successfully sent to user. Adding link to database..."
            )
            add_link(callback.message, "YouTube")

            logger.info("Link has been successfully added to database.")

            try:
                sent_message.delete()
            except Exception as e:
                logger.error("Error while deleting sent message", e)

            reply_back_button(text="بازگشت؟", message=callback.message, client=client)

            try:
                logger.info(f"Deleting {path}")

                os.remove(path=path)

                logger.info(f"{path} has been successfully deleted.")
            except Exception as e:
                logger.error(f"Error while deleting {path}", e)
    except Exception as e:
        logger.error(f"Error while handling callback: {e}")

        callback.message.reply_text("مشکلی پیش آمده است، لطفا دوباره تلاش کنید.")


@app.on_message(filters.text)
def message_handler(client: Client, message: Message):
    try:
        user_log(f"User {message.from_user.id} has sent a message: {message.text}")

        global temp_message

        update_users(message)

        if message.text == "تعداد تمام یوزر ها":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access all users count without being an admin"
                )
            else:
                userNumber = len(get_all_users())
                text = "تعداد تمامی یوزر ها :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "لیست لینک های درخواستی":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access all links without being an admin"
                )
            else:
                get_all_links(message, client)

        elif message.text == "تعداد یوزر های فعال هفته گذشته":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access weekly active users count without being an admin"
                )
            else:
                userNumber = len(get_weekly_users())
                text = "تعداد یوزر های فعال هفته گذشته :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "تعداد یوزر های فعال ماه گذشته":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access monthly active users count without being an admin"
                )
            else:
                userNumber = len(get_monthly_users())
                text = "تعداد یوزر های فعال ماه گذشته :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "تعداد یوزر های جدید هفته گذشته":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access weekly new users count without being an admin"
                )
            else:
                userNumber = len(get_weekly_new_users())
                text = "تعداد یوزر های جدید هفته گذشته :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "تعداد یوزر های جدید ماه گذشته":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access monthly new users count without being an admin"
                )
            else:
                userNumber = len(get_monthly_new_users())
                text = "تعداد یوزر های جدید ماه گذشته :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "تعداد یوزر های جدید ماه گذشته":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access monthly new users count without being an admin"
                )
            else:
                userNumber = len(get_monthly_new_users())
                text = "تعداد یوزر های جدید ماه گذشته :"
                text += "\n"
                text += str(userNumber)
                message.reply(text)

        elif message.text == "لیست ادمین ها":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to access admin list without being an admin"
                )
            else:
                text = get_all_admins()
                message.reply(text)

        elif message.text == "اضافه کردن ادمین":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to add an admin without being an admin"
                )
            else:
                message.reply(
                    "لطفا آی دی تلگرام کسی که می خواهید ادمین کنید را وارد کنید"
                )
                users[message.from_user.id] = "addAdmin"

        elif message.text == "حذف ادمین":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to remove an admin without being an admin"
                )
            else:
                message.reply(
                    "لطفا آی دی تلگرام کسی که می خواهید از ادمینی برکنار کنید را وارد کنید"
                )
                users[message.from_user.id] = "removeAdmin"

        elif message.text == "پیام همگانی":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to send a global message without being an admin"
                )
            else:
                message.reply("پیام بعدی شما به همه ی یوزر ها خواهد رفت")
                users[message.from_user.id] = "globalMessage"

        elif message.text == "کنسل کردن درخواست":
            users[message.from_user.id] = ""

        elif users[message.from_user.id] == "globalMessage":
            send_global_message(message, client)
            users[message.from_user.id] = ""

        elif users[message.from_user.id] == "addAdmin":
            promote_to_admin(message, client)
            users[message.from_user.id] = ""

        elif users[message.from_user.id] == "removeAdmin":
            remove_admin(message)
            users[message.from_user.id] = ""

        elif users[message.from_user.id] == "insta":
            try:
                temp_message[message.from_user.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            logger.info(
                f"User {message.from_user.id} has sent an Instagram link: {message.text}"
            )

            instagram_download(message.text, message, client)
            reply_back_button(text="بازگشت؟", message=message, client=client)

        elif users[message.from_user.id] == "youtube":
            if "youtube.com" in message.text or "youtu.be" in message.text:
                try:
                    temp_message[message.from_user.id].delete()
                except Exception as e:
                    logger.error("Error while deleting temp message", e)

                video_url = message.text

                logger.info(
                    f"User {message.from_user.id} has sent a YouTube link: {video_url}"
                )

                yt = YouTube(video_url)
                streams = yt.streams.filter(progressive=True)

                logger.info(f"Available resolutions for {video_url}: {streams}")

                resolutions = []

                for stream in streams:
                    resolution_button = [
                        InlineKeyboardButton(
                            text=stream.resolution, callback_data=stream.resolution
                        )
                    ]
                    resolutions.append(resolution_button)

                txt = "یکی از کیفیت های موجود رو انتخاب کن. " + "\n"

                temp_message[message.from_user.id] = message.reply_text(
                    text=txt, reply_markup=InlineKeyboardMarkup(resolutions)
                )

                users[message.from_user.id] = "ytquality"
                links[message.from_user.id] = message.text
                qualities[message.from_user.id] = resolutions

            else:
                text = "لینک اشتباه است، دوباره وارد کنید."
                text += "\n \n"
                text += "بازگشت؟"
                reply_buttons(text=text, message=message, client=client)
    except Exception as e:
        logger.error(f"Error while handling message: {e}")

        message.reply_text("مشکلی پیش آمده است، لطفا دوباره تلاش کنید.")


def youtube_download(link, res, message: Message, client: Client):
    try:
        logger.debug(f"Downloading youtube video from link: {link}")

        video_url = link
        yt = YouTube(video_url)
        title = yt.title

        filename_uuid = str(uuid.uuid4()) + "mp4"

        selected_stream = yt.streams.filter(res=res, progressive=True).first()

        logger.debug(f"Downloading video with title: {title}")

        sent_message = message.reply_text("در حال دانلود...")

        selected_stream.download(filename=filename_uuid)

        logger.debug(
            f"Downloaded the video with title: {title} and uuid: {filename_uuid}"
        )

        sent_message.delete()

        return filename_uuid
    except Exception as e:
        logger.error(f"Error downloading youtube video: {e}")

        return ""


def instagram_download(link, message: Message, client: Client):

    try:
        temp_message[message.from_user.id] = message.reply_text("در حال دانلود...")
    except Exception as e:
        message.reply_text("نمی توان این لینک را دانلود کرد")

        try:
            temp_message[message.from_user.id].delete()
        except Exception:
            logger.error(f"Error deleting message: {e}")
        return

    cl = InstaClient()

    try:
        res = cl.login(INSTAUSERNAME, INSTAPASSWORD)

        if not res:
            print("Login failed")
            return

        pk = cl.media_pk_from_url(link)

    except Exception as e:
        logger.error(f"Error logging in to instagram: {e}")

        message.reply_text("نمی توان این لینک را دانلود کرد")

        try:
            temp_message[message.from_user.id].delete()
        except Exception:
            logger.error(f"Error deleting message: {e}")
        return

    check = False
    try:
        filename_uuid = cl.clip_download(pk)
        check = True
    except Exception as e:
        check = False

    if not check:
        try:
            filename_uuid = cl.video_download(pk)
            check = True
        except Exception as e:
            check = False

    if not check:
        try:
            filename_uuid = cl.photo_download(pk)
            check = True
        except Exception as e:
            check = False

    if not check:
        try:
            filename_uuid = cl.igtv_download(pk)
            check = True
        except Exception as e:
            check = False

    if check:
        # send the file
        filename_uuid = str(filename_uuid)
        temp_message[message.from_user.id] = message.reply_text("در حال ارسال...")

        if filename_uuid[-3:] == "mp4":
            message.reply_video(filename_uuid)
        elif filename_uuid[-3:] == "jpg":
            message.reply_photo(filename_uuid)
        else:
            message.reply_document(filename_uuid)

        os.remove(filename_uuid)

        try:
            temp_message[message.from_user.id].delete()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

    if not check:
        try:
            filename_uuid = cl.album_download(pk)
            check = True

            for j in filename_uuid:
                i = str(j)
                if i[-3:] == "mp4":
                    message.reply_video(i)
                elif i[-3:] == "jpg":
                    message.reply_photo(i)
                else:
                    message.reply_document(i)

                os.remove(i)

            try:
                temp_message[message.from_user.id].delete()
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
        except Exception as e:
            check = False

    if not check:
        message.reply_text("نمی توان این لینک را دانلود کرد")


def old_instagram_download(link, message: Message, client: Client):
    logger.debug(f"Downloading instagram video from link: {link}")

    global temp_message
    try:
        # OPENING THE WEBPAGE
        temp_message[message.from_user.id] = message.reply_text("در حال دانلود...")

        logger.debug("Starting the web driver...")

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

        logger.debug("Web driver has started.")

        logger.debug("Opening the webpage...")

        driver.get("https://snapinsta.app/")

        logger.debug("Webpage has opened.")

        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            classname = button.get_dom_attribute("class")
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

        logger.debug(f"URLs found: {len(links)}")

        for link in links:
            # logger.debug(f"Checking link {i}...")
            # logger.debug(f"Link data-event: {link.get_dom_attribute('data-event')}")

            if link.get_dom_attribute("data-event") == "click_download_btn":
                try:
                    downloadLink = link.get_dom_attribute("href")

                    logger.debug(f"Download link found: {downloadLink}")

                    r = requests.get(downloadLink, allow_redirects=True)

                    content = r.headers.get("content-disposition")

                    logger.debug(f"Content-Disposition: {content}")

                    filename = content[content.find("filename=") + 9 :]
                    extention = os.path.splitext(filename)[1]
                    filename_uuid = str(uuid.uuid4()) + extention

                    logger.debug(f"Download Complete. UUID of File is: {filename_uuid}")

                    open(filename_uuid, "wb").write(r.content)

                    if filename_uuid[-3:] == "mp4":
                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                        logger.debug("Sending Video...")

                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )

                        message.reply_video(filename_uuid)

                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                    elif filename_uuid[-3:] == "jpg":
                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                        logger.debug("Sending Photo...")

                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )

                        message.reply_photo(filename_uuid)

                        logger.debug("Photo has been sent.")

                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                    logger.debug("Removing the file...")

                    os.remove(filename_uuid)

                    logger.debug("File has been removed.")

                except Exception as e:
                    logger.error(f"Error downloading file: {e}")

                counter += 1
            i += 1
        if counter == 0:
            try:
                temp_message[message.from_user.id].delete()
            except Exception as e:
                logger.error(f"Error deleting message: {e}")

            logger.debug("No download link found.")

            message.reply_text("نمی توان این لینک را دانلود کرد")
        else:
            add_link(message, "Instagram")

        try:
            temp_message[message.from_user.id].delete()
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

        logger.debug("Download complete. Closing the web driver...")

        driver.close()
    except Exception as e:
        logger.error(f"Error downloading instagram video: {e}")

        message.reply_text("نمی توان این لینک را دانلود کرد")

        try:
            temp_message[message.from_user.id].delete()
        except Exception:
            logger.error(f"Error deleting message: {e}")

    logger.debug("Web driver has closed.")


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
    temp_message[message.from_user.id] = test


def reply_back_button(text, message: Message, client: Client):
    global temp_message

    temp_message[message.from_user.id] = message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="بازگشت", callback_data="back")]]
        ),
    )
