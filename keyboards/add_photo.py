from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


confirm_btn = InlineKeyboardButton(
    text='Add a photo to the report',
    callback_data='add_photo'
)
cancel_btn = InlineKeyboardButton(
    text="Confirm sending",
    callback_data='complete_report'
)

add_photo_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [cancel_btn]
    ]
)