#Importing dependencies
import datetime
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
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
from mysql.connector import connect
# Create a new Pyrogram client

load_dotenv("Config.env")
api_id =  os.getenv("api_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")
bot_name = os.getenv("bot_name")



app = Client('bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)
conn = sqlite3.connect('BotDatabase.db')
####################################################################################################
# CONFIGURATIONS
connection = connect(
  host="localhost",
  user="username",
  password="password"
)

cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS downloader") 
connection.commit()
cursor.close()
connection.close() 
connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
cursor = connection.cursor()
# cursor.execute("DROP TABLE user")
# cursor.execute("DROP TABLE userData")
# cursor.execute("DROP TABLE admin")
# cursor.execute("DROP TABLE savedFile")
print("test")
cursor.execute("CREATE TABLE if not exists user (telegramID BIGINT,firstMessage TIMESTAMP,lastMessage TIMESTAMP,userName TEXT)")
cursor.execute("CREATE TABLE if not exists admin (ID BIGINT)")
cursor.execute("CREATE TABLE if not exists link (telegramID BIGINT, linkType TEXT,link TEXT)")

cursor.execute("SELECT * FROM user")
users = cursor.fetchall()
print(users)
cursor.execute("SELECT * FROM admin")
admins = cursor.fetchall()
print(admins)
if(len(admins)==0):
    pass
    cursor.execute("INSERT INTO admin VALUES (%s);",(368783021,))
cursor.execute("SELECT * FROM link")
links = cursor.fetchall()    
print(links)
# cursor.execute("INSERT INTO user VALUES (%s, %s, %s,%s);",(10000000000,datetime.datetime.now(),datetime.datetime.now(),"@test1",))


connection.commit()
cursor.close()
connection.close() 
def get_user_id(message):
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        # print(message.text)
        cursor.execute("SELECT * FROM user WHERE username = %s", (message.text[1:],))
        user=cursor.fetchone()
        # Extract the username from the message text
        if user is None:
            return None
            
        return user[0]
    except Exception as e:
        # Handle cases where the username is missing or incorrect
        print(e)
        return None
def days_between(d1, d2):
    return ((d1 - d2).total_seconds())/86400 
def addLink(message,linkType):
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)   
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO link VALUES (%s, %s,%s);",(message.chat.id,linkType,message.text,))    
        connection.commit()
        cursor.close()     
        connection.close()
    except Exception as e:
        print(e)
        pass    
def updateUsers(message):
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE telegramID  = %s", (message.from_user.id,))
        user= cursor.fetchone()
        if user is None:
            cursor.execute("INSERT INTO user VALUES (%s, %s, %s,%s);",(message.from_user.id,datetime.datetime.now(),datetime.datetime.now(),message.from_user.username,))
        else:
            cursor.execute("UPDATE user SET firstMessage = %s WHERE telegramID = %s",(datetime.datetime.now(), message.from_user.id)) 
            cursor.execute("UPDATE user SET username = %s WHERE telegramID  = %s",(message.from_user.username, message.from_user.id))
        connection.commit()
        cursor.close()     
        connection.close()  
    except Exception as e:
        print(e)
        pass
def getAllUsers():
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
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
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
        weeklyUsers = []
    
        for user in users:
            if days_between(datetime.datetime.now(),user[2])<=7:
                weeklyUsers.append(user)
        cursor.close()     
        connection.close()  
        return weeklyUsers
    except Exception as e:
        print(e) 
def getMonthlyUsers():
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
        weeklyUsers = []
    
        for user in users:
            if days_between(datetime.datetime.now(),user[2])<=30:
                weeklyUsers.append(user)
        cursor.close()     
        connection.close()  
        return weeklyUsers
    except Exception as e:
        print(e) 
def getWeeklyNewUsers():
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
        weeklyUsers = []
    
        for user in users:
            if days_between(datetime.datetime.now(),user[1])<=7:
                weeklyUsers.append(user)
        cursor.close()     
        connection.close()  
        return weeklyUsers
    except Exception as e:
        print(e)  
def getMonthlyNewUsers():
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
        weeklyUsers = []
    
        for user in users:
            if days_between(datetime.datetime.now(),user[1])<=30:
                weeklyUsers.append(user)
        cursor.close()     
        connection.close()  
        return weeklyUsers
    except Exception as e:
        print(e)
def checkAdmin(id):
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        print(id)
        cursor.execute("SELECT * FROM admin WHERE ID = %s", (id,))
        user=cursor.fetchone()
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
            message.reply( "بات ما یوزری با این ای دی ندارد")
            return False
        if (checkAdmin(id) == True):
            message.reply( "این یوزر از قبل ادمین است")
            return True
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO admin VALUES (%s);",(id,))
        connection.commit()
        cursor.close()     
        connection.close() 
        message.reply( "یوزر با موفقیت ادمین شد")
        return True
    except Exception as e:
        print(e) 
        pass 
