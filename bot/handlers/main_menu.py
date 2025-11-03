from aiogram import Router, types, F
from bot.keyboards.main_menu import get_main_menu
from services.user_service import UserService
from config.translator import Translator  # 🔹 Đừng quên import Translator nếu chưa có

main_menu_router = Router()
user_langs = {}

@main_menu_router.callback_query(F.data == "back_main")
async def handle_back_main(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id  # ✅ Lấy user_id đúng cách

    # 🔹 Lấy thông tin user từ database
    user = UserService.get_user_by_telegram_id(user_id)

    # 🔹 Xác định ngôn ngữ người dùng (ưu tiên DB)
    lang = getattr(user, "language", "en") if user else "en"
    user_langs[user_id] = lang  # Lưu cache tạm (nếu muốn dùng lại sau)

    translator = Translator(lang=lang)

    # 🔹 Xóa tin nhắn cũ (nếu có)
    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    # 🔹 Nội dung chính (có thể dịch theo lang)
    
    text = f"{translator.t('start.intro')}"

    # 🔹 Gửi lại main menu
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_main_menu(lang)
    )
