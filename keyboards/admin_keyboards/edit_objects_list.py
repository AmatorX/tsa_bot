from typing import Union

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_to_edit(data: Union[dict, list]):
    keyboard = []
    if type(data) is dict:
        # keyboard = []
        for user_id, user_name in data.items():
            callback_data = f"{user_id},{user_name}"  # формирование callback_data
            button = InlineKeyboardButton(text=user_name, callback_data=callback_data)
            keyboard.append([button])  # Добавление кнопки в список
        # button = InlineKeyboardButton(text='Cancel', callback_data='cancel')
        # keyboard.append([button])
        # users_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # return users_kb
    elif type(data) is list:
        # keyboard = []
        for material in data:
            button = InlineKeyboardButton(text=material, callback_data=material)
            keyboard.append([button])

    button = InlineKeyboardButton(text='Cancel', callback_data='cancel')
    keyboard.append([button])
    select_target_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return select_target_kb

