from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.translator import Translator

def get_free_trial_menu(lang:str):
    translator =Translator(lang)
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{translator.t('button.activate_free_trial')}", callback_data="activate_free_trial")
    kb.button(text=f"{translator.t('button.join_official_channel')}", callback_data="join_channel_trial")
    kb.button(text=f"{translator.t('button.back_button')}", callback_data="back_main")
    kb.adjust(1,2)
    return kb.as_markup()


