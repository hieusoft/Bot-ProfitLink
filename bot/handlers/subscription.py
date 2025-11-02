from aiogram import Router, types, F
from bot.keyboards.subscription_menu import get_subscription_menu
from bot.keyboards.back_buttons import back_main_menu
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.subscription_service import SubscriptionService
from services.subscription_detail_service import SubscriptionDetailService
from services.payment_service import PaymentService
from services.plan_service import PlanService
from services.user_service import UserService
from services.affiliate_service import AffiliateService
from models.payment_model import Payment
from datetime import datetime, timedelta
from services.oxapay_service import OxaPayService
import pytz

subscription_router = Router()
oxapay = OxaPayService()
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")


@subscription_router.callback_query(F.data == "subscription_plans")
async def open_subscription_menu(callback: types.CallbackQuery):
    bot = callback.message.bot
    chat_id = callback.message.chat.id
    plans = PlanService.get_all_active_plans()

    plans_text = "💎 <b>Available Subscription Plans</b>\n\n"
    now_vn = datetime.now(tz_vn)

    for plan in plans:
        price_text = f"${plan.price:.2f}"
        sale_start = plan.sale_start.astimezone(tz_vn) if plan.sale_start else None
        sale_end = plan.sale_end.astimezone(tz_vn) if plan.sale_end else None

        if plan.sale_percent > 0 and sale_start and sale_end and sale_start <= now_vn <= sale_end:
            discounted_price = plan.price * (1 - plan.sale_percent / 100)
            plans_text += (
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ <b>{plan.name}</b>\n"
                f"💰 <s>${plan.price:.2f}</s> ➡️ <b>${discounted_price:.2f}</b>\n"
                f"💸 <b>{plan.sale_percent:.0f}% OFF</b> until <i>{sale_end.strftime('%d %b %Y')}</i>\n"
                f"📅 Duration: <code>{plan.duration_days} days</code>\n"
            )
        else:
            plans_text += (
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ <b>{plan.name}</b>\n"
                f"💰 Price: <b>{price_text}</b>\n"
                f"📅 Duration: <code>{plan.duration_days} days</code>\n"
            )

    try:
        await bot.delete_message(chat_id, callback.message.message_id)
    except Exception:
        pass

    await callback.message.answer(
        "🏆 <b>Premium Subscription Plans</b>\n\n"
        "Unlock your full trading potential with our premium signals and VIP benefits:\n\n"
        "🚀 <b>All plans include:</b>\n"
        "• Exclusive VIP Signal Channel\n"
        "• Priority Expert Support\n"
        "• Real-time Market Insights\n\n"
        f"{plans_text}━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Choose the plan that best fits your goals below!</i> 👇",
        parse_mode="HTML",
        reply_markup=get_subscription_menu()
    )
    await callback.answer()


