from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.plan_service import PlanService
from datetime import datetime, timezone
from config.translator import Translator
import pytz
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
def get_subscription_menu(lang:str):
    kb = InlineKeyboardBuilder()
    plans = PlanService.get_all_active_plans()
    now_utc = datetime.now(timezone.utc)
    translator = Translator(lang)
    kb.button(text=f"{translator.t('button.join_official_channel')}", callback_data="join_channel")
    for plan in plans:
        display_price = f"${plan.price:.2f}"

        if (
            plan.sale_percent
            and plan.sale_start
            and plan.sale_end
        ):
         
            sale_start = plan.sale_start.astimezone(timezone.utc)
            sale_end = plan.sale_end.astimezone(timezone.utc)

            now_utc = datetime.now(timezone.utc)
            if sale_start <= now_utc <= sale_end:
                discounted_price = plan.price * (1 - plan.sale_percent / 100)
                display_price = f"${discounted_price:.2f}"
        text = f"{plan.name}–{display_price}"
        callback_data = f"sub_{plan.name.lower()}"
        kb.button(text=text, callback_data=callback_data) 
    kb.button(text=f"{translator.t('button.back_button')}", callback_data="back_main")
    kb.adjust(2,2,1)
    return kb.as_markup()
