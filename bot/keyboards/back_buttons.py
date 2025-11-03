# bot/keyboards/back_buttons.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.translator import Translator

def back_main_menu(lang:str):
    translator = Translator(lang)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{translator.t('button.back_button')}", callback_data="back_main")]
    ])
    return keyboard
