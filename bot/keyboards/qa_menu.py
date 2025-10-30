import random
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.qna_service import QnAService

def get_qa_menu():
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

    kb.button(text="↩️ Back", callback_data="back_main")
    kb.adjust(2)
    return kb.as_markup()
