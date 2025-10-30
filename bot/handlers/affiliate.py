from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.affiliate_service import AffiliateService
from bot.keyboards.affiliate_menu import get_affiliate_menu
from bot.keyboards.back_buttons import back_main_menu
from config.translator import Translator
from config.settings import settings
affiliate_router = Router()
ADMIN_CHAT_ID = settings.ADMIN_CHAT_ID
URL_BOT = settings.URL_BOT

class WithdrawState(StatesGroup):
    waiting_for_wallet = State()
class VerifyState(StatesGroup):
    waiting_for_social_link = State()

@affiliate_router.callback_query(F.data == "affiliate")
async def open_affiliate_menu(callback: types.CallbackQuery):
    bot = callback.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    balance = float(AffiliateService.get_total_commission_by_user(user_id) or 0.0)
    balance_text = f"{balance:,.2f}"
    affiliate_link = f"{URL_BOT}?start={user_id}"
    active_referrals = AffiliateService.get_referrals_by_referrer_active(user_id) or []
    pending_referrals = AffiliateService.get_referrals_by_referrer_pending(user_id) or []
    active_count = len(active_referrals)
    pending_count = len(pending_referrals)
    translator = Translator(lang="en")
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
        reply_markup=get_affiliate_menu()
    )

    await callback.answer()

@affiliate_router.callback_query(F.data == "aff_withdraw")
async def handle_affiliate_withdraw(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    balance = float(AffiliateService.get_total_commission_by_user(user_id) or 0.0)
    translator = Translator(lang="en")

    # Nếu số dư < 20 USD
    if balance < 20:
        await callback.answer(translator.t("affiliate_withdraw.not_enough_balance"), show_alert=True)
        return

    # Giao diện rút tiền
    kb = InlineKeyboardBuilder()
    kb.button(text=translator.t("affiliate_withdraw.cancel_button"), callback_data="affiliate")
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
    wallet = message.text.strip()
    translator = Translator(lang="en")

    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")

    # Kiểm tra địa chỉ ví hợp lệ
    if not (wallet.startswith("0x") and len(wallet) == 42):
        kb = InlineKeyboardBuilder()
        kb.button(text=translator.t("affiliate_withdraw.try_again_button"), callback_data="aff_withdraw")
        kb.button(text=translator.t("affiliate_withdraw.back_button"), callback_data="affiliate")
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

    balance = float(AffiliateService.get_total_commission_by_user(user_id) or 0.0)

    # Ghi yêu cầu rút tiền vào DB
    withdraw_id = AffiliateService.create_withdrawal(
        user_id=user_id,
        amount=balance,
        wallet_address=wallet,
        status="pending",
        tx_hash=None,
    )

    # Gửi xác nhận cho user
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=translator.t(
            "affiliate_withdraw.withdraw_success",
            balance=f"{balance:,.2f}",
            wallet=wallet
        ),
        parse_mode="HTML",
        reply_markup=back_main_menu()
    )

    # Gửi thông báo đến admin
    admin_kb = InlineKeyboardBuilder()
    admin_kb.button(
        text=translator.t("affiliate_withdraw.confirm_withdraw_button"),
        callback_data=f"approve_withdraw:{withdraw_id}:{user_id}"
    )
    markup = admin_kb.as_markup()

    admin_text = translator.t(
        "affiliate_withdraw.new_withdraw_request",
        user_id=user_id,
        balance=f"{balance:,.2f}",
        wallet=wallet,
        username=message.from_user.username or "No username"
    )

    await message.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_text,
        parse_mode="HTML",
        reply_markup=markup
    )
    await state.clear()


@affiliate_router.callback_query(F.data.startswith("approve_withdraw"))
async def approve_withdrawal(callback: types.CallbackQuery):
    translator = Translator(lang="en")

    if callback.from_user.id != ADMIN_CHAT_ID:
        await callback.answer(translator.t("affiliate_withdraw.user_not_authorized"), show_alert=True)
        return

    try:
        _, withdraw_id, user_id = callback.data.split(":")
        withdraw_id = int(withdraw_id)
        user_id = int(user_id)
    except:
        await callback.answer(translator.t("affiliate_withdraw.invalid_data_format"), show_alert=True)
        return

    AffiliateService.update_withdraw_status(withdraw_id, "approved")
    AffiliateService.reset_user_commission(user_id)

    await callback.message.edit_text(
        translator.t(
            "affiliate_withdraw.withdraw_approved",
            withdraw_id=withdraw_id,
            user_id=user_id
        ),
        parse_mode="HTML"
    )

    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text=translator.t("affiliate_withdraw.withdraw_approved_user"),
            parse_mode="HTML"
        )
    except:
        pass

    await callback.answer(translator.t("affiliate_withdraw.withdraw_approved_alert"))


@affiliate_router.callback_query(F.data == "aff_verify")
async def handle_affiliate_verify(callback: types.CallbackQuery, state: FSMContext):
    translator = Translator(lang="en")
    kb = InlineKeyboardBuilder()
    kb.button(text=translator.t("affiliate_verify.cancel_button"), callback_data="affiliate")
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
    translator = Translator(lang="en")

    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    social_info = message.text.strip()

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
    await message.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="HTML")

    try:
        await message.bot.edit_message_text(
            chat_id=user_id,
            message_id=edit_msg_id,
            text=translator.t("affiliate_verify.user_success"),
            parse_mode="HTML",
            reply_markup=back_main_menu()
        )
    except Exception:
        await message.bot.send_message(
            chat_id=user_id,
            text=translator.t("affiliate_verify.user_success"),
            parse_mode="HTML",
            reply_markup=back_main_menu()
        )

    await state.clear()
