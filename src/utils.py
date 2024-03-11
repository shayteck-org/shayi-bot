import logging
import os
import time

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


from db import add_link

logger = logging.getLogger(__name__)

temp_message = dict()


def youtube_download(link, res, message: Message, client: Client):
    logger.debug(f"Downloading youtube video from link: {link}")

    video_url = link
    yt = YouTube(video_url)
    title = yt.title

    selected_stream = yt.streams.filter(res=res, progressive=True).first()

    logger.debug(f"Downloading video with title: {title}")

    sent_message = message.reply_text("در حال دانلود...")

    selected_stream.download()

    logger.debug(f"Downloaded the video with title: {title}")

    sent_message.delete()

    return title


def instagram_download(link, message: Message, client: Client):
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

        for link in links:
            logger.debug(f"Checking link {i}...")
            logger.debug(f"Link data-event: {link.get_dom_attribute('data-event')}")

            if link.get_dom_attribute("data-event") == "click_download_btn":
                try:
                    downloadLink = link.get_dom_attribute("href")

                    logger.debug(f"Download link found: {downloadLink}")

                    r = requests.get(downloadLink, allow_redirects=True)

                    content = r.headers.get("content-disposition")

                    logger.debug(f"Content-Disposition: {content}")

                    filename = content[content.find("filename=") + 9 :]

                    logger.debug(f"Filename: {filename}")

                    open(filename, "wb").write(r.content)

                    if filename[-3:] == "mp4":
                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )

                        message.reply_video(filename)

                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                    elif filename[-3:] == "jpg":
                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                        temp_message[message.from_user.id] = message.reply_text(
                            "در حال ارسال..."
                        )

                        message.reply_photo(filename)

                        try:
                            temp_message[message.from_user.id].delete()
                        except Exception as e:
                            logger.error(f"Error deleting message: {e}")

                    os.remove(filename)

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
