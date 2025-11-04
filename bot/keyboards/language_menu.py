from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.translator import Translator
import os
import sys
import json

def get_language_menu(lang):
    kb = InlineKeyboardBuilder()
    translator = Translator(lang)

    # 🧩 Phát hiện môi trường chạy
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )

    # 🗂 Thư mục chứa các file ngôn ngữ JSON
    locale_dir = os.path.normpath(os.path.join(base_dir, "media", "language"))

    # 🧠 Tìm tất cả file .json trong thư mục ngôn ngữ
    try:
        files = [f for f in os.listdir(locale_dir) if f.endswith(".json")]
    except Exception:
        files = []

    available_codes = {os.path.splitext(f)[0] for f in files}

    # 🌍 Tự động đọc thông tin hiển thị từ từng file JSON
    for code in sorted(available_codes):
        try:
            lang_path = os.path.join(locale_dir, f"{code}.json")
            with open(lang_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Nếu trong file có key "language_name" (ví dụ "🇻🇳 Vietnamese") → dùng cái đó
            lang_label = data.get("language_name", code.upper())
        except Exception:
            lang_label = code.upper()

        # ✅ Đánh dấu ngôn ngữ hiện tại
        mark = " ✅" if lang == code else ""

        kb.button(
            text=f"{lang_label}{mark}",
            callback_data=f"lang_{code}"
        )

    # ⬅️ Nút quay lại
    kb.button(text=translator.t("button.back_button"), callback_data="back_main")

    # Chia nút đều 2 cột
    kb.adjust(2, 2, 2, 2, 1)

    return kb.as_markup()
