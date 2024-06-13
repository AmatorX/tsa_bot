from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


create_user = InlineKeyboardButton(
    text='Create a new user',
    callback_data='create_user'
)

move_user = InlineKeyboardButton(
    text='Move user',
    callback_data='move_user'
)

delete_user = InlineKeyboardButton(
    text='Delete user',
    callback_data='delete_user'
)

cancel = InlineKeyboardButton(
    text='Cancel',
    callback_data='cancel'
)

select_crud_user_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_user],
        [move_user],
        [delete_user],
        [cancel]
    ]
)