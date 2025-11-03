from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.translator import Translator

def get_language_menu(lang):
    kb = InlineKeyboardBuilder()
    translator = Translator(lang)

    languages = [
        ("🇬🇧 English", "en"),
        ("🇨🇳 Chinese", "zh"),
        ("🇷🇺 Russian", "ru"),
        ("🇪🇸 Spanish", "es"),
        ("🇻🇳 Vietnamese", "vn"),
        ("🇹🇷 Turkish", "tr"),
        ("🇮🇳 Hindi", "hi"),
        ("🇰🇷 Korean", "ko"),
    ]

    for text, code in languages:
        mark = " ✅" if lang == code else ""
        kb.button(text=f"{text}{mark}", callback_data=f"lang_{code}")

    # Nút quay lại
    kb.button(text=translator.t("button.back_button"), callback_data="back_main")

    kb.adjust(2, 2, 2, 2, 1)
    return kb.as_markup()
