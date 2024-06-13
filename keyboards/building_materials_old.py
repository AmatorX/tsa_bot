import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from config_data.config_group_users import (north_bldg_c, north_bldg_c_materials, savanna_2_bldg1,
#                                             savanna_2_bldg1_materials, willows_bldg3, willows_bldg3_materials,
#                                             willows_bldg4,
#                                             willows_bldg4_materials)


# def get_build_materials_kb(user_id):
#     """
#     Функция формирует объект клавиатуры с набором кнопок в зависимости от того
#     в какой группе состоит пользователь
#     :param user_id: int
#     :return: InlineKeyboardMarkup
#     """
#     buttons = []
#     if user_id in willows_bldg3.keys():
#         for element in willows_bldg3_materials:
#             btn = InlineKeyboardButton(text=element, callback_data=element)
#             buttons.append(btn)
#     elif user_id in willows_bldg4.keys():
#         for element in willows_bldg4_materials:
#             btn = InlineKeyboardButton(text=element, callback_data=element)
#             buttons.append(btn)
#     elif user_id in savanna_2_bldg1.keys():
#         for element in savanna_2_bldg1_materials:
#             btn = InlineKeyboardButton(text=element, callback_data=element)
#             buttons.append(btn)
#     elif user_id in north_bldg_c.keys():
#         for element in north_bldg_c_materials:
#             btn = InlineKeyboardButton(text=element, callback_data=element)
#             buttons.append(btn)
#
#     # Группировка кнопок по три в строке
#     buttons = [buttons[n:n+3] for n in range(0, len(buttons), 3)]
#     print(buttons)
#
#     build_materials_kb = InlineKeyboardMarkup(
#         inline_keyboard=buttons
#     )
#     return build_materials_kb


def get_buttons_list(user_id):
    """
    Функция принимает id пользователя и формирует список кнопок для него
    Поскольку функция вызывается не из текущей директории то путь к файлу json
    строится на основании директории handlers
    :param user_id: int
    :return: InlineKeyboardButton
    """
    user_group = get_user_group(user_id)
    with open("./admin_config/building_objects/building_objects.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        buttons_list = data.get(user_group)
        buttons = []
        for button in buttons_list:
            btn = InlineKeyboardButton(text=button, callback_data=button)
            buttons.append(btn)
        return buttons


def get_user_group(user_id):
    """
    Функция принимает id пользователя и возвращает его группу
    Поскольку функция вызывается не из текущей директории то путь к файлу json
    строится на основании директории handlers
    :param user_id: int
    :return: str
    """
    with open("./admin_config/users_groups/users_groups.json", "r", encoding="utf-8") as users_groups:
        data = json.load(users_groups)
        for key in data:
            if str(user_id) in data.get(key):
                # print(key)
                return key


def get_build_materials_kb(user_id):
    """
    Функция формирует объект клавиатуры с набором кнопок в зависимости от того
    в какой группе состоит пользователь
    :param user_id: int
    :return: InlineKeyboardMarkup
    """
    buttons = get_buttons_list(user_id)
    buttons_groups = [buttons[n:n + 3] for n in range(0, len(buttons), 3)]

    build_materials_kb = InlineKeyboardMarkup(
        inline_keyboard=buttons_groups
    )
    return build_materials_kb
