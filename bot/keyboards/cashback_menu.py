from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_cashback_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🆕 Register New Trading Account", callback_data="cb_register")
    kb.button(text="🔗 Link Existing Account", callback_data="cb_link")
    kb.button(text="💵 Check My Cashback Fee", callback_data="cb_check")
    kb.button(text="⬅️ Back", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()
