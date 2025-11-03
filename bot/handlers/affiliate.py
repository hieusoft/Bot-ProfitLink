from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.affiliate_service import AffiliateService
from services.user_service import UserService
from bot.keyboards.affiliate_menu import get_affiliate_menu
from bot.keyboards.back_buttons import back_main_menu
from config.translator import Translator
from config.settings import settings
import re,asyncio
affiliate_router = Router()
ADMIN_CHAT_ID = settings.ADMIN_CHAT_ID
URL_BOT = settings.URL_BOT
URL_REGEX = re.compile(
    r'^(https?:\/\/)?'  # http hoặc https (tùy chọn)
    r'([\w.-]+)\.'      # tên miền
    r'([a-zA-Z]{2,})'   # phần mở rộng (com, net, org,...)
    r'(\/\S*)?$',        # phần path (tùy chọn)
    re.IGNORECASE
)
user_langs = {}
class WithdrawState(StatesGroup):
    waiting_for_wallet = State()
class VerifyState(StatesGroup):
    waiting_for_social_link = State()

@affiliate_router.callback_query(F.data == "affiliate")
async def open_affiliate_menu(callback: types.CallbackQuery):
    bot = callback.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    balance = float(AffiliateService.get_affiliate_balance(user_id) or 0.0)
    balance_text = f"{balance:,.2f}"
    affiliate_link = f"{URL_BOT}?start={user_id}"
    active_referrals = AffiliateService.get_referrals_by_referrer_active(user_id) or []
    pending_referrals = AffiliateService.get_referrals_by_referrer_pending(user_id) or []
    active_count = len(active_referrals)
    pending_count = len(pending_referrals)
    if user_id not in user_langs:
        user_db = UserService.get_user_by_telegram_id(user_id)
        lang = user_db.language if user_db and hasattr(user_db, "language") else "en"
        user_langs[user_id] = lang
    else:
        lang = user_langs[user_id]
    translator = Translator(lang)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    except Exception:
        pass

    message_html = (
        f"{translator.t('affiliate_menu.title')}\n"
        f"{translator.t('affiliate_menu.subtitle')}\n\n"
        f"{translator.t('affiliate_menu.total_commission', balance_text=balance_text)}\n\n"
        f"{translator.t('affiliate_menu.referral_stats')}\n"
        f"{translator.t('affiliate_menu.active', active_count=active_count)}\n"
        f"{translator.t('affiliate_menu.pending', pending_count=pending_count)}\n\n"
        f"{translator.t('affiliate_menu.referral_link', affiliate_link=affiliate_link)}\n\n"
        f"{translator.t('affiliate_menu.footer')}"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=message_html,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=get_affiliate_menu(lang)
    )

    await callback.answer()

@affiliate_router.callback_query(F.data == "aff_withdraw")
async def handle_affiliate_withdraw(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance = float(AffiliateService.get_affiliate_balance(user_id) or 0.0)
    lang = user_langs.get(user_id, "en")
    translator = Translator(lang)    
    if balance < 20:
        await callback.answer(translator.t("affiliate_withdraw.not_enough_balance"), show_alert=True)
        return

   
    kb = InlineKeyboardBuilder()
    kb.button(text=translator.t("button.cancel_button"), callback_data="affiliate")
    markup = kb.as_markup()

    msg = await callback.message.edit_text(
        translator.t(
            "affiliate_withdraw.confirm_withdraw",
            balance=f"{balance:,.2f}"
        ),
        parse_mode="HTML",
        reply_markup=markup
    )

    await state.update_data(bot_message_id=msg.message_id)
    await state.set_state(WithdrawState.waiting_for_wallet)
    await callback.answer()


@affiliate_router.message(WithdrawState.waiting_for_wallet)
async def process_wallet_address(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    parts = text.split("|")

   
    if len(parts) != 2:
        await message.answer("⚠️ Vui lòng nhập đúng định dạng: <số tiền>|<địa chỉ ví>")
        return
    balace =float(AffiliateService.get_affiliate_balance(user_id))
    amount = float(parts[0].strip())
    wallet = parts[1].strip()
    lang = user_langs.get(user_id, "en")
    translator = Translator(lang)

    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")

    if not (wallet.startswith("0x") and len(wallet) == 42) or amount>balace or amount<=0:
        kb = InlineKeyboardBuilder()
        kb.button(text=translator.t("button.try_again_button"), callback_data="aff_withdraw")
        kb.button(text=translator.t("button.back_button"), callback_data="affiliate")
        markup = kb.as_markup()

        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=bot_message_id,
            text=translator.t("affiliate_withdraw.invalid_wallet"),
            parse_mode="HTML",
            reply_markup=markup
        )
        await state.clear()
        return

    withdraw_id = AffiliateService.create_withdrawal(
        user_id=user_id,
        amount=amount,
        wallet_address=wallet,
        status="pending",
        tx_hash=None,
    )


    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=translator.t(
            "affiliate_withdraw.withdraw_success",
            balance=f"{amount:,.2f}",
            wallet=wallet
        ),
        parse_mode="HTML",
        reply_markup=back_main_menu(lang)
    )



    admin_text = translator.t(
        "affiliate_withdraw.new_withdraw_request",
        user_id=user_id,
        balance=f"{amount:,.2f}",
        wallet=wallet,
        username=message.from_user.username or "No username"
    )

   

    await message.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_text,
        parse_mode="HTML",
    )
    await state.clear()

