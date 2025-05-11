import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError

from config_data.config import Config, load_config
from middlewares.album_middleware import AlbumMiddleware
from handlers import handlers, editing_handlers, admin_handlers
from utils.set_default_menu import set_main_menu
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.sheduler import no_report, remind_send_report, send_users_with_negative_statistics


# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config('.env')
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s,%(msecs)03d: %(levelname)s/%(processName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)

    # Инициализируем бот и диспетчер
    # bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    bot: Bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    # bot: Bot = Bot(token=config.tg_bot.token)
    dp: Dispatcher = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='America/Edmonton')
    scheduler.add_job(remind_send_report, trigger='cron', day_of_week='mon-sat', hour=13, minute=35, kwargs={'bot': bot})
    # scheduler.add_job(no_report, trigger='cron', day_of_week='mon-sat', hour=4, minute=36, kwargs={'bot': bot})
    scheduler.add_job(no_report, trigger='cron', hour=4, minute=45, kwargs={'bot': bot})
    scheduler.add_job(send_users_with_negative_statistics, trigger='cron', day_of_week='mon-sat', hour=13, minute=39, kwargs={'bot': bot})
    scheduler.start()
    dp.message.middleware(AlbumMiddleware())
    dp.startup.register(set_main_menu)
    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(editing_handlers.router)
    dp.include_router(handlers.router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info('Bot started')
        await dp.start_polling(bot)
    except TelegramAPIError as err:
        logger.error(f"Telegram API Error: {err}")
    finally:
        await bot.close()
        logger.info('Bot closed')


if __name__ == '__main__':
    asyncio.run(main())
