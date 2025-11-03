from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.translator import Translator
import os

def get_language_menu(lang):
    kb = InlineKeyboardBuilder()
    translator = Translator(lang)

    # Detect available locale files under media/language/*.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_dir = os.path.normpath(os.path.join(base_dir, "..", "..", "media", "language"))
    try:
        files = [f for f in os.listdir(locale_dir) if f.endswith(".json")]
    except Exception:
        files = []

    available_codes = {os.path.splitext(f)[0] for f in files}

    # Map codes to pretty labels with flags
    label_map = {
        "en": "🇬🇧 English",
        "zh": "🇨🇳 Chinese",
        "ru": "🇷🇺 Russian",
        "es": "🇪🇸 Spanish",
        "vn": "🇻🇳 Vietnamese",
        "tr": "🇹🇷 Turkish",
        "hi": "🇮🇳 Hindi",
        "ko": "🇰🇷 Korean",
    }

    # Preferred order
    preferred_order = ["en", "vn", "zh", "ru", "es", "tr", "hi", "ko"]

    # Add preferred languages if available
    for code in preferred_order:
        if code in available_codes:
            mark = " ✅" if lang == code else ""
            kb.button(text=f"{label_map.get(code, code.upper())}{mark}", callback_data=f"lang_{code}")

    # Add any remaining available languages not in label_map/order
    for code in sorted(available_codes - set(preferred_order)):
        mark = " ✅" if lang == code else ""
        kb.button(text=f"{code.upper()}{mark}", callback_data=f"lang_{code}")

    # Back button
    kb.button(text=translator.t("button.back_button"), callback_data="back_main")

    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()
