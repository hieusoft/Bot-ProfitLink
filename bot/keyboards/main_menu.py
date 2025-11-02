from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    kb = InlineKeyboardBuilder()

    kb.button(text="🎯 Start Free Trial (3 Days)", callback_data="free_trial")

    kb.button(text="💎 Premium Plans", callback_data="subscription_plans")
    kb.button(text="💰 Cashback Trading Fee", callback_data="cashback")

   
    kb.button(text="👤 My Account", callback_data="my_account")
    kb.button(text="🤝 Affiliate Center", callback_data="affiliate")
    
    kb.button(text="🧠 Help / Q&A", callback_data="qa")
    kb.button(
        text="🧑‍💼 Support Team",
        url="https://t.me/hieusoft"
    )


   
    kb.button(text="🌍 Change Language",callback_data="language")
   

    kb.adjust(1, 1,1, 2, 2, 1)

    return kb.as_markup()