def removeAdmin(message):
    try:
        id = get_user_id(message)
        
        if id is None:
            message.reply( "بات ما یوزری با این ای دی ندارد")
            return False
        if (checkAdmin(id) == True):
            connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM admin WHERE ID = %s",(id,))
            connection.commit()
            cursor.close()     
            connection.close() 
            message.reply( "یوزر با موفقیت از ادمینی درآمد")
            return True
        message.reply("این یوزر ادمین نیست")
        return True
    except Exception as e:
        print(e) 
        pass    
def getAllAdmins():
    try:
        connection = connect(
  host="localhost",
  user="username",
  password="password",
  database="downloader"
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
                if(admin[0]==user[0]):
                    text += str(admin[0])
                    text += " : "
                    text += "@"+user[3]
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
  host="localhost",
  user="username",
  password="password",
  database="downloader"
)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        users= cursor.fetchall()
        for user in users:
            # print(int(user[0]))
            # print(user[3])
            try:
                
                client.copy_message(int(user[0]),message.from_user.id,message.id)
            except Exception as e:
                # print(e)
                pass
        cursor.close()     
        connection.close()  
        
    except Exception as e:
        print(e)
        pass                    
print(getWeeklyUsers())          
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
        temp_message[message.from_user.id] = message.reply_text("در حال دانلود...")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        options.add_experimental_option("excludeSwitches",["enable-automaion"])
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
                        temp_message[message.from_user.id].delete()
                        temp_message[message.from_user.id] = message.reply_text("در حال ارسال...")
                        message.reply_video(filename)
                        temp_message[message.from_user.id].delete()
                    elif(filename[-3:]=="jpg"):
                        temp_message[message.from_user.id].delete()
                        temp_message[message.from_user.id] = message.reply_text("در حال ارسال...")
                        message.reply_photo(filename)
                        temp_message[message.from_user.id].delete()
                    os.remove(filename)
                except Exception as e:
                    print(e)
                    pass
                counter += 1
            i+=1
        if counter==0:
            temp_message[message.from_user.id].delete()
            message.reply_text("نمی توان این لینک را دانلود کرد")
        else:
            addLink(message,"Instagram")
        temp_message[message.from_user.id].delete()
        print("download done")
        driver.close()
    except Exception as e:
        print(e)
        print("couldn't download this link")
        temp_message[message.from_user.id].delete()
    pass


def reply_buttons(text, message: Message, client: Client):
    global temp_message
    test= message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="دانلود از اینستاگرام", callback_data="insta"),
             InlineKeyboardButton(text="دانلود از یوتوب", callback_data="youtube")]
        ]
    ))
    # print(test)
    # test.delete()
    temp_message[message.from_user.id] = test
    print(message.from_user.id)
    # print(temp_message[message.from_user.id])




def reply_back_button(text, message: Message, client: Client):
    global temp_message

    temp_message[message.from_user.id] = message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="بازگشت", callback_data="back")]
        ]
    ))


users = {}
links = {}
qualities = {}
temp_message = dict()


##############################################################################################################
# FUNCTIONALITIES BY ORDER


@app.on_message(filters.command("start"))
def start_handler(client: Client, message: Message):
    updateUsers(message)
    print("started by " + message.from_user.username)
    global temp_message
    users[message.from_user.id] = "start"
    text = "سلام خوش اومدی! \n من میتونم برات از اینستاگرام و یوتوب دانلود کنم😎 \n" \
           " کافیه لینک ویدیوی یوتوب یا هر چیزی تو اینستا مثل استوری،پست، igtv و reel رو بفرستی تا فایلشو واست بفرستم🫡🤌"
    reply_buttons(text, message, client)
@app.on_message(filters.command("adminpanel"))
def adminPanel(client: Client, message: Message):
    try:
        if(checkAdmin(message.chat.id)!= True):
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
            keyboard = ReplyKeyboardMarkup([
            ["تعداد تمام یوزر ها"],
            ["تعداد یوزر های فعال هفته گذشته"],
            ["تعداد یوزر های فعال ماه گذشته"],
            ["تعداد یوزر های جدید هفته گذشته"],
            ["تعداد یوزر های جدید ماه گذشته"],
            ["لیست ادمین ها"],
            ["اضافه کردن ادمین"],
            ["حذف ادمین"],
            ["پیام همگانی"],
            ["کنسل کردن درخواست"]
           
            ])
            print("test")
            # client.send_message(message.from_user.id,"پنل ادمینی برای شما فعال شد" , reply_markup = keyboard,reply_to_message_id=message.id)
            message.reply("پنل ادمینی برای شما فعال شد" , reply_markup = keyboard)
    except Exception as e:
        print(e.with_traceback)
        print(e)
