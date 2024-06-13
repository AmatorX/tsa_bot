from typing import Union
import re

from aiogram import Router
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from utils.get_info_about_user import get_user_info
from keyboards.start_report_kb import start_report_kb
from keyboards.building_materials import get_build_materials_kb
from keyboards.confirm_kb import confirm_cancel_kb
from keyboards.edit_data_kb import edit_report_data_kb
from keyboards.add_more_materials import confirm_cancel_add_materials_kb
from states.states import States
from google_sheets.add_data_to_sheets import save_data_in_tables, save_photo_url
from utils.downloader import save_to_server_photos
import os

# Получить текущий путь к директории, где находится текущий файл
current_dir = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу db.sqlite.3 относительно текущего файла
db_path = os.path.join(current_dir, '../../tsa/db.sqlite')

# Инициализируем роутер уровня модуля
router: Router = Router()
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['cancel']))
async def process_help_command(message: Message, state: FSMContext):
    await state.clear()
    await message.reply(f'Progress is reset. If necessary, start over...')


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer('Welcome to the bot. to create and send a report, '
                         'select the <b>"report"</b> command in the menu')


@router.message(Command(commands=["report"]))
async def process_report_command(message: Message, state: FSMContext):
    await state.clear()
    try:
        # Здесь добавляются данные для DATA, которые берутся из JSON
        # Заменить на выборку из Базы Данных!
        name, sh_url, materials, building = get_user_info(message.from_user.id, db_path=db_path)

        if name:
            await state.update_data(name=name, sh_url=sh_url, materials=materials, building=building)
            data = await state.get_data()
            await state.set_state(States.start_report)
            await message.answer('Would you like to send a report on the work done?',
                                 reply_markup=start_report_kb)
    except:
        await message.answer(text='You are not registered in the bot❗️ Contact the administrator')


