from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.plan_service import PlanService
from datetime import datetime, timezone
from config.translator import Translator
import pytz

tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

def get_subscription_menu(lang: str):
    kb = InlineKeyboardBuilder()
    plans = PlanService.get_all_active_plans()
    now_utc = datetime.now(timezone.utc)
    translator = Translator(lang)

    # 🔹 Nút đầu tiên: Tham gia kênh chính thức
    kb.button(
        text=translator.t("button.join_official_channel"),
        callback_data="join_channel"
    )

    # 🔹 Các gói đăng ký
    for plan in plans:
        # Mặc định giá gốc
        display_price = f"${plan.price:.2f}"

        # Tính giá giảm (nếu có)
        if plan.sale_percent and plan.sale_start and plan.sale_end:
            sale_start = plan.sale_start.astimezone(timezone.utc)
            sale_end = plan.sale_end.astimezone(timezone.utc)
            if sale_start <= now_utc <= sale_end:
                discounted_price = plan.price * (1 - plan.sale_percent / 100)
                display_price = f"${discounted_price:.2f}"

        # Callback khi chọn gói
        callback_data = f"sub_{plan.name.lower()}"

        # 🔹 Lấy tên gói dịch theo key động (vd: "plan.basic", "plan.premium")
        plan_key = f"plans.{plan.name.lower()}"
        print(plan_key)
        plan_name_translated = translator.t(plan_key)

        # 🔹 Tạo nút với tên gói + giá
        kb.button(
            text=f"{plan_name_translated}",
            callback_data=callback_data
        )

    # 🔹 Nút quay lại
    kb.button(
        text=translator.t("button.back_button"),
        callback_data="back_main"
    )

    # 🔹 Bố cục nút
    kb.adjust(2)
    return kb.as_markup()
