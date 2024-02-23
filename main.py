#Importing dependencies
from pytube import*
from pyrogram import*
from pyrogram.types import*
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium import*
from selenium.webdriver.common.keys import Keys
import time
import requests
import os
from dotenv import*


# Create a new Pyrogram client

load_dotenv("Config.env")
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")
bot_name = os.getenv("bot_name")


app = Client(name=bot_name, api_id=api_id, api_hash=api_hash, bot_token=bot_token)

####################################################################################################
# CONFIGURATIONS

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
    try:
        # OPENING THE WEBPAGE
        global temp_message
        temp_message = message.reply_text("در حال دانلود...")
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_experimental_option("excludeSwitches",["enable-automaion"])
        options.binary_location = '/usr/bin/google-chrome'
        driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=options)
        stealth(driver,languages=["en-US","en"],vendor="Google Inc",platform="Linux64",webgl_vendor="Intel Inc",renderer="Intel Iris OpenGL Engine", fix_hairline= True,)
        driver.get("https://snapinsta.app/")
        buttons = driver.find_elements(By.TAG_NAME,"button")
        for button in buttons:
            classname = button.get_dom_attribute("class")
            print(classname)
            if(classname=="fc-button fc-cta-consent fc-primary-button"):
                button.click()
                break
        time.sleep(2)

        #target username
        username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='url']")))

        #enter username and password
        username.clear()
        username.send_keys(link)

        #target the login button and click it
        button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        time.sleep(10)
        links = driver.find_elements(By.TAG_NAME,"a")
        i = 0
        counter = 0
        for link in links:
            print(i)
            print(link.get_dom_attribute("data-event"))
            if(link.get_dom_attribute("data-event")=="click_download_btn"):
                try:
                    downloadLink =  link.get_dom_attribute("href")
                    print(downloadLink)
                    r = requests.get(downloadLink, allow_redirects=True)
                    content = r.headers.get('content-disposition')
                    print(content)
                    filename=content[content.find("filename=")+9:]
                    print(filename)
                    open(filename,"wb").write(r.content)
                    if(filename[-3:]=="mp4"):
                        temp_message = message.reply_text("در حال ارسال...")
                        message.reply_video(filename)
                        temp_message.delete()
                    elif(filename[-3:]=="jpg"):
                        temp_message = message.reply_text("در حال ارسال...")
                        message.reply_photo(filename)
                        temp_message.delete()
                    os.remove(filename)
                except Exception as e:
                    print(e)
                    pass
                counter += 1
            i+=1
        if counter==0:
            temp_message.delete()
            message.reply_text("نمی توان این لینک را دانلود کرد")
        temp_message.delete()
        print("download done")
        driver.close()
    except Exception as e:
        print(e)
        print("couldn't download this link")
        temp_message.delete()
    pass


def reply_buttons(text, message: Message, client: Client):
    global temp_message
    temp_message = message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="دانلود از اینستاگرام", callback_data="insta"),
             InlineKeyboardButton(text="دانلود از یوتوب", callback_data="youtube")]
        ]
    ))



def reply_back_button(text, message: Message, client: Client):
    global temp_message

    temp_message = message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="بازگشت", callback_data="back")]
        ]
    ))


users = {}
links = {}
qualities = {}
temp_message = None

##############################################################################################################
# FUNCTIONALITIES BY ORDER


@app.on_message(filters.command("start"))
def start_handler(client: Client, message: Message):
    print("started by " + message.from_user.username)
    global temp_message
    users[message.from_user.id] = "start"
    text = "سلام خوش اومدی! \n من میتونم برات از اینستاگرام و یوتوب دانلود کنم😎 \n" \
           " کافیه لینک ویدیوی یوتوب یا هر چیزی تو اینستا مثل استوری،پست، igtv و reel رو بفرستی تا فایلشو واست بفرستم🫡🤌"
    reply_buttons(text, message, client)


@app.on_callback_query()
def call_back_handler(client: Client, callback: CallbackQuery):
    global temp_message
    if callback.data == "youtube":
        temp_message.delete()
        users[callback.from_user.id] = callback.data
        temp_message = callback.message.reply_text("لطفا لینک ویدیوی یوتوب رو بفرست🙏")

    elif callback.data == "insta":
        temp_message.delete()
        users[callback.from_user.id] = callback.data
        temp_message = callback.message.reply_text("لطفا لینک ویدیوی اینستاگرام رو بفرست🙏")

    elif callback.data == "back":
        temp_message.delete()
        users[callback.from_user.id] = ""
        text = "چه کار دیگه ای میتونم برات انجام بدم؟🤔"
        reply_buttons(text, callback.message, client)

    else:

        temp_message.delete()
        ID = callback.from_user.id
        users[ID] = "download"

        title = youtube_download(link=links[ID], res=callback.data, message=callback.message, client=client)
        sent_message = callback.message.reply_text("با موفقیت دانلود شد، در حال ارسال...")

        special_characters = r'\/:*?"<>|#'
        path = ''.join(char for char in title if char not in special_characters) + ".mp4"
        print(path)

        callback.message.reply_video(video=path)
        sent_message.delete()

        reply_back_button(text="بازگشت؟",message=callback.message, client=client)

        os.remove(path=path)
        print(path, "has been successfully deleted.")




@app.on_message(filters.text)
def message_handler(client: Client, message: Message):
    global temp_message
    if users[message.from_user.id] == "insta":
        temp_message.delete()
        instagram_download(message.text, message, client)
        reply_back_button(text="بازگشت؟",message=message, client=client)

    elif users[message.from_user.id] == "youtube":
        if "youtube.com" in message.text or "youtu.be" in message.text:
            temp_message.delete()
            video_url = message.text
            yt = YouTube(video_url)
            print("Available resolutions:")
            resolutions = []

            for stream in yt.streams.filter(progressive=True):
                print(stream.resolution)
                resolution_button = [InlineKeyboardButton(text=stream.resolution,callback_data=stream.resolution)]
                resolutions.append(resolution_button)

            txt = "یکی از کیفیت های موجود رو انتخاب کن. " + "\n"
            temp_message = message.reply_text(text=txt, reply_markup=InlineKeyboardMarkup(resolutions))

            users[message.from_user.id] = "ytquality"
            links[message.from_user.id] = message.text
            qualities[message.from_user.id] = resolutions

        else:
            text = "لینک اشتباه است، دوباره وارد کنید."
            text += "\n \n"
            text += "بازگشت؟"
            reply_buttons(text=text, message=message, client=client)


# Run the bot
app.run()