from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Launching the bot'),
        BotCommand(command='/report',
                   description='Submit a new report'),
        BotCommand(command='/cancel',
                   description='Cancel All'),
        BotCommand(command='/admin',
                   description='Go to the admin menu'),
    ]

    await bot.set_my_commands(main_menu_commands)
