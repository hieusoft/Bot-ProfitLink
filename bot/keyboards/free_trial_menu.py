from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_free_trial_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Activate Free Trial", callback_data="activate_free_trial")
    kb.button(text="🚀 Join Official Channel", callback_data="join_channel_trial")
    kb.button(text="⬅️ Back", callback_data="back_main")
    kb.adjust(1,2)
    return kb.as_markup()


