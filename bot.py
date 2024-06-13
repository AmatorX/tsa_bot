import asyncio
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError

from config_data.config import Config, load_config
from middlewares.album_middleware import AlbumMiddleware
from handlers import handlers, editing_handlers, admin_handlers
from utils.set_default_menu import set_main_menu
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.sheduler import reminder


# Функция конфигурирования и запуска бота
async def main() -> None:

    # Загружаем конфиг в переменную config
    config: Config = load_config('.env')

    # Инициализируем бот и диспетчер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()
    scheduler = AsyncIOScheduler(timezone='America/Edmonton')
    scheduler.add_job(reminder, trigger='cron', day_of_week='mon-sat', hour=16, minute=55, kwargs={'bot': bot})
    scheduler.start()
    dp.message.middleware(AlbumMiddleware())
    dp.startup.register(set_main_menu)
    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(editing_handlers.router)
    dp.include_router(handlers.router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print('Bot started')
        await dp.start_polling(bot)
    except TelegramAPIError as err:
        print(f"Telegram API Error: {err}")
    finally:
        await bot.close()
        print('Bot closed')


if __name__ == '__main__':
    asyncio.run(main())
