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
    get_all_users_state,
    update_user_state,
    get_single_user_state,
)

from logger import user_log, admin_log
from constants import API_ID, API_HASH, BOT_TOKEN, INSTAUSERNAME, INSTAPASSWORD

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

usernamesInsta = []
instaCl = None

# users = get_all_users_state()
links = {}
qualities = {}
temp_message = dict()

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def setUserState(id, state):
    update_user_state(id, state)


def getUserState(id):
    return get_single_user_state(id)


@app.on_message(filters.command("start"))
def start_handler(client: Client, message: Message):
    user_log(f"User {message.from_user.id} has started the bot")

    try:
        update_users(message)

        global temp_message
        setUserState(message.from_user.id, "start")

        text = (
            "سلام خوش اومدی! \n من میتونم برات از اینستاگرام و یوتوب دانلود کنم😎 \n"
            " کافیه لینک ویدیوی یوتوب یا هر چیزی تو اینستا مثل استوری،پست، igtv و reel رو بفرستی تا فایلشو واست بفرستم🫡🤌"
        )

        reply_buttons(text, message, client)
    except Exception as e:
        logger.error(f"Error while starting the bot: {e}")


def resetInstacl():
    try:
        global instaCl
        instaCl = getClientLogin()
    except Exception as e:
        logger.error(f"Error while resetting insta client: {e}")


@app.on_message(filters.command("adminpanel"))
def adminPanel(client: Client, message: Message, back=False):
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
                    ["مدیریت یوزر های اینستاگرام"],
                    ["کنسل کردن درخواست"],
                ]
            )

            # client.send_message(message.from_user.id,"پنل ادمینی برای شما فعال شد" , reply_markup = keyboard,reply_to_message_id=message.id)
            if back:
                message.reply("بازگشت به پنل ادمین", reply_markup=keyboard)
            else:
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

            setUserState(callback.from_user.id, "youtube")

            temp_message[callback.message.chat.id] = callback.message.reply_text(
                "لطفا لینک ویدیوی یوتوب رو بفرست🙏"
            )
        elif callback.data == "insta":
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            setUserState(callback.from_user.id, "insta")

            temp_message[callback.message.chat.id] = callback.message.reply_text(
                "لطفا لینک ویدیوی اینستاگرام رو بفرست🙏"
            )
        elif callback.data == "back":
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            setUserState(callback.from_user.id, "start")
            text = "چه کار دیگه ای میتونم برات انجام بدم؟🤔"

            reply_buttons(text, callback.message, client)
        elif callback.data == "deleteinstauser":
            delete_insta_user(client, callback)
        elif callback.data == "addinstauser":
            add_insta_user(client, callback)
        else:
            try:
                temp_message[callback.message.chat.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            ID = callback.from_user.id
            setUserState(ID, "download")

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

            setUserState(callback.from_user.id, "start")
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


@app.on_message(filters.video | filters.photo)
def media_handler(client: Client, message: Message):
    user_log(f"User {message.from_user.id} has sent a media")

    try:
        global temp_message

        update_users(message)

        if getUserState(message.from_user.id) == "globalMessage":
            send_global_message(message, client)
            setUserState(message.from_user.id, "start")
            return
        else:
            return
    except Exception as e:
        logger.error(f"Error while handling media: {e}")

        message.reply_text("مشکلی پیش آمده است، لطفا دوباره تلاش کنید.")


def add_insta_user(client: Client, callback: CallbackQuery):
    setUserState(callback.from_user.id, "addinstauser")

    client.send_message(
        callback.from_user.id,
        'لطفا یوزر و پسورد اینستاگرام را وارد کنید به فرمت زیر: \n "user pass"',
    )


def delete_insta_user(client: Client, callback: CallbackQuery):
    setUserState(callback.from_user.id, "deleteinstauser")
    filename = "data/insta_users.txt"
    iusers: list[list[str]] = []
    with open(filename, "r") as file:
        data = file.readlines()  # each line = 'user pass'
        if len(data) > 0:
            for line in data:
                line = line.split(" ")
                iusers.append(line)
    options = []
    for i in iusers:
        options.append([i[0]])

    options.append(["کنسل کردن درخواست"])
    kb = ReplyKeyboardMarkup(options)

    kb.resize_keyboard = True

    client.send_message(
        callback.from_user.id,
        "لطفا نام کاربری یوزر مورد نظر را برای حذف انتخاب کنید",
        reply_markup=kb,
    )


def manageInstagramUsers(client: Client, message: Message):
    try:
        filename = "data/insta_users.txt"
        iusers: list[list[str]] = []
        with open(filename, "r") as file:
            data = file.readlines()  # each line = 'user pass'
            if len(data) > 0:
                for line in data:
                    line = line.split(" ")
                    iusers.append(line)

        if len(iusers) == 0:
            message.reply_text("هیچ یوزری وارد نشده است")
            return

        text = "لیست یوزر های اینستاگرام"
        text += "\n"
        for user in iusers:
            text += user[0] + " : " + user[1]
            text += "\n\n"
        message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="حذف یوزر", callback_data="deleteinstauser"
                        ),
                        InlineKeyboardButton(
                            text="افزودن یوزر", callback_data="addinstauser"
                        ),
                    ]
                ]
            ),
        )
        return

    except Exception as e:
        logger.error(f"Error while managing instagram users: {e}")

        message.reply_text("مشکلی پیش آمده است، لطفا دوباره تلاش کنید.")


