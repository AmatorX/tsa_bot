import json
import os
import sqlite3
from datetime import date, datetime

import pytz
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from config_data.config import load_config, Config

config: Config = load_config('.env')

admin_send_remind_id = config.tg_bot.admin_send_remind_id
admin_ids = config.tg_bot.admin_ids


async def remind_send_report(bot: Bot):
    print('Start function remind_send_report')
    # base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию скрипта
    # db_path = os.path.join(base_dir, '../../tsa/db.sqlite3')  # Формируем путь к базе
    db_path = '/app/db/db.sqlite3' # При работе из докера

    # Подключаемся к базе данных SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 🔹 Получаем всех пользователей, у которых есть связь с объектом строительства
    cursor.execute("""
        SELECT tg_id 
        FROM tsa_app_worker 
        WHERE build_obj_id IS NOT NULL
    """)
    user_all_ids = [row[0] for row in cursor.fetchall()]

    # 🔹 Получаем пользователей, которые оставили отчёт за текущий день
    cursor.execute("""
        SELECT DISTINCT w.tg_id 
        FROM tsa_app_worker w 
        JOIN tsa_app_workentry we ON w.id = we.worker_id 
        WHERE we.date = DATE('now', '-7 hours')
    """)
    user_ids_report = [row[0] for row in cursor.fetchall()]

    conn.close()

    # 🔹 Ищем пользователей, которые не оставили отчёт
    users_to_remind = set(user_all_ids) - set(user_ids_report)

    # 🔹 Отправляем сообщения пользователям, которые ещё не отчитались
    for user_id in users_to_remind:
        try:
            await bot.send_message(
                user_id,
                text="You didn't send the report today. If you didn't work today, ignore this message"
            )
        except TelegramBadRequest:
            print(f"Unable to send message to {user_id}")


# async def no_report(bot: Bot):
#     base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию скрипта
#     db_path = os.path.join(base_dir, '../../tsa/db.sqlite')  # Формируем путь к базе
#
#     # Подключаемся к базе данных SQLite
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     # # Получаем всех пользователей из базы данных (tg_id и имена)
#     # cursor.execute("SELECT id, name FROM tsa_app_worker")
#     # all_users = cursor.fetchall()
#
#     # Получаем всех пользователей, у которых есть связь с объектом строительства
#     cursor.execute("SELECT id, name FROM tsa_app_worker WHERE build_obj_id IS NOT NULL")
#     all_users = cursor.fetchall()
#
#     # id всех пользователей
#     user_all_ids = {row[0]: row[1] for row in all_users}  # tg_id -> name
#
#     # Получаем worker_id пользователей, которые оставили отчёт (например, по сегодняшним данным)
#     cursor.execute("""
#         SELECT DISTINCT worker_id
#         FROM tsa_app_workentry
#         WHERE date = DATE('now', '-7 hours')
#     """)
#     # ('now', '-7 hours') в запросе потому что нужно учесть разницу во времени UTC и Калгари
#     # Когда в Калгари еще 1-е чиисло, по UTC дата уже 2-е число
#     worker_ids_report = [row[0] for row in cursor.fetchall()]
#
#     # Находим tg_id пользователей, которые не отправили отчёт
#     users_no_report = [
#         user_all_ids[tg_id]
#         for tg_id in user_all_ids.keys()
#         if tg_id not in worker_ids_report
#     ]
#     # Закрываем соединение с базой
#     conn.close()
#
#     if not users_no_report:
#         await bot.send_message(
#             admin_send_remind_id,
#             text="All employees have sent their reports. ✅"
#         )
#     else:
#         await bot.send_message(
#             admin_send_remind_id,
#             text=f"The employees did not send the report: {', '.join(users_no_report)}"
#         )


