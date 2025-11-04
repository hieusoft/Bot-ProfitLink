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

user_langs = {}


@account_router.callback_query(F.data == "my_account")
async def my_account_info(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    user = UserService.get_user_by_telegram_id(user_id)
    lang = getattr(user, "language", "en") if user else "en"
    user_langs[user_id] = lang 

    translator = Translator(lang)

    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    sub = SubscriptionService.get_active_subscription(user_id)
    affiliate_link = f"{URL_BOT}?start={user_id}"

    if sub:
        last_detail = SubscriptionDetailService.get_latest_subscription_detail(sub.sub_id)
        plan_name = getattr(last_detail, "plan_name", "Unknown Plan")

        now_vn = datetime.now(tz_vn).replace(tzinfo=None)

      
        end_date = (
            datetime.strptime(sub.end_date, "%Y-%m-%d %H:%M:%S")
            if isinstance(sub.end_date, str)
            else sub.end_date
        )

        # ✅ Đảm bảo so sánh cùng kiểu naive
        remaining_days = (end_date - now_vn).days
        end_date_str = end_date.strftime("%d/%m/%Y")

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
