from aiogram import Bot
from services.user_service import UserService
from datetime import datetime, timedelta
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

class SendMessage:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def check_all_users(self):
        all_users = UserService.get_all_user()
        now = datetime.now(tz_vn)
       
        for user in all_users:
           
            if isinstance(user.updated_at, str):
                try:
                    updated_at = datetime.strptime(user.updated_at, "%Y-%m-%d %H:%M:%S")
                    updated_at = tz_vn.localize(updated_at)
                except Exception as e:
                    print(f"Lỗi parse thời gian của user {user.id}: {e}")
                    continue
            else:
                updated_at = user.updated_at.astimezone(tz_vn)

            diff = now - updated_at
            if diff <= timedelta(minutes=5) and user.verified_kol == "approved":
                text = (
                    "🌟 *Chào mừng bạn đã trở thành đối tác KOL/KOC của chúng tôi!* 🌟\n\n"
                    "Chúng tôi rất vui mừng khi được đồng hành cùng bạn trong hành trình phát triển thương hiệu.\n"
                    "Hãy theo dõi các chiến dịch sắp tới để nhận thông tin và phần thưởng hấp dẫn 💼💰\n\n"
                    "_Đội ngũ HieuSoft_ ⚡"
                )
                await self.send(user.user_id,text)

    async def send(self, user_id: int, text: str):
        try:
            await self.bot.send_message(chat_id=user_id, text=text)
          
        except Exception as e:
            pass
