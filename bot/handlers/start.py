from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from bot.keyboards.main_menu import get_main_menu
from services.user_service import UserService
from services.subscription_service import SubscriptionService
from config.translator import Translator
import os

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: types.Message, command: CommandStart):
    bot = message.bot
    chat_id = message.chat.id
    user = message.from_user
    args = command.args

    try:
        async for msg in bot.get_chat_history(chat_id=chat_id, limit=10):
            if msg.from_user and msg.from_user.id == (await bot.me()).id:
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
                except Exception:
                    pass
    except Exception:
        pass

    existing_user = UserService.get_user_by_telegram_id(user.id)


    if not existing_user:
       
        ref_code = args.strip() if args else None

        if ref_code:
            referrer = UserService.get_user_by_telegram_id(ref_code)
            if referrer:

                await UserService.register_with_referral(
                    user_id=user.id,
                    username=user.username,
                    language="en",
                    verified_kol="not_submitted",
                    ref_code=ref_code
                )
               
                try:
                    ref_lang = getattr(referrer, "language", "en")
                    ref_translator = Translator(ref_lang)
                    ref_username = f"@{user.username}" if user.username else str(user.id)
                    await bot.send_message(
                        chat_id=int(ref_code),
                        text=ref_translator.t("referral.new_referral", username=ref_username, user_id=user.id),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            else:

                await UserService.register_user(
                    user_id=user.id,
                    username=user.username,
                    language="en",
                    verified_kol="not_submitted"
                )
        else:
          
            await UserService.register_user(
                user_id=user.id,
                username=user.username,
                language="en",
                verified_kol="not_submitted"
            )

        try:
            SubscriptionService.create_subscription(
                user_id=user.id,
                start_date=None,
                end_date=None,
                status=None,
                trial=False
            )
        except Exception:
            pass


    # Use user's saved language for all texts
    db_user = UserService.get_user_by_telegram_id(user.id)
    user_lang = getattr(db_user, "language", "en")
    translator = Translator(lang=user_lang)
    name = user.full_name or translator.t("start.no_username")
    caption = translator.t("start.welcome", name=name)

    banner_path = os.path.join("media", "assets", "banner.jpg")
    user = db_user
    
    if os.path.exists(banner_path):
        photo = FSInputFile(banner_path)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_main_menu(user.language)
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode="Markdown",
            reply_markup=get_main_menu(user.language)
        )
