from aiogram import Bot
from services.user_service import UserService
from services.affiliate_service import AffiliateService
from datetime import datetime, timedelta
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

class SendMessage:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def check_all_users(self):
        all_users = UserService.get_all_user()
        now = datetime.now(tz_vn)

        # 🔹 Notify new approved KOL/KOC partners
        for user in all_users:
            if isinstance(user.updated_at, str):
                try:
                    updated_at = datetime.strptime(user.updated_at, "%Y-%m-%d %H:%M:%S")
                    updated_at = tz_vn.localize(updated_at)
                except Exception as e:
                    print(f"Time parse error for user {user.id}: {e}")
                    continue
            else:
                updated_at = user.updated_at.astimezone(tz_vn)
           
            diff = now - updated_at
            if diff <= timedelta(minutes=5) and user.verified_kol == "approved":
                text = (
                    f"🌟 *Welcome aboard, our new KOL/KOC Partner!* 🌟\n\n"
                    f"Your current commission rate is *{user.commission_percent}%* 💰\n\n"
                    "We’re thrilled to have you join our growing community of creators and brand ambassadors.\n"
                    "Stay tuned for upcoming campaigns and exclusive rewards! 💼✨\n\n"
                    "_The HieuSoft Team_ ⚡"
                )
                await self.send(user.user_id, text)


        all_affiliate_withdraws = AffiliateService.get_all_withdraw()
        for withdraw in all_affiliate_withdraws:
            if isinstance(withdraw.updated_at, str):
                try:
                    updated_at = datetime.strptime(withdraw.updated_at, "%Y-%m-%d %H:%M:%S")
                    updated_at = tz_vn.localize(updated_at)
                except Exception as e:
                    print(f"Time parse error for withdraw {withdraw.user_id}: {e}")
                    continue
            else:
                updated_at = withdraw.updated_at.astimezone(tz_vn)

            diff = now - updated_at
            if diff <= timedelta(minutes=5) and withdraw.status == "approved":
                txid = withdraw.tx_hash or "No TXID available"

                text = (
                    "💸 *Payment Successful!*\n\n"
                    "Hello partner, your withdrawal request has been successfully processed. 🎉\n"
                    f"🔹 *Amount:* {withdraw.amount}\n"
                    f"🔹 *TXID:* `{txid}`\n\n"
                    "Thank you for being part of the *HieuSoft Affiliate Program*! 💼\n\n"
                    "_The HieuSoft Team_ ⚡"
                )

                await self.send(withdraw.user_id, text)

    async def send(self, user_id: int, text: str):
        try:
            await self.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")
