from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_btn = InlineKeyboardButton(
    text='Confirm ✅',
    callback_data='confirm'
)
edit_btn = InlineKeyboardButton(
    text='Edit 📝',
    callback_data='edit'
)

confirm_cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [confirm_btn, edit_btn]
    ]
)