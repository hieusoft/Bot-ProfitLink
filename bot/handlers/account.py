from aiogram import Router, types, F
from datetime import datetime
from services.subscription_service import SubscriptionService
from bot.keyboards.back_buttons import back_main_menu
from services.subscription_detail_service import SubscriptionDetailService
from config.settings import settings
from config.translator import Translator
from services.user_service import UserService
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
account_router = Router()
URL_BOT = settings.URL_BOT

# Lưu ngôn ngữ user
user_langs = {}


@account_router.callback_query(F.data == "my_account")
async def my_account_info(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id

    # 🔹 Lấy ngôn ngữ từ DB (lưu cache 1 lần)
    if user_id not in user_langs:
        user_db = UserService.get_user_by_telegram_id(user_id)
        lang = user_db.language if user_db and hasattr(user_db, "language") else "en"
        user_langs[user_id] = lang
    else:
        lang = user_langs[user_id]
    
    translator = Translator(lang)

    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    sub = SubscriptionService.get_active_subscription(user_id)
    affiliate_link = f"{URL_BOT}?start={user_id}"

    # 🔹 Nếu có gói đăng ký
    if sub:
        last_detail = SubscriptionDetailService.get_latest_subscription_detail(sub.sub_id)
        plan_name = getattr(last_detail, "plan_name", "Unknown Plan")
        remaining_days = (sub.end_date - datetime.utcnow()).days
        end_date_str = sub.end_date.strftime("%d/%m/%Y")

        text = (
            f"{translator.t('account.title')}\n"
            f"{translator.t('account.user', name=callback.from_user.full_name)}\n\n"
            f"{translator.t('account.subscription_title')}\n"
            f"{translator.t('account.plan', plan=plan_name)}\n"
            f"{translator.t('account.status_active')}\n"
            f"{translator.t('account.remaining', days=remaining_days)}\n"
            f"{translator.t('account.expires', date=end_date_str)}\n\n"
            f"{translator.t('account.affiliate', link=affiliate_link)}\n\n"
            f"{translator.t('account.footer_active')}"
        )
    else:
        # 🔹 Nếu chưa có gói
        text = (
            f"{translator.t('account.title')}\n"
            f"{translator.t('account.user', name=callback.from_user.full_name)}\n\n"
            f"{translator.t('account.status_inactive')}\n"
            f"{translator.t('account.subscribe_hint')}\n\n"
            f"{translator.t('account.affiliate', link=affiliate_link)}\n\n"
            f"{translator.t('account.footer_inactive')}"
        )

    await bot.send_message(
        chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=back_main_menu(lang),
    )

    await callback.answer()
