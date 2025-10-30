import os
from dotenv import load_dotenv

# Load file .env (đặt ở gốc dự án)
load_dotenv()

class Settings:
    

    def __init__(self):
      
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "")
        self.URL_BOT = os.getenv("URL_BOT", "")
        self.ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
        self.MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
        self.MYSQL_USER = os.getenv("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
        self.MYSQL_DB = os.getenv("MYSQL_DB", "telegram_bot_system")
        self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        self.MAX_PAGE_LENGTH = int(os.getenv("MAX_PAGE_LENGTH",1000))
        self.OXAPAY_API_KEY = os.getenv("OXAPAY_API_KEY", "")
        self.CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN", "")

        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

settings = Settings()
