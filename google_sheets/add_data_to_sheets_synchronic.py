import gspread
from gspread import Client, Spreadsheet, Worksheet
from datetime import datetime


def update_cells_by_results(sh: Spreadsheet, data: dict, name: str):
    """
    Функция записывает в googlesheet количество использованного материала
    :param sh: Spreadsheet
    :param data: dict
    :param name: str
    :return: None
    """
    # Получем текущий месяц и год для опредеоения в какую таблицу записывать
    now = datetime.now()
    current_month = now.strftime("%B").lower()  # преобразуем в нижний регистр
    current_year = now.strftime("%Y")
    ws_name = f"results_{current_month}_{current_year}"
    ws: Worksheet = sh.worksheet(ws_name)

    day = now.day
    row = ws.find(name).row + day + 2
    material_data: dict = data.get('material')
    for key, value in material_data.items():
        col = ws.find(key).col
        ws.update_cell(row, col, value)
        print(f"Обновление ячейки ({row}, {col}) со значением {value}")


def update_cells_by_work_time(sh: Spreadsheet, data: dict, name: str):
    """
    Функция записывает данные количества отработанного времени
    :param sh: Spreadsheet
    :param data: dict
    :param name: str
    :return: None
    """
    ws: Worksheet = sh.worksheet('work_time')
    now = datetime.now()
    month_name = now.strftime("%B")
    start_row = ws.find(month_name).row
    values = ws.get_all_values()[start_row - 1:]
    user_row = 0

    for i, row in enumerate(values):
        if name in row:
            user_row = i + start_row
            print(f"Значение найдено в строке с индексом: {i + start_row}")
            break

    day = now.day
    col = int(day) + 2
    value = data.get('work_time')
    print(f"Обновление ячейки ({user_row}, {col}) со значением {value}")
    ws.update_cell(user_row, col, value)


def save_data_in_tables(id: int, data: dict):
    gc: Client = gspread.service_account('./google_sheets_key.json')
    sh = gc.open_by_url(data.get('sh_url'))
    name = data.get('name')
    update_cells_by_work_time(sh=sh, data=data, name=name)
    update_cells_by_results(sh=sh, data=data, name=name)


def save_photo_url(user: int, data: dict):
    now = datetime.now()
    current_month = now.strftime("%B").lower()  # преобразуем в нижний регистр
    current_year = now.strftime("%Y")
    ws_name = f"photos_{current_month}_{current_year}"
    day = now.day
    name = data.get('name')
    gc: Client = gspread.service_account('./google_sheets_key.json')
    sh = gc.open_by_url(data.get('sh_url'))
    ws: Worksheet = sh.worksheet(ws_name)
    photos = data.get('photos')
    row = ws.find(name).row + day
    col = 1

    for photo in photos:
        col += 1
        ws.update_cell(row=row, col=col, value=photo)
        print(f"Обновление ячейки ({row}, {col}) со значением {photo}")

