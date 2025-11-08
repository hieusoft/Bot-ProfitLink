from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
import asyncio, logging
from config.settings import settings
from aiogram.client.default import DefaultBotProperties
from bot.handlers import (
    start_router,
    affiliate_router,
    subscription_router,
    cashback_router,
    qa_router,
    free_trial_router,
    main_menu_router, 
    account_router,
    language_router,
    admin_router
)
from bot.cron.check_renew import SubscriptionChecker
from bot.utils.send_message import SendMessage
logging.basicConfig(level=logging.INFO)
async def main():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    dp.include_routers(
        start_router,
        affiliate_router,
        subscription_router,
        cashback_router,
        qa_router,  
        free_trial_router,
        main_menu_router,  
        account_router,
        language_router,
        admin_router
    )
    checker = SubscriptionChecker(bot)
    sender = SendMessage(bot)
    async def checker_task():
        while True:
            try:
                await checker.check_all_users()
            except Exception as e:
                logging.error(f"Error in checker_task: {e}")
            await asyncio.sleep(24 * 60 * 60)  
    async def sender_task():
        while True:
            try:
                await sender.check_all_users()
            except Exception as e:
                logging.error(f"Error in sender_task: {e}")
            await asyncio.sleep(5 * 60)  
    asyncio.create_task(checker_task())
    asyncio.create_task(sender_task())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