@app.on_message(filters.text)
def message_handler(client: Client, message: Message):
    try:
        user_log(f"User {message.from_user.id} has sent a message: {message.text}")

        global temp_message

        update_users(message)

        if getUserState(message.from_user.id) == "globalMessage":
            send_global_message(message, client)
            setUserState(message.from_user.id, "start")
            return

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
                setUserState(message.from_user.id, "addAdmin")

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
                setUserState(message.from_user.id, "removeAdmin")

        elif message.text == "پیام همگانی":
            if not check_admin(message.from_user.id):
                message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")

                logger.warn(
                    f"{message.from_user.id} tried to send a global message without being an admin"
                )
            else:
                message.reply("پیام بعدی شما به همه ی یوزر ها خواهد رفت")
                setUserState(message.from_user.id, "globalMessage")

        elif message.text == "مدیریت یوزر های اینستاگرام":
            manageInstagramUsers(client, message)

        elif message.text == "کنسل کردن درخواست":
            setUserState(message.from_user.id, "start")
            if check_admin(message.from_user.id):
                adminPanel(client, message, True)

        elif getUserState(message.from_user.id) == "globalMessage":
            send_global_message(message, client)
            setUserState(message.from_user.id, "start")

        elif getUserState(message.from_user.id) == "addAdmin":
            promote_to_admin(message, client)
            setUserState(message.from_user.id, "start")

        elif getUserState(message.from_user.id) == "removeAdmin":
            remove_admin(message)
            setUserState(message.from_user.id, "start")

        elif getUserState(message.from_user.id) == "insta":
            try:
                temp_message[message.from_user.id].delete()
            except Exception as e:
                logger.error("Error while deleting temp message", e)

            logger.info(
                f"User {message.from_user.id} has sent an Instagram link: {message.text}"
            )

            instagram_download(message.text, message, client)
            reply_back_button(text="بازگشت؟", message=message, client=client)

        elif getUserState(message.from_user.id) == "youtube":
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

                setUserState(message.from_user.id, "ytquality")
                links[message.from_user.id] = message.text
                qualities[message.from_user.id] = resolutions
            else:
                text = "لینک اشتباه است، دوباره وارد کنید."
                text += "\n \n"
                text += "بازگشت؟"
                reply_buttons(text=text, message=message, client=client)
        elif getUserState(message.from_user.id) == "addinstauser":
            message.text = message.text.strip()
            check = message.text.split(" ")
            if len(check) != 2:
                message.reply_text("فرمت اشتباه است")
                return
            filename = "data/insta_users.txt"
            with open(filename, "a") as file:
                file.write(message.text + "\n")
            message.reply_text("یوزر اضافه شد")
            setUserState(message.from_user.id, "start")

            manageInstagramUsers(client, message)

        elif getUserState(message.from_user.id) == "deleteinstauser":
            username = message.text.strip()

            filename = "data/insta_users.txt"
            iusers: list[str] = []
            c = False
            with open(filename, "r") as file:
                data = file.readlines()
                if len(data) > 0:
                    for line in data:
                        linecheck = line.split(" ")
                        if linecheck[0] == username:
                            c = True
                            continue
                        iusers.append(line)

            with open(filename, "w") as file:
                for i in iusers:
                    file.write(i)

            if c:
                message.reply_text("یوزر حذف شد")
                manageInstagramUsers(client, message)
            else:
                message.reply_text("یوزر یافت نشد دوباره تلاش کنید")

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

    try:
        global instaCl
        if instaCl == None:
            cl = getClientLogin(usernamesInsta)

            if cl == None:
                logger.error("Login failed")
                return
            instaCl = cl

        else:
            cl = instaCl

        checkreset = False
        while True:
            try:
                pk = cl.media_pk_from_url(link)
                break
            except Exception as e:
                logger.error(f"Error getting pk: {e}")
                if checkreset:
                    break
                checkreset = True
                resetInstacl()
                cl = instaCl
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

        try:
            os.remove(filename_uuid)

        except Exception as e:
            logger.error(f"Error deleting file: {e}")

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

                try:
                    os.remove(i)
                except Exception as e:
                    logger.error(f"Error deleting file: {e}")
            try:
                temp_message[message.from_user.id].delete()
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
        except Exception as e:
            check = False

    if not check:
        message.reply_text("نمی توان این لینک را دانلود کرد")
    else:
        setUserState(message.from_user.id, "start")


def getClientLogin(usernames: list = None):
    curent_username = ""
    try:
        filename = "data/insta_users.txt"

        with open(filename, "r") as file:
            data = file.readlines()  # each line = 'user pass'
            if len(data) == len(usernames):
                return None

            if len(data) > 0:
                for line in data:
                    line = line.split()
                    if len(line) == 2:
                        if usernames is not None and line[0] in usernames:
                            continue
                        cl = InstaClient()
                        curent_username = line[0]
                        print(f"Logging in with {line[0]}")
                        success = cl.login(line[0], line[1])
                        if success:
                            return cl

                return None
            else:
                return None
    except Exception as e:
        logger.error(f"Error getting client login: {e} /user {curent_username}")
        if usernames is not None:
            usernames.append(curent_username)
            return getClientLogin(usernames)
        else:
            return getClientLogin([curent_username])


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
