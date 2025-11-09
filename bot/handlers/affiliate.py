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
    r'^(https?:\/\/)'         
    r'([\w.-]+)\.'           
    r'([a-zA-Z]{2,})'         
    r'(\/\S*)?$',         
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
    user = UserService.get_user_by_telegram_id(user_id)
    lang = getattr(user, "language", "en") if user else "en"
    user_langs[user_id] = lang 
     
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
    user_db = UserService.get_user_by_telegram_id(user_id)
    lang = user_db.language 
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


import asyncio
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

@affiliate_router.message(WithdrawState.waiting_for_wallet)
async def process_wallet_address(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    parts = text.split("|")
    lang = user_langs.get(user_id, "en")
    translator = Translator(lang)

    # ⚠️ Kiểm tra định dạng
    if len(parts) != 2:
        msg = await message.answer(translator.t("affiliate_withdraw.invalid_format"))
        await asyncio.sleep(3)
        try:
            await msg.delete()
          
        except:
            pass
        return

    balance = float(AffiliateService.get_affiliate_balance(user_id))
    amount = float(parts[0].strip())
    wallet = parts[1].strip()

   
    if amount < 20:
        msg = await message.answer(translator.t("affiliate_withdraw.not_enough_balance"))
        await asyncio.sleep(3)
        try:
            await msg.delete()
          
        except:
            pass
        return


    if amount > balance:
        msg = await message.answer(translator.t("affiliate_withdraw.insufficient_balance"))
        await asyncio.sleep(3)
        try:
            await msg.delete()
           
        except:
            pass
        return
    

    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")

    # ⚠️ Ví không hợp lệ
    if not (wallet.startswith("0x") and len(wallet) == 42):
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

        # 🕒 Sau vài giây xoá thông báo lỗi ví
        # await asyncio.sleep(3)
        # try:
        #     await message.bot.delete_message(chat_id=message.chat.id, message_id=bot_message_id)
        # except:
        #     pass

        await state.clear()
        return

    # ✅ Tạo lệnh rút tiền
    withdraw_id = AffiliateService.create_withdrawal(
        user_id=user_id,
        amount=amount,
        wallet_address=wallet,
        status="pending",
        tx_hash=None,
    )

    # ✅ Thông báo thành công cho user
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

    # ✅ Gửi thông báo cho admin
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
    if user_id not in user_langs:
        lang = user.language if user and hasattr(user, "language") else "en"
        user_langs[user_id] = lang
    else:
        lang = user_langs[user_id]
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

    kb = InlineKeyboardBuilder()
    kb.button(text=translator.t("button.back_button"), callback_data="affiliate")
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
    social_text = message.text.strip()


    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    edit_msg_id = data.get("edit_msg_id")

    # Tách các link theo dòng
    links = [line.strip() for line in social_text.splitlines() if line.strip()]

    # Nếu không có link nào
    if not links:
        await message.answer(translator.t("affiliate_verify.empty_links"))
        return

    # Kiểm tra từng link
    invalid_links = [link for link in links if not URL_REGEX.match(link)]

    if invalid_links:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=translator.t("button.try_again_button"),
            callback_data="aff_verify"
        )
        kb.button(
            text=translator.t("button.back_button"),
            callback_data="affiliate"
        )
        markup = kb.as_markup()

        # ⚠️ Gộp các link sai để hiển thị cho người dùng (nếu cần)
        bad_list = "\n".join(invalid_links)
        warn_text = translator.t("affiliate_verify.alert_social_warning")

        try:
            await message.bot.edit_message_text(
                chat_id=user_id,
                message_id=edit_msg_id,
                text=warn_text,
                parse_mode="HTML",
                reply_markup=markup
            )
        except Exception:
            await message.bot.send_message(
                chat_id=user_id,
                text=warn_text,
                parse_mode="HTML",
                reply_markup=markup
            )

        await state.clear()
        return

    # ✅ Nếu tất cả link hợp lệ
    combined_links = "\n".join(links)

    UserService.update_verified_kol(
        user_id=user_id,
        verified_kol="under_review",
        link=combined_links   # 🟢 Lưu tất cả link trong 1 chuỗi (ngăn cách bằng xuống dòng)
    )

    admin_text = translator.t(
        "affiliate_verify.admin_new_request",
        user_id=user_id,
        username=username,
        social_info=combined_links
    )

    # Gửi cho admin
    await message.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_text,
        parse_mode="HTML"
    )

    # Gửi lại cho user
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