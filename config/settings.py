import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    

    def __init__(self):
      
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "e")
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
        self.ADD_LIST = os.getenv("ADD_LIST", "")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")
        self.API_ID = int(os.getenv("TELEGRAM_API_ID", "123456"))
        self.API_HASH = os.getenv("TELEGRAM_API_HASH", "your_api_hash_here")
        self.SESSION_FILE = os.getenv("TELEGRAM_SESSION", "bot_session")
        self.DISCOUNT=int(os.getenv("DISCOUNT", 10))
        self.MAX_CONNECTION =int(os.getenv("MAX_CONNECTION", 20))
        self.CHANNEL_LIST=os.getenv("CHANNEL_LIST", "")
        self.URL_SUPPORT=os.getenv("URL_SUPPORT", "")

settings = Settings()
