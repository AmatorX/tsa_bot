import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_buttons_list(data: dict):
    """
    Функция принимает id пользователя и формирует список кнопок для него
    Поскольку функция вызывается не из текущей директории то путь к файлу json
    строится на основании директории handlers
    :param data: dict
    :return: InlineKeyboardButton
    """
    buttons_list = data.get('materials')
    buttons = []
    for button in buttons_list:
        btn = InlineKeyboardButton(text=button, callback_data=button)
        buttons.append(btn)
    return buttons


def get_build_materials_kb(data: dict):
    """
    Функция формирует объект клавиатуры с набором кнопок в зависимости от того
    в какой группе состоит пользователь
    :param data: dict
    :return: InlineKeyboardMarkup
    """
    buttons = get_buttons_list(data)
    buttons_groups = [buttons[n:n + 3] for n in range(0, len(buttons), 3)]

    build_materials_kb = InlineKeyboardMarkup(
        inline_keyboard=buttons_groups
    )
    return build_materials_kb
