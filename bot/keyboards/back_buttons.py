# bot/keyboards/back_buttons.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back ", callback_data="back_main")]
    ])
    return keyboard
