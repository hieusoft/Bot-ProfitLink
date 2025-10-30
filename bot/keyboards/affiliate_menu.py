from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_affiliate_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Withdraw", callback_data="aff_withdraw")
    kb.button(text="🧾 Verify as KOL/KOC", callback_data="aff_verify")
    kb.button(text="⬅️ Back", callback_data="back_main")
    kb.adjust(2, 1)
    return kb.as_markup()