async def get_users_with_negative_statistics():
    print('Start function get_users_with_negative_statistics')
    # base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию скрипта
    # db_path = os.path.join(base_dir, '../../tsa/db.sqlite3')  # Формируем путь к базе
    db_path = '/app/db/db.sqlite3' # При работе из докера

    # Подключаемся к базе данных SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем все материалы из базы данных
    cursor.execute("SELECT name, price FROM tsa_app_material")
    all_materials = cursor.fetchall()

    # Создаем словарь для быстрого доступа к цене материала
    material_prices = {name: price for name, price in all_materials}

    # Получаем id работников, их имена и почасовую ставку зарплаты
    cursor.execute("SELECT id, name, salary FROM tsa_app_worker")
    id_name_salary = cursor.fetchall()

    # Создаем словари для быстрого доступа к зарплате и имени работника
    worker_salary = {worker_id: salary for worker_id, _, salary in id_name_salary}
    worker_name = {worker_id: name for worker_id, name, _ in id_name_salary}

    # Получаем всех пользователей, которые отправили отчет
    cursor.execute(
        "SELECT worker_id, worked_hours, materials_used FROM tsa_app_workentry WHERE date = DATE('now', '-7 hours')"
    )
    all_results = cursor.fetchall()

    efficiency_list = []  # Список для хранения [name, эффективность]

    # Рассчитываем эффективность для каждого пользователя
    for worker_id, worked_hours, materials_used in all_results:
        # Зарплата за день
        daily_salary = worked_hours * worker_salary.get(worker_id, 0)

        # Материалы, использованные за день, представлены как JSON-строка, парсим их
        materials_used_dict = json.loads(materials_used)  # Преобразуем строку в словарь (можно заменить на json.loads)

        # Считаем заработок за установку материалов
        earnings_from_materials = sum(
            material_prices.get(material, 0) * float(quantity)
            for material, quantity in materials_used_dict.items()
        )

        # Эффективность
        efficiency = round(earnings_from_materials - daily_salary, 2)
        print('efficiency', efficiency)

        # Добавляем в список только если эффективность отрицательная
        if efficiency < 0:
            efficiency_list.append([worker_name[worker_id], efficiency])

    conn.close()  # Закрываем соединение с базой
    print(f'Function get_users_with_negative_statistics return {efficiency_list}')
    return efficiency_list


# async def send_users_with_negative_statistics(bot: Bot):
#     efficiency_list = await get_users_with_negative_statistics()
#     if not efficiency_list:
#         await bot.send_message(
#             admin_send_remind_id,
#             text="No users with negative statistics for today."
#         )
#     else:
#         await bot.send_message(
#             admin_send_remind_id,
#             text="List of users with negative statistics:\n" +
#                  "\n".join(f"{name}: {efficiency}" for name, efficiency in efficiency_list)
#         )



async def send_users_with_negative_statistics(bot: Bot):
    print('Start function send_users_with_negative_statistics')

    # Получаем пользователей с отрицательной статистикой
    efficiency_list = await get_users_with_negative_statistics()  # [[name, efficiency], ...]

    if not efficiency_list:
        await bot.send_message(
            admin_send_remind_id,
            text="No users with negative statistics for today."
        )
        return

    # Отправляем админу общий список пользователей с отрицательной статистикой
    await bot.send_message(
        admin_send_remind_id,
        text="List of users with negative statistics:\n" +
             "\n".join(f"{name}: {efficiency}" for name, efficiency in efficiency_list)
    )

    # Получаем список работников для каждого бригадира
    foremen_workers = await get_foremen_workers()

    # Группируем пользователей с отрицательной статистикой по их бригадирам
    foremen_negative_stats = {}

    for name, efficiency in efficiency_list:
        for foreman_tg_id, workers in foremen_workers.items():
            # Проверяем, есть ли этот работник в списке подчиненных бригадира
            worker_id = next((wid for wid, wname in workers.items() if wname == name), None)
            if worker_id:
                if foreman_tg_id not in foremen_negative_stats:
                    foremen_negative_stats[foreman_tg_id] = []
                foremen_negative_stats[foreman_tg_id].append(f"{name}: {efficiency}")

    # Отправляем каждому бригадиру его работников с отрицательной статистикой
    for foreman_tg_id, workers_list in foremen_negative_stats.items():
        await bot.send_message(
            foreman_tg_id,
            text="Your workers with negative statistics:\n" + "\n".join(workers_list)
        )