@affiliate_router.callback_query(F.data == "aff_verify")
async def handle_affiliate_verify(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = UserService.get_user_by_telegram_id(user_id)
    lang = user_langs.get(user_id, "en")
    translator = Translator(lang)
    if user and user.verified_kol == "under_review":
        await callback.answer(
            translator.t("affiliate_verify.alert_under_review"),
            show_alert=True
        )
        return

    elif user.verified_kol == "approved":
        await callback.answer(
            translator.t("affiliate_verify.alert_approved"),
            show_alert=True
        )
        return
    elif user.verified_kol == "rejected":
        await callback.answer(
            translator.t("affiliate_verify.alert_rejected"),
            show_alert=True
        )
        return
    translator = Translator(lang="en")
    kb = InlineKeyboardBuilder()
    kb.button(text=translator.t("button.cancel_button"), callback_data="affiliate")
    markup = kb.as_markup()


    await callback.message.edit_text(
        text=(
            f"{translator.t('affiliate_verify.title')}\n\n"
            f"{translator.t('affiliate_verify.instruction')}"
        ),
        parse_mode="HTML",
        reply_markup=markup
    )
    await state.update_data(edit_msg_id=callback.message.message_id)
    await state.set_state(VerifyState.waiting_for_social_link)
    await callback.answer()


@affiliate_router.message(VerifyState.waiting_for_social_link)
async def process_social_verification(message: types.Message, state: FSMContext):
    
    user_id = message.from_user.id
    lang = user_langs.get(user_id, "en")
    translator = Translator(lang)

    username = message.from_user.username or "No username"
    social_info = message.text.strip()

    try:
        await message.delete()
    except Exception:
        pass
    if not URL_REGEX.match(social_info):
        warn_msg = await message.answer(
           translator.t("affiliate_verify.alert_social_warning"),
            parse_mode="HTML"
        )
        async def _delete_later(bot, chat_id, message_id, delay=5):
            await asyncio.sleep(delay)
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass
        asyncio.create_task(_delete_later(message.bot, warn_msg.chat.id, warn_msg.message_id, delay=5))
        return
    UserService.update_verified_kol(
        user_id=user_id,
        verified_kol="under_review"
    
    )
    data = await state.get_data()
    edit_msg_id = data.get("edit_msg_id")

    try:
        await message.delete()
    except Exception:
        pass
    admin_text = translator.t(
        "affiliate_verify.admin_new_request",
        user_id=user_id,
        username=username,
        social_info=social_info
    )


    
   


    await message.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_text,
        parse_mode="HTML"
    )
    try:
        await message.bot.edit_message_text(
            chat_id=user_id,
            message_id=edit_msg_id,
            text=translator.t("affiliate_verify.user_success"),
            parse_mode="HTML",
            reply_markup=back_main_menu(lang)
        )
    except Exception:
        await message.bot.send_message(
            chat_id=user_id,
            text=translator.t("affiliate_verify.user_success"),
            parse_mode="HTML",
            reply_markup=back_main_menu(lang)
        )

    await state.clear()