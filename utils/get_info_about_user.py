import json
import sqlite3


def get_user_info(tg_id: int, db_path: str):
    """
    Функция для получения данных пользователя из базы данных SQLite.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверка наличия таблицы tsa_app_worker
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tsa_app_worker';")
    if not cursor.fetchone():
        print("Таблица tsa_app_worker не найдена.")
        conn.close()
        return None, None, None, None

    # Запрос для получения информации о пользователе
    cursor.execute("""
        SELECT w.name, b.sh_url, b.name
        FROM tsa_app_worker w
        LEFT JOIN tsa_app_buildobject b ON w.build_obj_id = b.id
        WHERE w.tg_id = ?
    """, (tg_id,))

    user_info = cursor.fetchone()

    if not user_info:
        conn.close()
        return None, None, None, None

    name, sh_url, building = user_info

    # Запрос для получения материалов (только имена)
    cursor.execute("""
        SELECT m.name
        FROM tsa_app_material m
        JOIN tsa_app_buildobject_material bm ON m.id = bm.material_id
        WHERE bm.buildobject_id = (
            SELECT build_obj_id
            FROM tsa_app_worker
            WHERE tg_id = ?
        )
    """, (tg_id,))

    materials = [row[0] for row in cursor.fetchall()]

    conn.close()
    print(f'name: {name}, materials: {materials}, building: {building}')
    return name, sh_url, materials, building


# # Пример использования функции
# tg_id = 5258530182  # Замените на реальный tg_id
# db_path = '../db.sqlite'  # Замените на реальный путь к файлу базы данных
# name, sh_url, materials, building = get_user_info(tg_id, db_path)
# print(f"Name: {name}, SH URL: {sh_url}, Materials: {materials}, Building: {building}")


#
#
# def get_user_info(user_id: int, path: str):
#     """
#     Функция для получения данных пользователя для добавления их в data машины состояний
#     """
#     name, sh_url, materials = None, None, None
#     with open(path, 'r', encoding="utf-8") as file:
#         data = json.load(file)
#         for key, building_data in data.items():
#             users = building_data.get("users", {})
#             if str(user_id) in users:
#                 name = users.get(str(user_id))
#                 sh_url = building_data.get("sh_url", None)
#                 materials = building_data.get("materials", {})
#                 building = key
#                 return name, sh_url, materials, building
#
#
# tg_id = 6283837485  # Замените на реальный tg_id
# db_path = '../admin_config/main.json'  # Замените на реальный путь к файлу базы данных
# name, sh_url, materials, building = get_user_info(tg_id, db_path)
# print(f"Name: {name}, SH URL: {sh_url}, Materials: {materials}, Building: {building}")