async def get_foremen_workers():
    print('Start function get_foremen_workers')
    # base_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем директорию скрипта
    # db_path = os.path.join(base_dir, '../../tsa/db.sqlite3')  # Формируем путь к базе
    db_path = '/app/db/db.sqlite3' # При работе из докера
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем всех бригадиров
    cursor.execute("""
        SELECT id, tg_id, build_obj_id 
        FROM tsa_app_worker 
        WHERE foreman = 1 AND build_obj_id IS NOT NULL
    """)
    foremen = cursor.fetchall()  # [(id, tg_id, build_obj_id), ...]

    foremen_dict = {}

    for foreman_id, tg_id, build_obj_id in foremen:
        # Получаем рабочих, относящихся к тому же объекту
        cursor.execute("""
            SELECT id, name 
            FROM tsa_app_worker 
            WHERE build_obj_id = ? AND id != ?
        """, (build_obj_id, foreman_id))

        workers = {row[0]: row[1] for row in cursor.fetchall()}  # {id: name}

        if workers:  # Добавляем только если у бригадира есть рабочие
            foremen_dict[tg_id] = workers  # tg_id бригадира -> {id: name} рабочих

    conn.close()
    print(f'Function get_foremen_workers return {foremen_dict}')
    return foremen_dict


async def no_report(bot: Bot):
    print('Start function no_report')
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # db_path = os.path.join(base_dir, '../../tsa/db.sqlite3') # При работе локально
    db_path = '/app/db/db.sqlite3' # При работе из контейнера

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем всех пользователей, у которых есть связь с объектом строительства
    cursor.execute("SELECT id, name FROM tsa_app_worker WHERE build_obj_id IS NOT NULL")
    all_users = cursor.fetchall()

    # id всех пользователей
    user_all_ids = {row[0]: row[1] for row in all_users}  # id -> name

    # Получаем worker_id пользователей, которые отправили отчёт
    cursor.execute("""
        SELECT DISTINCT worker_id
        FROM tsa_app_workentry
        WHERE date = DATE('now', '-7 hours')
    """)
    worker_ids_report = {row[0] for row in cursor.fetchall()}  # Set для быстрого поиска

    # Находим пользователей, которые не отправили отчёт
    users_no_report = {
        worker_id: user_all_ids[worker_id]
        for worker_id in user_all_ids
        if worker_id not in worker_ids_report
    }

    conn.close()

    # Отправляем админу сообщение о тех, кто не отправил отчет
    if not users_no_report:
        await bot.send_message(admin_send_remind_id, "All employees have sent their reports. ✅")
    else:
        await bot.send_message(
            admin_send_remind_id,
            text=f"The employees did not send the report: {', '.join(users_no_report.values())}"
        )

    # 🔹 Получаем список рабочих для каждого бригадира
    foremen_workers = await get_foremen_workers()

    # Отправляем бригадирам список их работников, которые не сдали отчет
    for foreman_tg_id, workers in foremen_workers.items():
        # Фильтруем тех, кто не отправил отчет
        workers_no_report = [name for worker_id, name in workers.items() if worker_id in users_no_report]

        if workers_no_report:
            await bot.send_message(
                foreman_tg_id,
                text=f"Your workers did not send the report: {', '.join(workers_no_report)}"
            )


async def send_admin_statistics_for_the_day_by_team(bot: Bot):
    print("Запуск функции отправки статистики по командам за день")
    tz = pytz.timezone("America/Edmonton")
    today_str = datetime.now(tz).strftime("%Y-%m-%d")

    file_dir = "/app/db"
    file_path = os.path.join(file_dir, f"{today_str}.txt")

    if not os.path.exists(file_path):
        for admin_id in admin_ids:
            await bot.send_message(admin_id, f"The statistics file for {today_str} was not found.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("The file does not contain a valid dictionary.")

        # Убираем пустые, None и нулевые значения
        filtered_data = {
            key: value for key, value in data.items()
            if value not in (None, 0, 0.0, "", " ")
        }

        if not filtered_data:
            for admin_id in admin_ids:
                await bot.send_message(admin_id, "No meaningful statistics to display today.")
            return

        message_lines = ["📊 *Team statistics for today:*"]
        for key, value in filtered_data.items():
            message_lines.append(f"- `{key}`: *{value}*")

        message = "\n".join(message_lines)

        for admin_id in admin_ids:
            await bot.send_message(
                admin_id,
                message,
            )

    except Exception as e:
        error_msg = f"Error reading the file: {e}"
        for admin_id in admin_ids:
            await bot.send_message(admin_id, error_msg)

