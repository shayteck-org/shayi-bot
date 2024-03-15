import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot_name = os.getenv("BOT_NAME")
INSTAUSERNAME = os.getenv('INSTAUSERNAME')
INSTAPASSWORD = os.getenv('INSTAPASSWORD')
