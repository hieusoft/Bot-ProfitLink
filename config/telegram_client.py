from telethon import TelegramClient
from config.settings import settings

import os,asyncio
API_ID = settings.API_ID
API_HASH = settings.API_HASH
SESSION_FILE = settings.SESSION_FILE

def get_telegram_client() -> TelegramClient:
  
    return TelegramClient(SESSION_FILE, API_ID, API_HASH)


