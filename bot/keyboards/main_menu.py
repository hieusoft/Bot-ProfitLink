from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.translator import Translator
from config.settings import settings
def get_main_menu(lang:str):
    kb = InlineKeyboardBuilder()
    translator = Translator(lang)
    kb.button(text=f"{translator.t('button.start_free_trial')}", callback_data="free_trial")
    kb.button(text=f"{translator.t('button.premium_plan')}", callback_data="subscription_plans")
    kb.button(text=f"{translator.t('button.cashback_trading_fee')}", callback_data="cashback")  
    kb.button(text=f"{translator.t('button.my_account')}", callback_data="my_account")
    kb.button(text=f"{translator.t('button.affiliate_center')}", callback_data="affiliate")
    kb.button(text=f"{translator.t('button.help_q/a')}", callback_data="qa")
    kb.button(
        text=f"{translator.t('button.support_team')}",
        url=settings.URL_SUPPORT
    )
    kb.button(text=f"{translator.t('button.change_language')}",callback_data="language")
    kb.adjust(1, 1,1, 2, 2, 1)
    return kb.as_markup()