# Хендлер обрабатывающий начало отчета
@router.callback_query(StateFilter(States.start_report) and F.data == 'start_report')
async def start_report(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer(text='Enter the number of hours worked 🕔')
    await callback.answer()
    await state.set_state(States.work_time)


# Хендлер обработки отмены отчета
@router.callback_query(StateFilter(States.start_report))
async def cancel_report(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer(text="The report has been canceled!", show_alert=True)
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text='The report has been canceled!')


@router.message(StateFilter(States.work_time))
async def select_building_material(event: Union[Message, CallbackQuery], state: FSMContext):
    """
    Функция выбора материалов. Предлагает клавиатуру выбора материалов
    В режиме редактирования соабатывает if instance
    """
    if isinstance(event, Message):
        # if re.fullmatch(r'^\d+([.,]\d+)?$', event.text):
        if re.fullmatch(r'^[1-9]\d*([.,]\d+)?$', event.text):
            work_time = event.text.replace('.', ',')
            check_num = float(event.text.replace(',', '.'))
            if check_num <= 15:
                await state.update_data(work_time=work_time)
                data = await state.get_data()
                await event.answer(text=f'You entered <b>{data["work_time"]}</b> hours')
                await event.answer(text="Select the material used 🏗",
                                   reply_markup=get_build_materials_kb(data))
                await state.set_state(States.building_materials)
            else:
                await event.reply("Invalid input❗️ The number should not be more than 15!")
        else:
            await event.reply("Invalid input❗️\nEnter the correct number!")
    else:
        data = await state.get_data()
        await event.message.answer(text="Select the material used",
                                   reply_markup=get_build_materials_kb(data))
        await state.set_state(States.building_materials)


@router.callback_query(StateFilter(States.building_materials))
async def quantity_materials(callback: CallbackQuery, state: FSMContext):
    """
    Функция предлагает ввод количества материалов
    """

    await state.update_data(temp_material=callback.data)
    data = await state.get_data()
    await callback.message.answer(text=f"Your choice <b>{data['temp_material']}</b>")
    await callback.message.answer(text=f"Enter the amount of material used")
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.set_state(States.material_used)


@router.message(StateFilter(States.material_used))
async def material_used(message: Message, state: FSMContext):
    data = await state.get_data()
    if re.fullmatch(r'^\d+([.,]\d+)?$', message.text):
        current_material = data.get('temp_material')
        current_quantity = message.text.replace('.', ',')
        check_num = message.text.replace(',', '.')
        if float(check_num) <= 2000:
            data.pop('temp_material', None)  # Удаляем временный ключ
            # Теперь находим, или создаём новый, словарь материалов
            material_dict = data.get('material', {})
            material_dict[current_material] = current_quantity
            # И обновляем данные
            await state.update_data(material=material_dict)
            data = await state.get_data()
            material_text = '\n'.join(
                f"<b>{material}</b>: <b>{quantity}</b>" for material, quantity in data['material'].items())
            await message.answer(text=f"You have entered the following data for the report:\n"
                                      f"Worked hours: <b>{data['work_time']}</b>\n"
                                      f"Materials used:\n{material_text}")
            await message.answer(text=f"Do you want to add more material?",
                                 reply_markup=confirm_cancel_add_materials_kb)
        else:
            # await state.set_state(States.building_materials)
            await message.reply("Invalid input❗️\nEnter the correct number! The number should not be more than 2000!")
    else:
        # await state.set_state(States.building_materials)
        await message.reply("Invalid input❗️\nEnter the correct number!")


@router.callback_query(F.data == 'add_materials')
async def add_more_materials(callback: CallbackQuery, state: FSMContext):
    """
    Функция обрабатывающая callback добавлять материалы
    """
    await state.set_state(States.work_time)
    await callback.message.edit_reply_markup()
    await callback.answer()
    await select_building_material(callback, state)


@router.callback_query(F.data == 'not_add_materials')
async def confirm_send_report(callback: CallbackQuery, state: FSMContext):
    """
    Функция обрабатывающая callback не добавлять материалы
    """
    data = await state.get_data()
    await callback.message.edit_reply_markup()
    await callback.answer()
    material_text = '\n'.join(
        f"<b>{material}</b>: <b>{quantity}</b>" for material, quantity in data['material'].items())
    await callback.message.answer(text=f"You have entered the following data for the report:\n"
                                       f"Worked hours: <b>{data['work_time']}</b>\n"
                                       f"Materials used:\n{material_text}")
    await callback.message.answer(text='Confirm sending the report, or select edit', reply_markup=confirm_cancel_kb)


@router.callback_query(F.data == 'confirm')
async def write_data(callback: CallbackQuery, state: FSMContext):
    """
    Функция проверки выбора отправки данных
    """
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(text='Wait, data is being recorded 🚀')
    await confirm(callback.message, state)


async def confirm(message, state):
    """
    Функция вызывающая запись материалов в таблицы work_time и results
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    await state.set_state(States.add_photo)
    # await save_data_in_tables(message.from_user.id, data)
    await save_data_in_tables(message, state, data)
    current_state = await state.get_state()
    if current_state:
        await message.edit_text(text='<b>The data has been sent✅\n\nSend me some photos 🏞. (Maximum of 10)!</b>')


@router.message(F.video)
async def video(message: Message, state: FSMContext):
    """
    Функция обработки случайной отправки видео вместо фото
    """
    await message.answer('Sending videos is not supported❗️')


@router.message(F.photo and StateFilter(States.add_photo))
async def get_photo_link(message: Message, state: FSMContext, album=None):
    """
    Функция обработки альбома с фото
    Отправляет данные на запись в таблицу photos
    """
    data = await state.get_data()
    if album:
        for msg in album:
            await process_photo(msg, state)

    data = await state.get_data()
    photos = data.get('photos')

    await save_photo_url(message, state, data)
    current_state = await state.get_state()
    if current_state:
        material_text = '\n'.join(
            f"<b>{material}</b>: <b>{quantity}</b>" for material, quantity in data['material'].items())
        await message.answer(text=f"Thank you 👍! Photos uploaded. Report completed\n\nYou have sent such a report:\n"
                                  f"Worked hours: <b>{data['work_time']}</b>\n"
                                  f"Materials used:\n{material_text}\n\n"
                                  f"If you want to change the report, select the '/report' command from the menu.\n"
                                  f"After sending, the old data and photos will be replaced with new ones")
        await save_to_server_photos(data)
        await state.clear()


async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    # Обработка ошибки если файл в альбоме не фото, не позволяет зависнуть отправке
    # фото, отправятся на запись только фото файлы
    try:
        file_id = message.photo[-1].file_id
        file_info = await message.bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

        photo_list = data.get('photos', [])
        photo_list.append(file_url)
        await state.update_data(photos=photo_list)
    except:
        await message.answer('Sending videos is not supported❗️ Send the correct data')
        pass


@router.callback_query(F.data == 'edit')
async def edit_report(callback: CallbackQuery, state: FSMContext):
    """
    Хендлер обработки редактирования отчета
    """
    await callback.message.answer(text='Editing a report...\n'
                                       'Choose what you want to edit', reply_markup=edit_report_data_kb)
    await callback.message.edit_reply_markup()
    await state.set_state(States.edit_data)
    await callback.answer()


@router.callback_query(F.data == 'edit_material')
async def go_to_select_building_material(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await state.update_data(material={})
    await state.set_state(States.work_time)
    await callback.answer()
    await select_building_material(callback, state)


@router.message()
async def send_echo(message: Message):
    """
    Функция обработки всех остальных сообщений, не попавших в хендлеры
    :param message:
    :return:
    """
    await message.reply(text="Unknown command or incorrectly entered data!")
