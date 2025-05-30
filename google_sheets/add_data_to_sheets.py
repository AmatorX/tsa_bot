import os

import gspread_asyncio
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

from utils.add_data_to_db import add_work_entry


def get_creds():
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'google_sheets_key.json')
    creds = Credentials.from_service_account_file(creds_path)
    # creds = Credentials.from_service_account_file("./google_sheets_key.json")
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


async def save_photo_url(message: Message, state: FSMContext, data):
    timezone = pytz.timezone('America/Edmonton')
    now = datetime.now(timezone)
    current_month = now.strftime("%B")
    current_year = now.strftime("%Y")
    ws_name = f"photos_{current_month}_{current_year}"
    day = now.day
    name = data.get('name')
    agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    gc = await agcm.authorize()
    sh = await gc.open_by_url(data.get('sh_url'))
    ws = await sh.worksheet(ws_name)
    photos = data.get('photos')
    try:
        cell = await ws.find(name)
        row = cell.row + day
        col = 1
        for photo in photos:
            col += 1
            await ws.update_cell(row=row, col=col, value=photo)
            # print(f"Обновление ячейки ({row}, {col}) со значением {photo}")
    except AttributeError:
        await message.answer('Recording is not possible❗️\n '
                             'You are not found in the photos table!\n '
                             'Contact the administrator')
        await state.clear()
        print('Пользователь не найден в таблице PHOTOS')


# async def add_data(message: Message, state: FSMContext, sh, name, data):
#     try:
#         ws = await sh.worksheet('Work Time')
#         timezone = pytz.timezone('America/Edmonton')
#         now = datetime.now(timezone)
#         # month_day = now.strftime("%B %d")
#         month_day = now.strftime("%B ") + str(int(now.strftime("%d")))
#         # month_name = now.strftime("%B")
#         cell = await ws.find(month_day)
#         start_row = cell.row
#         end_row = start_row + 100
#         values = await ws.get_all_values()
#
#         values = values[start_row - 1:end_row]
#
#         user_row = 0
#
#         for i, row in enumerate(values):
#             if name in row:
#                 user_row = i + start_row
#                 print(f"Значение найдено в строке с индексом: {i + start_row}")
#                 break
#
#         day = str(now.day)
#         # col = int(day) + 2
#         # cell_day = await ws.find(day)
#         # col = cell_day.col
#         col = cell.col
#         value = data.get('work_time')
#         print(f"Обновление ячейки ({user_row}, {col}) со значением {value}")
#         await ws.update_cell(user_row, col, value)
#
#         current_month = now.strftime("%B")
#         current_year = now.strftime("%Y")
#         ws_name = f"results_{current_month}_{current_year}"
#         print(f'Ищем таблицу {ws_name}')
#         ws = await sh.worksheet(ws_name)
#
#         day = now.day
#         cell = await ws.find(name)
#         row = cell.row + day + 4
#         material_data = data.get('material')
#         for key, value in material_data.items():
#             cur_col = await ws.find(key)
#             col = cur_col.col
#             await ws.update_cell(row, col, value)
#             print(f"Обновление ячейки ({row}, {col}) со значением {value}")
#     except:
#         await message.edit_text('Recording is not possible❗️\n '
#                                 'You are not found in the results table or in the working hours table!\n '
#                                 'Contact the administrator')
#         await state.clear()
#         print('Пользователь не найден в таблице WORK TIME или RESULTS')
#     add_work_entry(worker_name=data.get('name'),
#                    build_object_name=data.get('building'),
#                    work_time=data.get('work_time'),
#                    materials=data.get('material'))
#
#
# async def save_data_in_tables(message: Message, state: FSMContext, data: dict):
#     """
#     Функция записывает данные в гугл шитс
#     :param message: text
#     :param state: FSMContext
#     :param data: dict
#     :return: None
#     """
#     # creds = Credentials.from_authorized_user_file('path/to/credentials.json')
#     agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
#     gc = await agcm.authorize()
#     sh = await gc.open_by_url(data.get('sh_url'))
#     name = data.get('name')
#     await add_data(message=message, state=state, sh=sh, data=data, name=name)

async def add_data(message: Message, state: FSMContext, data):
    try:
        add_work_entry(worker_name=data.get('name'),
                       build_object_name=data.get('building'),
                       work_time=data.get('work_time'),
                       materials=data.get('material'))

    except:
        await message.edit_text('Recording is not possible❗️\n '
                                'You are not found in the results table or in the working hours table!\n '
                                'Contact the administrator')
        await state.clear()
        print('Пользователь не найден в таблице WORK TIME или RESULTS')



async def save_data_in_tables(message: Message, state: FSMContext, data: dict):
    """
    Функция записывает данные в гугл шитс
    :param message: text
    :param state: FSMContext
    :param data: dict
    :return: None
    """
    # creds = Credentials.from_authorized_user_file('path/to/credentials.json')
    # agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
    # gc = await agcm.authorize()
    # sh = await gc.open_by_url(data.get('sh_url'))
    # name = data.get('name')
    await add_data(message=message, state=state, data=data)