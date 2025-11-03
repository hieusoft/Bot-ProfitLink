from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.translator import Translator


def get_affiliate_menu(lang:str):
    kb = InlineKeyboardBuilder()
    translator =Translator(lang)
    kb.button(text=f"{translator.t('button.withdraw_button')}", callback_data="aff_withdraw")
    kb.button(text=f"{translator.t('button.verify_kol')}", callback_data="aff_verify")
    kb.button(text=f"{translator.t('button.back_button')}", callback_data="back_main")
    kb.adjust(2, 1)
    return kb.as_markup()
