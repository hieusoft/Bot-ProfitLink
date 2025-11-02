from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_language_menu():
    kb = InlineKeyboardBuilder()

   
    languages = [
        ("🇬🇧 English", "lang_en"),
        ("🇨🇳 Chinese", "lang_zh"),
        ("🇷🇺 Russian", "lang_ru"),
        ("🇪🇸 Spanish", "lang_es"),
        ("🇻🇳 Vietnamese", "lang_vi"),
        ("🇹🇷 Turkish", "lang_tr"),
        ("🇮🇳 Hindi", "lang_hi"),
        ("🇰🇷 Korean", "lang_ko"),
    ]

   
    for text, callback in languages:
        kb.button(text=text, callback_data=callback)
    kb.button(text="⬅️ Back", callback_data="back_main")
    kb.adjust(2, 2, 2, 2,1)

    return kb.as_markup()
