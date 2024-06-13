from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


users_btn = InlineKeyboardButton(
    text='Edit users',
    callback_data='admin_users_menu'
)

objects_btn = InlineKeyboardButton(
    text='Edit materials',
    callback_data='admin_building_material_menu'
)

exit_btn = InlineKeyboardButton(
    text='Exit admin mode',
    callback_data='admin_exit_admin_mode'
)

users_list = InlineKeyboardButton(
    text='Users list',
    callback_data='admin_users_list'
)

materials_list = InlineKeyboardButton(
    text='Materials list',
    callback_data='admin_materials_list'
)

menu_selection_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [users_list, materials_list],
        [users_btn, objects_btn],
        [exit_btn]
    ]
)