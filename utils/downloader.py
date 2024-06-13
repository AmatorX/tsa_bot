import os
from datetime import datetime

import aiohttp
import aiofiles
import pytz


async def save_to_server_photos(data):
    """
    Функция скачивания и сохранения фото на сервер
    """
    name = data['name']
    building = data['building']
    photos = data['photos']
    timezone = pytz.timezone('America/Edmonton')
    date_str = datetime.now(timezone).strftime("%d_%m_%Y")
    folder_path = os.path.join("media", building, date_str, name)

    # Создание папки, если она не существует (включая все промежуточные каталоги)
    os.makedirs(folder_path, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(photos, 1):
            async with session.get(url) as response:
                photo_data = await response.read()

                # Сохранение фото
                async with aiofiles.open(os.path.join(folder_path, f"photo_{i}.jpg"), mode='wb') as photo_file:
                    await photo_file.write(photo_data)