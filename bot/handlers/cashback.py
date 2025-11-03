from aiogram import Router, types, F
from config.translator import Translator
from services.user_service import UserService
cashback_router = Router()

@cashback_router.callback_query(F.data == "cashback")
async def open_cashback_menu(callback: types.CallbackQuery):
    user = UserService.get_user_by_telegram_id(callback.from_user.id)
    lang = getattr(user, "language", "en")
    translator = Translator(lang)

    await callback.answer(
        text=f"{translator.t('cashback.title')}",
        show_alert=True
    )
