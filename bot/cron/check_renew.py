from aiogram import Bot, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import pytz, asyncio
from services.subscription_service import SubscriptionService
from services.subscription_detail_service import SubscriptionDetailService
from services.payment_service import PaymentService
from services.plan_service import PlanService
from services.oxapay_service import OxaPayService
from services.user_service import UserService
from models.payment_model import Payment
from telethon import errors
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, PeerChannel
from config.telegram_client import get_telegram_client
from config.settings import settings
from config.translator import Translator

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
DISCOUNT = settings.DISCOUNT
CHANNEL_LIST = settings.CHANNEL_LIST


class SubscriptionChecker:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.oxapay = OxaPayService()
    async def check_all_users(self):
        all_subs = SubscriptionService.get_all_subscription_active()
        now = datetime.now(tz_vn).replace(tzinfo=None)

        for sub in all_subs:
            if not sub.end_date:
                continue
            sub_end = (
                datetime.strptime(sub.end_date, "%Y-%m-%d %H:%M:%S")
                if isinstance(sub.end_date, str)
                else sub.end_date
            )
            if sub_end < now:
                await self.delete_user_channels(sub.user_id)

                user = UserService.get_user_by_telegram_id(sub.user_id)
                translator = Translator(getattr(user, "language", "en"))
                text = translator.t("renew.expired_notice")

                await self.bot.send_message(
                    chat_id=sub.user_id, text=text, parse_mode="Markdown"
                )

                SubscriptionService.update_subscription(
                    sub_id=sub.sub_id,
                    start_date=sub.start_date,
                    end_date=sub.end_date,
                    status="expired",
                )
                continue

            last_sub_detail = SubscriptionDetailService.get_last_active_details(sub.sub_id)
            if last_sub_detail and last_sub_detail.plan_id != 1:
                expired_at = (
                    datetime.strptime(last_sub_detail.expired_at, "%Y-%m-%d %H:%M:%S")
                    if isinstance(last_sub_detail.expired_at, str)
                    else last_sub_detail.expired_at
                )

                remaining_time = expired_at - now
                if remaining_time <= timedelta(days=3):
                    await self.send_renew_message(sub, last_sub_detail, remaining_time)

    async def send_renew_message(self, sub, sub_detail, remaining_time):
        plan = PlanService.get_plan_by_id(sub_detail.plan_id)
        if not plan:
            return

        user = UserService.get_user_by_telegram_id(sub.user_id)
        translator = Translator(user.language)

        timestamp = datetime.now(tz_vn).strftime("%Y%m%d%H%M%S")
        order_id = f"{sub.user_id}_{timestamp}_{plan.name.upper()}_RENEW"
        amount = float(plan.price) * (1 - DISCOUNT / 100)

        last_payment = PaymentService.get_latest_payment_renew(sub.user_id, plan.plan_id)
        now_vn = datetime.now(tz_vn).replace(tzinfo=None)

        create_new_payment = True
        merchant_id = track_id = None

        if last_payment and last_payment.invoice_date and last_payment.expired_at:
            invoice_datetime = datetime.fromtimestamp(last_payment.invoice_date)
            expired_datetime = datetime.fromtimestamp(last_payment.expired_at)

            if now_vn < expired_datetime and "RENEW" in last_payment.order_id:
                create_new_payment = False
                order_id = last_payment.order_id
                amount = last_payment.amount
                merchant_id = last_payment.merchant_id
                track_id = last_payment.track_id

        if create_new_payment:
            track_id, merchant_id, expired_at, invoice_date = await self.oxapay.create_invoice_renew(amount, order_id)
            payment = Payment(
                user_id=sub.user_id,
                plan_id=plan.plan_id,
                order_id=order_id,
                amount=amount,
                currency="USDT",
                method="OxaPay",
                status="pending",
                merchant_id=merchant_id,
                track_id=track_id,
                expired_at=expired_at,
                invoice_date=invoice_date,
                completed_at=None,
            )
            PaymentService.create_payment(payment)

        payment_url = f"https://pay.oxapay.com/{merchant_id}/{track_id}"
        kb = InlineKeyboardBuilder()
        kb.button(text=translator.t("button.oxapay"), url=payment_url)
        kb.button(
            text=translator.t("button.affiliate_balance"),
            callback_data=f"pay_sub_{plan.name}_affiliate_balance_renew",
        )
        kb.button(
            text=translator.t("button.check_payment"),
            callback_data=f"check_sub_{plan.name}_renew",
        )
        kb.adjust(2, 1)

        text = translator.t(
            "renew.about_to_expire",
            days=remaining_time.days,
            plan_name=plan.name,
            discount=DISCOUNT,
        )

        await self.bot.send_message(
            chat_id=sub.user_id,
            text=text,
            reply_markup=kb.as_markup(),
            parse_mode="Markdown",
        )

    async def delete_user_channels(self, user_id: int):
        try:
            with open(CHANNEL_LIST, "r", encoding="utf-8") as f:
                channels = [line.strip() for line in f.readlines() if line.strip()]
            if not channels:
                return

            async with get_telegram_client() as client:
                async def remove_from_channel(channel_id):
                    try:
                        channel = PeerChannel(int(channel_id))
                        async for user in client.iter_participants(channel):
                            if user.id == int(user_id):
                                kick_rights = ChatBannedRights(until_date=None, view_messages=True)
                                await client(EditBannedRequest(channel, user.id, kick_rights))
                                unban_rights = ChatBannedRights(
                                    until_date=None,
                                    send_messages=None,
                                    send_media=None,
                                    send_stickers=None,
                                    send_gifs=None,
                                    send_games=None,
                                    send_inline=None,
                                    embed_links=None,
                                    view_messages=None,
                                )
                                await client(EditBannedRequest(channel, user.id, unban_rights))
                                break
                    except errors.ChatAdminRequiredError:
                        pass
                    except Exception:
                        pass

                semaphore = asyncio.Semaphore(5)
                async def limited_remove(ch):
                    async with semaphore:
                        await remove_from_channel(ch)

                await asyncio.gather(*(limited_remove(ch) for ch in channels))
        except FileNotFoundError:
            pass
        except Exception:
            pass
