from aiogram import Router, types, F
from datetime import datetime
from bot.keyboards.language_menu import get_language_menu
from config.settings import settings
from config.translator import Translator
import pytz
from services.user_service import UserService

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
language_router = Router()
URL_BOT = settings.URL_BOT


@language_router.callback_query(F.data == "language")
async def open_language_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = UserService.get_user_by_telegram_id(user_id)
    lang = getattr(user, "language", "en")

    translator = Translator(lang)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        text=translator.t("language.title"),
        reply_markup=get_language_menu(lang)
    )
    await callback.answer()


# ✅ Hàm xử lý khi người dùng chọn ngôn ngữ
@language_router.callback_query(F.data.startswith("lang_"))
async def change_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data 
    new_lang = data.split("_")[1]  
    UserService.update_language(user_id,new_lang)



    
    translator = Translator(new_lang)

    try:
        await callback.message.edit_text(
            text=f"{translator.t('language.changed')}",
            reply_markup=get_language_menu(new_lang)
        )
    except Exception:
        await callback.message.answer(
            text=f"{translator.t('language.changed')}",
            reply_markup=get_language_menu(new_lang)
        )

    await callback.answer()
