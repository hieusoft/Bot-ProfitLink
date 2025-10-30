from aiogram import Router, types, F
from aiogram.types import FSInputFile
from datetime import datetime, timedelta
import os

from bot.keyboards.free_trial_menu import get_free_trial_menu
from bot.keyboards.back_buttons import back_main_menu
from services.plan_service import PlanService
from services.subscription_service import SubscriptionService
from services.subscription_detail_service import SubscriptionDetailService
from config.translator import Translator
from aiogram.utils.keyboard import InlineKeyboardBuilder

free_trial_router = Router()


@free_trial_router.callback_query(F.data == "free_trial")
async def open_free_trial_menu(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    translator = Translator("en") 

    
    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    
    caption_text = (
        f"{translator.t('free_trial.title')}\n\n"
        f"{translator.t('free_trial.description')}\n\n"
        f"{translator.t('free_trial.activate_cta')}"
    )

    
    await callback.message.answer(
        text=caption_text,
        parse_mode="Markdown",
        reply_markup=get_free_trial_menu(),
    )

    await callback.answer()

@free_trial_router.callback_query(F.data == "activate_free_trial")
async def activate_free_trial(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    translator = Translator("en") 
    plan = PlanService.get_plan_by_id(1)
    if not plan:
        await callback.answer(translator.t("free_trial.not_found"), show_alert=True)
        return

    if SubscriptionService.has_used_trial(user_id):
        await callback.answer(translator.t("free_trial.already_used"), show_alert=True)
        return

    sub = SubscriptionService.get_subscription_by_user_id(user_id)
    if not sub:
        sub = SubscriptionService.create_subscription(user_id)
    sub_id = sub.sub_id

    active_details = SubscriptionDetailService.get_active_details(sub_id)
    if active_details:
        await callback.answer(translator.t("free_trial.already_active"), show_alert=True)
        return

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=plan.duration_days)

    SubscriptionService.update_subscription_trial(
        sub_id=sub_id,
        start_date=start_time,
        end_date=end_time,
        trial=True,
        status="active",
    )

    SubscriptionDetailService.create_subscription_detail(
        sub_id=sub_id,
        plan_id=plan.plan_id,
        payment_id=None,
        activated_at=start_time,
        expired_at=end_time,
        renewed=False,
    )

    success_text = (
        f"{translator.t('free_trial.activated_title')}\n\n"
        f"{translator.t('free_trial.activated_message', days=plan.duration_days, expire_time=end_time.strftime('%Y-%m-%d %H:%M'))}"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Back", callback_data="free_trial")
    try:
        await callback.message.edit_text(
            text=success_text,
            parse_mode="Markdown",
            reply_markup=kb.as_markup(),
        )
    except Exception:
        await callback.message.answer(success_text, parse_mode="Markdown", reply_markup=back_main_menu())

    await callback.answer(translator.t("free_trial.success_alert"))

from aiogram.utils.keyboard import InlineKeyboardBuilder

@free_trial_router.callback_query(F.data == "join_channel_trial")
async def join_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    invite_link = "https://t.me/addlist/yVDMsEMPpa4zNGE1"

    sub = SubscriptionService.get_subscription_by_user_id(user_id)

    if not sub:
        await callback.message.edit_text(
            "❌ Please register for a plan before joining the channel.",
            parse_mode="HTML"
        )
        return

    sub_id = sub.sub_id
    active_details = SubscriptionDetailService.get_active_details(sub_id)

    if active_details:
        kb = InlineKeyboardBuilder()
        kb.button(text="⬅️ Back", callback_data="free_trial")
        kb.button(text="👉 Join Channel", url=invite_link)
        await callback.message.edit_text(
            "✅ You can now join our official Telegram channel:",
            parse_mode="HTML",
            reply_markup=kb.as_markup()
        )
    else:
        await callback.answer(
            "⚠️ Your subscription is not active. Please activate or renew it to join the channel.",
            show_alert=True
        )
