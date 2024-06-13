from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


work_time = InlineKeyboardButton(
    text='Hours worked 🕔',
    callback_data='edit_work_time'
)
material = InlineKeyboardButton(
    text='Material 🧱',
    callback_data='edit_material'
)


edit_report_data_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [work_time, material]
    ]
)