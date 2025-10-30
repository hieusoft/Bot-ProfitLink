from aiogram import Router, types, F
from bot.keyboards.main_menu import get_main_menu

main_menu_router = Router()

@main_menu_router.callback_query(F.data == "back_main")
async def handle_back_main(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id


    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    text = (
        "💎 *Welcome to Hieusoft Crypto Bot!*\n\n"
        "Empower your trading journey with real-time premium signals, lifetime affiliate rewards, "
        "and cashback from every trade — all in one smart bot. 🚀\n\n"
        "Choose your next action below to start earning 👇"
    )



    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )
