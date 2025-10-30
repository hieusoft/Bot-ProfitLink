from aiogram import Router, types, F
from config.translator import Translator
cashback_router = Router()

@cashback_router.callback_query(F.data == "cashback")
async def open_cashback_menu(callback: types.CallbackQuery):
    translator = Translator(lang="en")

    await callback.answer(
        text=f"{translator.t('cashback.title')}",
        show_alert=True
    )