@subscription_router.callback_query(F.data.startswith("sub_"))
async def choose_payment_method(callback: types.CallbackQuery):
    user = callback.from_user
    plan_key = callback.data
    now_vn = datetime.now(tz_vn)
    parts = plan_key.split("_")
    plan_name = parts[1].capitalize()

    plan = PlanService.get_plan_by_name(plan_name)
    if not plan:
        await callback.message.edit_text("❌ Plan does not exist!")
        return

    timestamp = now_vn.strftime("%Y%m%d%H%M%S")
    order_id = f"{user.id}_{timestamp}_{plan_name.upper()}"

    sale_start = plan.sale_start.astimezone(tz_vn) if plan.sale_start else None
    sale_end = plan.sale_end.astimezone(tz_vn) if plan.sale_end else None

    if plan.sale_percent > 0 and sale_start and sale_end and sale_start <= now_vn <= sale_end:
        amount = float(plan.price * (1 - plan.sale_percent / 100))
    else:
        amount = float(plan.price)

    last_payment = PaymentService.get_latest_payment_pending(user.id, plan.plan_id)
    create_new_payment = True

    if last_payment and last_payment.invoice_date:
        invoice_datetime = datetime.fromtimestamp(last_payment.invoice_date, tz=tz_vn)
        if now_vn - invoice_datetime < timedelta(minutes=30):
            create_new_payment = False
            order_id = last_payment.order_id
            amount = last_payment.amount

    if create_new_payment:
        track_id, merchant_id, expired_at, invoice_date = await oxapay.create_invoice(amount, order_id)
        payment = Payment(
            user_id=user.id,
            plan_id=plan.plan_id,
            order_id=order_id,
            amount=amount,
            currency="USDT",
            method="OxaPay",
            status="pending",
            merchant_id=merchant_id,
            track_id=track_id,
            expired_at=expired_at,
            invoice_date=invoice_date,
            completed_at=None
        )
        PaymentService.create_payment(payment)

    kb = InlineKeyboardBuilder()
    kb.button(text="💳 OxaPay", callback_data=f"pay_sub_{plan_name}_oxapay")
    kb.button(text="🪙 CryptoBot", callback_data=f"pay_sub_{plan_name}_cryptobot")
    kb.button(text="↩️ Back", callback_data="subscription_plans")
    kb.adjust(2, 1, 1)

    await callback.message.edit_text(
        f"""💎 <b>{plan_name} Plan</b>
🧾 <b>Order ID:</b> <code>{order_id}</code>
💰 <b>Amount:</b> <b>{amount} USDT</b>

<i>Choose your payment method below 👇</i>
""",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await callback.answer()


@subscription_router.callback_query(F.data.endswith("_oxapay"))
async def oxapay_payment(callback: types.CallbackQuery):
    user = callback.from_user
    plan_key = callback.data
    parts = plan_key.split("_")
    plan_name = parts[2].capitalize()

    plan = PlanService.get_plan_by_name(plan_name)
    if not plan:
        await callback.message.answer("❌ Plan does not exist!", show_alert=True)
        return

    last_payment = PaymentService.get_latest_payment_pending(user.id, plan.plan_id)
    if not last_payment:
        await callback.message.answer("❌ No recent payment found!", show_alert=True)
        return

    payment_url = f"https://pay.oxapay.com/{last_payment.merchant_id}/{last_payment.track_id}"

    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 Pay with OxaPay", url=payment_url)
    kb.button(text="✅ Check Payment", callback_data=f"check_sub_{plan_name}_payment")
    kb.button(text="↩️ Back", callback_data=f"sub_{plan_name}")
    kb.adjust(1, 2)

    await callback.message.edit_text(
        text=(
            f"🔗 Click the button below to pay for *{plan_name}* plan.\n\n"
            "⏳ After completing the payment, please wait a few minutes and then click 'Check Payment'."
        ),
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await callback.answer()


@subscription_router.callback_query(F.data.startswith("check_sub_") & F.data.endswith("_payment"))
async def check_subscription_payment(callback: types.CallbackQuery):
    user = callback.from_user
    plan_key = callback.data
    parts = plan_key.split("_")
    plan_name = parts[2].capitalize()
    print("cps")
    plan = PlanService.get_plan_by_name(plan_name)
    if not plan:
        await callback.answer("❌ Plan does not exist!", show_alert=True)
        return

    last_payment = PaymentService.get_latest_payment(user.id, plan.plan_id)
    if not last_payment:
        await callback.answer("❌ No recent payment found!", show_alert=True)
        return

    is_paid = await oxapay.check_payment_status(last_payment.track_id)
    now_vn = datetime.now(tz_vn)

    if not is_paid:
        payment_url = f"https://pay.oxapay.com/{last_payment.merchant_id}/{last_payment.track_id}"
        kb = InlineKeyboardBuilder()
        kb.button(text="🔗 Pay Again", url=payment_url)
        kb.button(text="↩️ Back", callback_data=f"pay_sub_{plan_name}_oxapay")
        kb.adjust(1, 1)
        await callback.message.edit_text(
            text=f"⏳ Payment for *{plan_name}* plan is still pending.\nPlease complete your payment below:",
            parse_mode="Markdown",
            reply_markup=kb.as_markup()
        )
        await callback.answer("⏳ Payment not confirmed yet. Try again in a few minutes.", show_alert=True)
        return

    referred = UserService.get_user_by_telegram_id(user.id)

    if referred:
        referrer = UserService.get_user_by_telegram_id(referred.ref_by)
        commission_amount = last_payment.amount * (referrer.commission_percent / 100)
        AffiliateService.update_referral(
            referrer_id=referrer.user_id,
            referred_id=user.id,
            commission_usd=commission_amount,
            status="approved",
        )

    sub = SubscriptionService.get_subscription_by_user_id(user.id)
    if not sub:
        await callback.answer("❌ Subscription record not found!", show_alert=True)
        return

    active_details = SubscriptionDetailService.get_active_details(sub.sub_id)
    duration = timedelta(days=plan.duration_days)

    PaymentService.update_payment_status(
        track_id=last_payment.track_id,
        status="success",
        completed_at=now_vn
    )

    if active_details:
        earliest_start = min(d.activated_at for d in active_details)
        latest_end = max(d.expired_at for d in active_details)
        last_detail = sorted(active_details, key=lambda x: x.expired_at)[-1]
        renewed = last_detail.plan_id == plan.plan_id
        new_start = latest_end
        new_end = latest_end + duration

        SubscriptionDetailService.create_subscription_detail(
            sub_id=sub.sub_id,
            plan_id=plan.plan_id,
            payment_id=last_payment.payment_id,
            activated_at=new_start,
            expired_at=new_end,
            renewed=renewed
        )

        SubscriptionService.update_subscription_end(
            sub_id=sub.sub_id,
            end_date=new_end,
            status="active"
        )
    else:
        start_time = now_vn
        end_time = start_time + duration

        SubscriptionDetailService.create_subscription_detail(
            sub_id=sub.sub_id,
            plan_id=plan.plan_id,
            payment_id=last_payment.payment_id,
            activated_at=start_time,
            expired_at=end_time,
            renewed=False
        )

        SubscriptionService.update_subscription(
            sub_id=sub.sub_id,
            start_date=start_time,
            end_date=end_time,
            status="active"
        )

    await callback.message.edit_text(
        f"✅ *Payment Successful!*\n\n"
        f"🎉 Your subscription to the *{plan_name}* plan is now active.\n"
        f"Enjoy exclusive access to premium signals and VIP benefits!",
        parse_mode="Markdown",
        reply_markup=back_main_menu()
    )

    await callback.answer("✅ Payment confirmed! Subscription activated.", show_alert=True)

@subscription_router.callback_query(F.data == "join_channel")
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
    active_details = SubscriptionService.get_active_subscription(user_id)

    if active_details:
        kb = InlineKeyboardBuilder()
        kb.button(text="👉 Join Channel", url=invite_link)  # Nút link ẩn
        kb.button(text="↩️ Back", callback_data="free_trial")
       
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

@subscription_router.callback_query(F.data.startswith("check_sub_") & F.data.endswith("_renew"))
async def check_subscription_payment_renew(callback: types.CallbackQuery):
    user = callback.from_user
    plan_key = callback.data
    parts = plan_key.split("_")
    plan_name = parts[2].capitalize()
    plan = PlanService.get_plan_by_name(plan_name)
    if not plan:
        await callback.answer("❌ Plan does not exist!", show_alert=True)
        return

    last_payment = PaymentService.get_latest_payment(user.id, plan.plan_id)
    if not last_payment:
        await callback.answer("❌ No recent payment found!", show_alert=True)
        return

    is_paid = await oxapay.check_payment_status(last_payment.track_id)
    now_vn = datetime.now(tz_vn)

    if not is_paid:
        payment_url = f"https://pay.oxapay.com/{last_payment.merchant_id}/{last_payment.track_id}"
        print(payment_url)
        await callback.answer("⏳ Payment not confirmed yet. Try again in a few minutes.", show_alert=True)
        return

    referred = UserService.get_user_by_telegram_id(user.id)

    if referred:
        referrer = UserService.get_user_by_telegram_id(referred.ref_by)
        commission_amount = last_payment.amount * (referrer.commission_percent / 100)
        AffiliateService.update_referral(
            referrer_id=referrer.user_id,
            referred_id=user.id,
            commission_usd=commission_amount,
            status="approved",
        )

    sub = SubscriptionService.get_subscription_by_user_id(user.id)
    if not sub:
        await callback.answer("❌ Subscription record not found!", show_alert=True)
        return

    active_details = SubscriptionDetailService.get_active_details(sub.sub_id)
    duration = timedelta(days=plan.duration_days)

    PaymentService.update_payment_status(
        track_id=last_payment.track_id,
        status="success",
        completed_at=now_vn
    )

    if active_details:
        earliest_start = min(d.activated_at for d in active_details)
        latest_end = max(d.expired_at for d in active_details)
        last_detail = sorted(active_details, key=lambda x: x.expired_at)[-1]
        renewed = last_detail.plan_id == plan.plan_id
        new_start = latest_end
        new_end = latest_end + duration

        SubscriptionDetailService.create_subscription_detail(
            sub_id=sub.sub_id,
            plan_id=plan.plan_id,
            payment_id=last_payment.payment_id,
            activated_at=new_start,
            expired_at=new_end,
            renewed=renewed
        )

        SubscriptionService.update_subscription_end(
            sub_id=sub.sub_id,
            end_date=new_end,
            status="active"
        )
    
        await callback.answer(
            "✅ Payment Successful!\n🎉 Your subscription is now active.\nEnjoy premium access and VIP benefits!",
            show_alert=True
        )
        try:
            await callback.message.delete()
        except Exception as e:
            print(f"[Subscription] Error deleting message: {e}")