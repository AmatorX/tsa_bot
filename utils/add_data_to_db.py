import os
import sqlite3
import json
from datetime import datetime

import pytz


# def add_work_entry(worker_name: str, build_object_name: str, work_time: float, materials: dict):
#
#     """
#     Функция для добавления записи в базу данных WorkEntry.
#
#     :param worker_name: Имя рабочего.
#     :param build_object_name: Имя объекта строительства.
#     :param work_time: Отработанное время в часах.
#     :param materials: Словарь с материалами (например, {'material1': 2, 'material2': 12.5}).
#     :param db_path: Путь к базе данных SQLite.
#     """
#     print(f'Функция add_work_entry. Добавлены данные:\n'
#           f'worker_name: {worker_name}, build_object_name: {build_object_name}, work_time: {work_time}, materials: {materials}')
#     base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию скрипта
#     db_path = os.path.join(base_dir, '../../tsa/db.sqlite')  # Формируем путь к базе
#     print(f"Connecting to database at: {db_path}")
#
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     try:
#         # Проверить, существует ли рабочий с указанным именем
#         cursor.execute("SELECT id FROM tsa_app_worker WHERE name = ?", (worker_name,))
#         worker = cursor.fetchone()
#         if not worker:
#             raise ValueError(f"Worker with name '{worker_name}' not found.")
#         worker_id = worker[0]
#
#         # Проверить, существует ли объект строительства с указанным именем
#         cursor.execute("SELECT id FROM tsa_app_buildobject WHERE name = ?", (build_object_name,))
#         build_object = cursor.fetchone()
#         if not build_object:
#             raise ValueError(f"Build object with name '{build_object_name}' not found.")
#         build_object_id = build_object[0]
#
#         # Добавить запись в таблицу WorkEntry
#         cursor.execute("""
#             INSERT INTO tsa_app_workentry (worker_id, build_object_id, worked_hours, materials_used, date)
#             VALUES (?, ?, ?, ?, DATE('now'))
#         """, (worker_id, build_object_id, work_time, json.dumps(materials)))
#
#         conn.commit()
#         print("Work entry added successfully.")
#
#     except Exception as e:
#         print(f"Error: {e}")
#         conn.rollback()
#
#     finally:
#         conn.close()

def add_work_entry(worker_name: str, build_object_name: str, work_time: float, materials: dict):
    """
    Функция для добавления записи в базу данных WorkEntry.

    :param worker_name: Имя рабочего.
    :param build_object_name: Имя объекта строительства.
    :param work_time: Отработанное время в часах.
    :param materials: Словарь с материалами (например, {'material1': 2, 'material2': 12.5}).
    """
    print(f'Функция add_work_entry. Добавлены данные:\n'
          f'worker_name: {worker_name}, build_object_name: {build_object_name}, work_time: {work_time}, materials: {materials}')
    # base_dir = os.path.dirname(os.path.abspath(__file__))  # При работе локально
    # db_path = os.path.join(base_dir, '../../TSA/db.sqlite3')
    db_path = '/app/db/db.sqlite3' # При работе из докера

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timezone = pytz.timezone('America/Edmonton')
    now = datetime.now(timezone)
    today = now.date()
    now_time = datetime.now(timezone).time()
    now_time_str = now_time.strftime('%H:%M')

    try:
        # Проверить, существует ли рабочий с указанным именем
        cursor.execute("SELECT id FROM tsa_app_worker WHERE name = ?", (worker_name,))
        worker = cursor.fetchone()
        if not worker:
            raise ValueError(f"Worker with name '{worker_name}' not found.")
        worker_id = worker[0]

        # Проверить, существует ли объект строительства с указанным именем
        cursor.execute("SELECT id FROM tsa_app_buildobject WHERE name = ?", (build_object_name,))
        build_object = cursor.fetchone()
        if not build_object:
            raise ValueError(f"Build object with name '{build_object_name}' not found.")
        build_object_id = build_object[0]

        # Проверить, есть ли запись за сегодня для этого рабочего и объекта строительства

        cursor.execute("""
            SELECT id FROM tsa_app_workentry 
            WHERE worker_id = ? AND build_object_id = ? AND date = ?
        """, (worker_id, build_object_id, today))

        existing_entry = cursor.fetchone()

        if existing_entry:
            # Если запись уже существует, обновляем её
            # cursor.execute("""
            #     UPDATE tsa_app_workentry
            #     SET worked_hours = ?, materials_used = ?
            #     WHERE id = ?
            # """, (work_time, json.dumps(materials), existing_entry[0]))
            cursor.execute("""
                UPDATE tsa_app_workentry
                SET worked_hours = ?, materials_used = ?, created_time = ?
                WHERE id = ?
            """, (work_time, json.dumps(materials), now_time_str, existing_entry[0]))
            print("Work entry updated successfully.")
        else:
            # Если записи нет, добавляем новую
            # cursor.execute("""
            #     INSERT INTO tsa_app_workentry (worker_id, build_object_id, worked_hours, materials_used, date)
            #     VALUES (?, ?, ?, ?, ?)
            # """, (worker_id, build_object_id, work_time, json.dumps(materials), today))
            # print("Work entry added successfully.")

            cursor.execute("""
                INSERT INTO tsa_app_workentry (worker_id, build_object_id, worked_hours, materials_used, date, created_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (worker_id, build_object_id, work_time, json.dumps(materials), today, now_time_str))
            print("Work entry added successfully.")

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        conn.close()


