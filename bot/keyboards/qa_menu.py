import random
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.qna_service import QnAService
from config.translator import Translator

def get_qa_menu(lang:str):
    translator = Translator(lang)
    categories = QnAService.get_all_active_categories()
    emojis = ["💎", "🤝", "💰", "⚙️", "🧑‍💻", "🎯", "📝", "📌", "🚀", "🎉"]

    if len(emojis) < len(categories):
        raise ValueError("Not enough emojis for categories!")

    random.shuffle(emojis)
    kb = InlineKeyboardBuilder()

    for i, cat in enumerate(categories):
        kb.button(
            text=f"{emojis[i]} {cat.category_name}",
            callback_data=f"qa_category_{cat.category_id}_{cat.category_name}"
        )

    kb.button(text=f"{translator.t('button.back_button')}", callback_data="back_main")
    kb.adjust(2)
    return kb.as_markup()
