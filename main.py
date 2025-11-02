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
    )

    checker = SubscriptionChecker(bot)
    sender = SendMessage(bot)

    async def periodic_check():
        while True:
         
            await checker.check_all_users()

            await sender.check_all_users()
            
            await asyncio.sleep(30)  

    asyncio.create_task(periodic_check())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