@app.on_callback_query()
def call_back_handler(client: Client, callback: CallbackQuery):
    global temp_message
    if callback.data == "youtube":
        temp_message[callback.message.chat.id].delete()
        users[callback.from_user.id] = callback.data
        temp_message[callback.message.chat.id] = callback.message.reply_text("لطفا لینک ویدیوی یوتوب رو بفرست🙏")

    elif callback.data == "insta":
        
        temp_message[callback.message.chat.id].delete()
        users[callback.from_user.id] = callback.data
        temp_message[callback.message.chat.id] = callback.message.reply_text("لطفا لینک ویدیوی اینستاگرام رو بفرست🙏")

    elif callback.data == "back":
        temp_message[callback.message.chat.id].delete()
        users[callback.from_user.id] = ""
        text = "چه کار دیگه ای میتونم برات انجام بدم؟🤔"
        reply_buttons(text, callback.message, client)

    else:

        temp_message[callback.message.chat.id].delete()
        ID = callback.from_user.id
        users[ID] = "download"

        title = youtube_download(link=links[ID], res=callback.data, message=callback.message, client=client)
        sent_message = callback.message.reply_text("با موفقیت دانلود شد، در حال ارسال...")

        special_characters = r'\/:*?"<>|#'
        path = ''.join(char for char in title if char not in special_characters) + ".mp4"
        print(path)

        callback.message.reply_video(video=path)
        addLink(callback.message,"YouTube")
        sent_message.delete()

        reply_back_button(text="بازگشت؟",message=callback.message, client=client)

        os.remove(path=path)
        print(path, "has been successfully deleted.")




@app.on_message(filters.text)
def message_handler(client: Client, message: Message):
    global temp_message
    updateUsers(message)
    if (message.text == "تعداد تمام یوزر ها"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getAllUsers())
            text = "تعداد تمامی یوزر ها :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif (message.text == "تعداد یوزر های فعال هفته گذشته"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getWeeklyUsers())
            text = "تعداد یوزر های فعال هفته گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif (message.text == "تعداد یوزر های فعال ماه گذشته"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyUsers())
            text = "تعداد یوزر های فعال ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)
    elif (message.text == "تعداد یوزر های جدید هفته گذشته"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getWeeklyNewUsers())
            text = "تعداد یوزر های جدید هفته گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)  
    elif (message.text == "تعداد یوزر های جدید ماه گذشته"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyNewUsers())
            text = "تعداد یوزر های جدید ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)       
    elif (message.text == "تعداد یوزر های جدید ماه گذشته"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            userNumber = len(getMonthlyNewUsers())
            text = "تعداد یوزر های جدید ماه گذشته :"
            text += "\n"
            text += str(userNumber)
            message.reply(text)  
    elif (message.text == "لیست ادمین ها"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            text = getAllAdmins()
            message.reply(text)
    elif (message.text == "اضافه کردن ادمین"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply("لطفا آی دی تلگرام کسی که می خواهید ادمین کنید را وارد کنید")   
            users[message.from_user.id] = "addAdmin"
    elif (message.text == "حذف ادمین"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply("لطفا آی دی تلگرام کسی که می خواهید از ادمینی برکنار کنید را وارد کنید")   
            users[message.from_user.id] = "removeAdmin" 
    elif (message.text == "پیام همگانی"):
        if(checkAdmin(message.from_user.id) != True):
            message.reply("فقط ادمین ها می توانند از این دستور استفاده کنند")
        else:
            message.reply("پیام بعدی شما به همه ی یوزر ها خواهد رفت")   
            users[message.from_user.id] = "globalMessage" 
    elif (message.text == "کنسل کردن درخواست"):
        users[message.from_user.id] = "" 
    elif users[message.from_user.id] == "globalMessage":
        sendGlobalMessage(message,client)   
        users[message.from_user.id] = ""  
    elif (users[message.from_user.id] == "addAdmin"):
        promoteToAdmin(message,client)
        users[message.from_user.id] = ""
    elif (users[message.from_user.id] == "removeAdmin"):
        removeAdmin(message)
        users[message.from_user.id] = ""
    elif users[message.from_user.id] == "insta":
        temp_message[message.from_user.id].delete()
        instagram_download(message.text, message, client)
        reply_back_button(text="بازگشت؟",message=message, client=client)

    elif users[message.from_user.id] == "youtube":
        if "youtube.com" in message.text or "youtu.be" in message.text:
            temp_message[message.from_user.id].delete()
            video_url = message.text
            yt = YouTube(video_url)
            print("Available resolutions:")
            resolutions = []

            for stream in yt.streams.filter(progressive=True):
                print(stream.resolution)
                resolution_button = [InlineKeyboardButton(text=stream.resolution,callback_data=stream.resolution)]
                resolutions.append(resolution_button)

            txt = "یکی از کیفیت های موجود رو انتخاب کن. " + "\n"
            temp_message[message.from_user.id] = message.reply_text(text=txt, reply_markup=InlineKeyboardMarkup(resolutions))

            users[message.from_user.id] = "ytquality"
            links[message.from_user.id] = message.text
            qualities[message.from_user.id] = resolutions

        else:
            text = "لینک اشتباه است، دوباره وارد کنید."
            text += "\n \n"
            text += "بازگشت؟"
            reply_buttons(text=text, message=message, client=client)


# Run the bot
print("BOT IS ON")
app.run()
print("BOT IS OFF")
