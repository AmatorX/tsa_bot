from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


add_btn = InlineKeyboardButton(
    text='Add material',
    callback_data='add_material'
)

del_btn = InlineKeyboardButton(
    text='Delete material',
    callback_data='delete_material'
)

cancel = InlineKeyboardButton(
    text='Cancel',
    callback_data='cancel'
)

select_action_material_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [add_btn, del_btn, cancel]
    ]
)