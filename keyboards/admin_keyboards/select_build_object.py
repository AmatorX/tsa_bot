from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


north_bldg_c = InlineKeyboardButton(
    text='north_bldg_c',
    callback_data='north_bldg_c'
)

savanna_2_bldg1 = InlineKeyboardButton(
    text='savanna_2_bldg1',
    callback_data='savanna_2_bldg1'
)

willows_bldg3 = InlineKeyboardButton(
    text='willows_bldg3',
    callback_data='willows_bldg3'
)

willows_bldg4 = InlineKeyboardButton(
    text='willows_bldg4',
    callback_data='willows_bldg4'
)

cancel = InlineKeyboardButton(
    text='Cancel',
    callback_data='cancel'
)

select_binding_object_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [north_bldg_c, savanna_2_bldg1],
        [willows_bldg3, willows_bldg4],
        [cancel]
    ]
)