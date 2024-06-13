from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_btn = InlineKeyboardButton(
    text='Add more materials 🧱',
    callback_data='add_materials'
)
edit_btn = InlineKeyboardButton(
    text="Don't add more ➡️",
    callback_data='not_add_materials'
)

confirm_cancel_add_materials_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [confirm_btn, edit_btn]
    ]
)