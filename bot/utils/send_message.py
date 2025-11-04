from aiogram import Bot
from services.user_service import UserService
from services.affiliate_service import AffiliateService
from datetime import datetime, timedelta
from config.translator import Translator
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

class SendMessage:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def check_all_users(self):
        all_users = UserService.get_all_user()
        now = datetime.now(tz_vn).replace(tzinfo=None) 

        for user in all_users:
        
            if isinstance(user.updated_at, str):
                try:
                    updated_at = datetime.strptime(user.updated_at, "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"Time parse error for user {user.user_id}: {e}")
                    continue
            else:
                updated_at = user.updated_at  
            diff = now - updated_at

            if diff <= timedelta(minutes=5):
                translator = Translator(getattr(user, "language", "en"))
                text = None

                
                created_at_vn = (
                    datetime.strptime(user.created_at, "%Y-%m-%d %H:%M:%S")
                    if isinstance(user.created_at, str)
                    else user.created_at
                )

                if user.verified_kol == "approved":
                    text = translator.t("notify.kol_welcome", percent=f"{user.commission_percent}")
                elif user.verified_kol == "rejected":
                    text = translator.t("notify.kol_rejected")
                elif (
                    user.verified_kol == "not_submitted"
                    and (now - created_at_vn) >= timedelta(minutes=5)
                ):
                    print("có")
                    text = translator.t("notify.kol_not_submitted")

                if text:
                    await self.send(user.user_id, text)
        all_affiliate_withdraws = AffiliateService.get_all_withdraw()
        for withdraw in all_affiliate_withdraws:
            if isinstance(withdraw.updated_at, str):
                try:
                    updated_at = datetime.strptime(withdraw.updated_at, "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"Time parse error for withdraw {withdraw.user_id}: {e}")
                    continue
            else:
                updated_at = withdraw.updated_at

            diff = now - updated_at
            if diff <= timedelta(minutes=5):
                
                user = UserService.get_user_by_telegram_id(withdraw.user_id)
                translator = Translator(getattr(user, "language", "en"))
                txid = withdraw.tx_hash or "No TXID available"

                text = None
                if withdraw.status == "approved":
                    
                    text = translator.t(
                        "notify.withdraw_user_paid_no_txid" if txid == "No TXID available" else "notify.withdraw_paid",
                        amount=f"{withdraw.amount}",
                        txid=txid,
                    )

                elif withdraw.status == "pending":
                    text = translator.t("notify.withdraw_pending")
                elif withdraw.status == "rejected":
                    text = translator.t("notify.withdraw_rejected")

                if text:
                    await self.send(withdraw.user_id, text)

    async def send(self, user_id: int, text: str):
        try:
            await self.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
        except Exception as e:
            print(f"[SendMessage] ❌ Error sending message to {user_id}: {e}")
