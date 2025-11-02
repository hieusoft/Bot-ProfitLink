from aiogram import Router, types, F
from datetime import datetime
from bot.keyboards.language_menu import get_language_menu
from config.settings import settings
from config.translator import Translator
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
language_router = Router()
URL_BOT = settings.URL_BOT


@language_router.callback_query(F.data == "language")
async def open_language_menu(callback: types.CallbackQuery):
 
    try:
       
        await callback.message.delete()
    except Exception:
      
        pass

    await callback.message.answer(
        text="🌐 Please choose your language / Vui lòng chọn ngôn ngữ:",
        reply_markup=get_language_menu()
    )

    
    await callback.answer()
