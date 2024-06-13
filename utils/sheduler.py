import json

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


async def reminder(bot: Bot):
    # Открываем файл для чтения
    with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
        # Загружаем JSON-данные из файла
        data = json.load(file)
        user_ids = []
        for building in data.values():
            user_ids.extend(building['users'].keys())
    # user_ids = ['504609639', '400551767']
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text="Please don't forget to send the report 📧")
        except TelegramBadRequest:
            print(f"Unable to send message to {user_id}")
