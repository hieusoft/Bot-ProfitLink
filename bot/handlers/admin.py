from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from services.user_service import UserService
from config.translator import Translator
from config.settings import settings
from aiogram.utils.markdown import hbold
import asyncio
from deep_translator import GoogleTranslator
admin_router = Router()
ADMIN_ID = settings.ADMIN_CHAT_ID  


@admin_router.message(Command("broadcast"))
async def broadcast_message(message: types.Message, command: CommandObject):
  
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("🚫 Bạn không có quyền sử dụng lệnh này.")
        return

    if not command.args:
        await message.answer("❗ Vui lòng nhập nội dung thông báo.\n\nVí dụ:\n`/broadcast Xin chào mọi người!`")
        return

    content = command.args.strip()
    users = UserService.get_all_user() 
    if not users:
        await message.answer("⚠️ Không tìm thấy user nào trong database.")
        return

    sent_count = 0
    failed_count = 0

    await message.answer(f"📢 Bắt đầu gửi thông báo tới {len(users)} người dùng...")

    for user in users:
        target_lang = normalize_lang(user.language)
        content_taget = GoogleTranslator(source='auto', target=target_lang).translate(content)
        try:
            await message.bot.send_message(
                chat_id=int(user.user_id),
                text=f"{content_taget}"
            )
            sent_count += 1
            await asyncio.sleep(0.3) 
        except Exception:
            failed_count += 1
    await message.answer(f"✅ Đã gửi tới {sent_count} user.\n❌ Lỗi khi gửi tới {failed_count} user.")
def normalize_lang(lang: str) -> str:
    """Chuyển mã ngôn ngữ Telegram / hệ thống về dạng GoogleTranslator chấp nhận"""
    lang = lang.lower()
    if lang in ("zh", "zh-cn", "cn", "ch"):
        return "zh-CN"
    elif lang in ("zh-tw", "tw", "hk"):
        return "zh-TW"
    elif lang == "vn": 
        return "vi"
    return lang