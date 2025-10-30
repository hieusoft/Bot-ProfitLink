from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.plan_service import PlanService
from datetime import datetime, timezone
import pytz
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")
def get_subscription_menu():
    kb = InlineKeyboardBuilder()
    plans = PlanService.get_all_active_plans()
    now_utc = datetime.now(timezone.utc)

    for plan in plans:
        display_price = f"${plan.price:.2f}"

        # Kiểm tra đủ điều kiện sale
        if (
            plan.sale_percent
            and plan.sale_start
            and plan.sale_end
        ):
            # Chuyển sale_start/sale_end về UTC thực sự
            sale_start = plan.sale_start.astimezone(timezone.utc)
            sale_end = plan.sale_end.astimezone(timezone.utc)

            now_utc = datetime.now(timezone.utc)
            if sale_start <= now_utc <= sale_end:
                discounted_price = plan.price * (1 - plan.sale_percent / 100)
                display_price = f"${discounted_price:.2f}"

        text = f"{plan.name}–{display_price}"
        callback_data = f"sub_{plan.name.lower()}"
        kb.button(text=text, callback_data=callback_data)


   
    kb.button(text="🚀 Join Official Channel", callback_data="join_channel")
    kb.button(text="⬅️ Back", callback_data="back_main")
    kb.adjust(2, 1,2)
    return kb.as_markup()
