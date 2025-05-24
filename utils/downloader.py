# import os
# from datetime import datetime
#
# import aiohttp
# import aiofiles
# import pytz
#
#
# async def save_to_server_photos(data):
#     """
#     Функция скачивания и сохранения фото на сервер
#     """
#     name = data['name']
#     building = data['building']
#     photos = data['photos']
#     timezone = pytz.timezone('America/Edmonton')
#     date_str = datetime.now(timezone).strftime("%d_%m_%Y")
#     folder_path = os.path.join("media", building, date_str, name)
#
#     # Создание папки, если она не существует (включая все промежуточные каталоги)
#     os.makedirs(folder_path, exist_ok=True)
#
#     async with aiohttp.ClientSession() as session:
#         for i, url in enumerate(photos, 1):
#             async with session.get(url) as response:
#                 photo_data = await response.read()
#
#                 # Сохранение фото
#                 async with aiofiles.open(os.path.join(folder_path, f"photo_{i}.jpg"), mode='wb') as photo_file:
#                     await photo_file.write(photo_data)



import os
import aiohttp
import aiofiles
from datetime import datetime
import pytz

async def save_to_server_photos(data):
    """
    Функция скачивания и сохранения фото на сервер с отладочной информацией
    """
    try:
        name = data['name']
        building = data['building']
        photos = data['photos']

        timezone = pytz.timezone('America/Edmonton')
        date_str = datetime.now(timezone).strftime("%d_%m_%Y")
        folder_path = os.path.join("media", building, date_str, name)

        print(f"[INFO] Целевая папка: {folder_path}")

        try:
            os.makedirs(folder_path, exist_ok=True)
            print("[INFO] Папка успешно создана или уже существует.")
        except Exception as e:
            print(f"[ERROR] Ошибка при создании папки: {e}")
            return

        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(photos, 1):
                try:
                    print(f"[INFO] Скачиваем фото {i}: {url}")
                    async with session.get(url) as response:
                        if response.status == 200:
                            photo_data = await response.read()
                            file_path = os.path.join(folder_path, f"photo_{i}.jpg")
                            print(f"[INFO] Сохраняем фото в: {file_path}")
                            async with aiofiles.open(file_path, mode='wb') as photo_file:
                                await photo_file.write(photo_data)
                        else:
                            print(f"[WARNING] Не удалось скачать фото {i}: статус {response.status}")
                except Exception as e:
                    print(f"[ERROR] Ошибка при скачивании/сохранении фото {i}: {e}")

        print("[INFO] Завершено сохранение всех фото.")
    except Exception as e:
        print(f"[ERROR] Общая ошибка в save_to_server_photos: {e}")