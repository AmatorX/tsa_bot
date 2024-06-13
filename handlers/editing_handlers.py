import re

from aiogram import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.handlers import material_used
from keyboards.building_materials_old import get_build_materials_kb
from keyboards.confirm_kb import confirm_cancel_kb
from states import States

# Инициализируем роутер уровня модуля
router: Router = Router()
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()


@router.callback_query(StateFilter(States.edit_data) and F.data == 'edit_work_time')
async def edit_work_time(callback: CallbackQuery, state: FSMContext):
    """
    Функция перехватывает callback на изменение work time
    """
    await callback.message.answer(text='Enter the number of hours worked')
    await callback.message.edit_reply_markup()
    await callback.answer()
    await state.set_state(States.edit_work_time)


@router.message(StateFilter(States.edit_work_time))
async def select_building_material(message: Message, state: FSMContext):
    if re.fullmatch(r'^\d+([.,]\d+)?$', message.text):
        work_time = message.text.replace('.', ',')
        check_num = float(message.text.replace(',', '.'))
        if check_num <= 15:
            await state.update_data(work_time=work_time)
            data = await state.get_data()
            material_text = '\n'.join(f"{material}: {quantity}" for material, quantity in data['material'].items())
            await message.answer(text=f"You have entered the following data for the report:\n"
                                      f"Worked hours: <b>{data['work_time']}</b>\n"
                                      f"Materials used:\n{material_text}")
            await message.answer(text=f"Confirm sending the report or edit the data",
                                 reply_markup=confirm_cancel_kb)
        else:
            # await state.set_state(States.building_materials)
            await message.reply("Invalid input❗️\nEnter the correct number! The number should not be more than 15!")
    else:
        # await state.set_state(States.building_materials)
        await message.reply("Invalid input❗️\nEnter the correct number!")

