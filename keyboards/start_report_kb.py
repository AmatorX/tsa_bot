from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_report_btn = InlineKeyboardButton(
    text='Start report ✅',
    callback_data='start_report'
)

cancel_report_btn = InlineKeyboardButton(
    text='Cancel ❌',
    callback_data='cancel_report'
)

start_report_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [start_report_btn, cancel_report_btn]
    ]
)