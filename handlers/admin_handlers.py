import json
from typing import Union
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states import States

from config_data.config import Config, load_config

from keyboards.admin_keyboards.crud_user import select_crud_user_kb
from keyboards.admin_keyboards.select_build_object import select_binding_object_kb
from keyboards.admin_keyboards.edit_objects_list import select_to_edit
from keyboards.admin_keyboards.admin_choose_menu import menu_selection_kb
from keyboards.admin_keyboards.crud_materials import select_action_material_kb

config: Config = load_config('.env')
admins = config.tg_bot.admin_ids


# Инициализируем роутер уровня модуля
router: Router = Router()
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()


@router.message(Command(commands=['admin']))
async def start_admin_menu(message: Union[Message, CallbackQuery], state: FSMContext):
    """
    Хендлер обработки команды admin, отвечает инлайн клавиатурой выбора меню:
    Список пользователй, список материалов по объектам
    работа с пользователями, работа с материалами, отмена
    """
    if message.from_user.id in admins:
        await message.answer(text='Welcome. You are logged in as an administrator. Select the desired menu',
                             reply_markup=menu_selection_kb)
        await state.set_state(States.admin_choose_menu)
    else:
        await message.answer(text='You are not an administrator. The menu is not available')


@router.callback_query(F.data == "admin_exit_admin_mode")
async def exit_menu(callback: CallbackQuery, state: FSMContext):
    """
    Выход из меню админа
    """
    await state.clear()
    await callback.message.edit_reply_markup()
    await callback.message.edit_text('You have exited the admin menu')


@router.callback_query(F.data == "cancel")
async def exit_menu(callback: CallbackQuery, state: FSMContext):
    """
    Отмена действия из любого меню, вызывает клавиатуру выбора действий admin
    """
    await state.clear()
    await callback.message.edit_reply_markup()
    await callback.message.answer(text='Select the desired menu', reply_markup=menu_selection_kb)


@router.callback_query(F.data == "admin_users_list")
async def users_list(callback: CallbackQuery, state: FSMContext):
    """
    Показывает полный список пользователй, обрабатывает callback клавиатуры выбора действия admin
    """
    await callback.answer()
    with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        response = ""
        for obj, info in data.items():
            response += f"<u>Object [{obj}]</u> :\n\t\t\t<u>Employees:</u>\n\t\t\t\t\t\t"
            users = '\n\t\t\t\t\t\t'.join(info['users'].values())
            response += users + "\n\n"
        await callback.message.answer(text=response)
        await callback.message.answer(text='Select the desired menu', reply_markup=menu_selection_kb)
        await callback.message.edit_reply_markup()
        await state.clear()


@router.callback_query(F.data == 'admin_materials_list')
async def materials_list(callback: CallbackQuery, state: FSMContext):
    """
    Показывает полный список материалов по объектам, обрабатывает callback клавиатуры выбора действия admin
    """
    await callback.answer()
    with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    response = ""
    for obj, info in data.items():
        response += f"<u>Object [{obj}]</u> :\n\t\t\t<u>Materials:</u>\n\t\t\t\t\t\t"
        materials = '\n\t\t\t\t\t\t'.join(info['materials'])
        response += materials + "\n\n"
    await callback.message.answer(text=response)
    await callback.message.answer(text='Select the desired menu', reply_markup=menu_selection_kb)
    await callback.message.edit_reply_markup()
    await state.clear()


@router.callback_query(StateFilter(States.admin_choose_menu) and F.data == 'admin_users_menu')
async def select_users_action(callback: CallbackQuery, state: FSMContext):
    """
    Функция Меню работы с пользователями, обрабатывает callback клавиатуры выбора действия admin
    Предлагает выбор действия над пользователем
    """
    await callback.answer()
    await callback.message.edit_reply_markup()
    await callback.message.answer(text='Select the action to be performed on the user',
                                  reply_markup=select_crud_user_kb)
    await state.set_state(States.admin_select_action_user)


@router.callback_query(StateFilter(States.admin_select_action_user))
async def admin_users_menu(callback: CallbackQuery, state: FSMContext):
    """
    Меню работы с пользователями, обрабатывает callback клавиатуры выбора действия над пользователем
    предлагает выбрать объект на котором работает сотрудник
    """
    await callback.answer()
    await state.update_data(action=callback.data)
    if callback.data == 'move_user' or callback.data == 'delete_user':
        await callback.message.answer(text='Select the object on which the user is working',
                                      reply_markup=select_binding_object_kb)
    elif callback.data == 'create_user':
        await callback.message.answer(text='Select the object where to add a new user',
                                      reply_markup=select_binding_object_kb)
    await state.set_state(States.admin_select_crud_user)

    await callback.message.edit_reply_markup()


@router.callback_query(StateFilter(States.admin_select_crud_user))
async def crud(callback: CallbackQuery, state: FSMContext):
    """
    Функция записывает объект на котром работает сотрудник
    Выводит список пользователей для выбора
    Если выбрано действие создать пользователя, запрашивает данные для записи
    """
    await callback.message.edit_reply_markup()
    await state.update_data(current_group=callback.data)
    data = await state.get_data()
    action = data.get('action')
    if action != 'create_user':
        with open("./admin_config/main.json", "r", encoding="utf-8") as file:
            callback_data = await state.get_data()
            current_group = callback_data.get('current_group')
            data = json.load(file)
            group: dict = data.get(current_group)
            users_dict = group.get("users")
            await state.set_state(States.admin_select_target_group)
            await callback.message.answer(text='Select the user to edit', reply_markup=select_to_edit(users_dict))
    else:
        await callback.message.answer(text='Enter the telegram id and username. '
                                           'The data must be separated by a comma.\n'
                                           ' Example: 123456, New User')
        await state.set_state(States.admin_add_new_user)


@router.message(StateFilter(States.admin_add_new_user))
async def add_new_user(message: Message, state: FSMContext):
    """
    Функция записи нового пользователя
    """
    data = await state.get_data()
    current_group = data.get('current_group')
    parts = message.text.split(",")  # разделяем строку по запятой
    user_id = parts[0].strip()  # удаляем лишние пробелы
    user_name = parts[1].strip()
    with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
        groups = json.load(file)

    # Добавление пользователя в целевую группу
    groups[current_group]['users'][user_id] = user_name

    # Сохранение обновленных данных обратно в JSON-файл
    with open('./admin_config/main.json', 'w') as file:
        json.dump(groups, file, ensure_ascii=False, indent=4)
    await message.answer(text=f'User "{user_name}" has been added to the <u>{current_group}</u> group')
    await message.answer(text=f'Select an action:',
                         reply_markup=menu_selection_kb)
    await state.clear()


@router.callback_query(StateFilter(States.admin_select_target_group))
async def select_target_group(callback: CallbackQuery, state: FSMContext):
    """
    Удаление сотрудника если было выбрано action удаление
    Или выбора группы куда переместить если было выбрано перемещение
    """
    user_id, user_name = callback.data.split(',')
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.update_data(user_id=user_id, user_name=user_name)
    data = await state.get_data()
    action = data.get("action")

    if action == "move_user":
        await state.set_state(States.admin_move_user_to_group)
        await callback.message.answer(text='Select which group to move the employee to',
                                      reply_markup=select_binding_object_kb)
    elif action == 'delete_user':
        data = await state.get_data()
        current_group = data.get('current_group')
        user_id = data.get('user_id')
        with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
            groups = json.load(file)

        # Удаление пользователя из текущей группы
        if user_id in groups[current_group]['users']:
            del groups[current_group]['users'][user_id]

        # Сохранение обновленных данных обратно в JSON-файл
        with open('./admin_config/main.json', 'w') as file:
            json.dump(groups, file, ensure_ascii=False, indent=4)
        data = await state.get_data()
        user = data.get("user_name")
        await callback.message.answer(text=f'User "{user}" has been deleted')
        await callback.message.answer(f'Select an action:',
                                      reply_markup=menu_selection_kb)
        await state.clear()


@router.callback_query(StateFilter(States.admin_move_user_to_group))
async def move_user_to_target_group(callback: CallbackQuery, state: FSMContext):
    """
    Функция перемещает выбранного сотрудника в целевую группу
    """
    await state.update_data(target_group=callback.data)
    data = await state.get_data()
    current_group = data.get('current_group')
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    target_group = data.get('target_group')
    # Загрузка данных из JSON-файла
    with open('./admin_config/main.json', 'r', encoding='utf-8') as file:
        groups = json.load(file)

    # Удаление пользователя из текущей группы
    if user_id in groups[current_group]['users']:
        del groups[current_group]['users'][user_id]

    # Добавление пользователя в целевую группу
    groups[target_group]['users'][user_id] = user_name

    # Сохранение обновленных данных обратно в JSON-файл
    with open('./admin_config/main.json', 'w') as file:
        json.dump(groups, file, ensure_ascii=False, indent=4)
    await callback.message.edit_reply_markup()
    await callback.message.edit_text(f'"{user_name}" was moved from "<u>{current_group}</u>" to "<u>{target_group}</u>"')
    await callback.message.answer(f'Select an action:',
                                  reply_markup=menu_selection_kb)
    await state.clear()


@router.callback_query(StateFilter(States.admin_choose_menu) and F.data == 'admin_building_material_menu')
async def select_users_action(callback: CallbackQuery, state: FSMContext):
    """
    Функция Меню работы с пользователями, обрабатывает callback клавиатуры выбора действия admin
    Предлагает выбор действия над материалами
    """
    await callback.answer()
    await callback.message.edit_reply_markup()
    await callback.message.answer(text='Select the desired action',
                                  reply_markup=select_action_material_kb)
    await state.set_state(States.admin_select_object_materials)
# Следующий хендлер предлагает выбрать объект


@router.callback_query(StateFilter(States.admin_select_object_materials))
async def select_group_materials(callback: CallbackQuery, state: FSMContext):
    """
    Функция сохраняет необходимое действие над материалом.
    Предлагает выбрать объект материала
    """
    await state.update_data(material_action=callback.data)
    await callback.answer()
    await callback.message.edit_reply_markup()
    await state.set_state(States.admin_edit_materials)
    await callback.message.answer(text='Select the object for which you want to edit the material',
                                  reply_markup=select_binding_object_kb)


@router.callback_query(StateFilter(States.admin_edit_materials))
async def update_material(callback: CallbackQuery, state: FSMContext):
    """
    Функция вызова удаления или добавления нового материала

    """
    await callback.answer()
    await state.update_data(object=callback.data)
    data = await state.get_data()
    await callback.message.edit_reply_markup()
    action = data.get('material_action')
    build_object = data.get('object')
    if action == 'delete_material':
        with open("./admin_config/main.json", "r", encoding="utf-8") as file:
            file_data = json.load(file)
            build_obj: dict = file_data.get(build_object)
            materials: list = build_obj.get("materials")
            await state.set_state(States.admin_edit_materials)
            await callback.message.answer(text='Select the material to edit', reply_markup=select_to_edit(materials))
            await state.set_state(States.admin_delete_materials)
    else:
        await callback.message.answer(text='Enter the name of the material you want to add')
        await state.set_state(States.admin_add_new_material)


@router.callback_query(StateFilter(States.admin_delete_materials))
async def delete_material(callback: CallbackQuery, state: FSMContext):
    """
    Удаление материала
    """
    await callback.answer()
    data = await state.get_data()
    material = callback.data
    build = data.get("object")
    with open("./admin_config/main.json", "r", encoding="utf-8") as file:
        file_data = json.load(file)
        file_data[build]["materials"].remove(material)

        # Сохранение обновленных данных обратно в JSON-файл
    with open('./admin_config/main.json', 'w') as file:
        json.dump(file_data, file, ensure_ascii=False, indent=4)
    await callback.message.edit_reply_markup()
    await callback.message.answer(f'Material {material} removed', reply_markup=menu_selection_kb)
    await state.clear()


@router.message(StateFilter(States.admin_add_new_material))
async def add_material(message: Message, state: FSMContext):
    """
    Добавление материала
    """
    data = await state.get_data()
    material = message.text
    build = data.get("object")
    with open("./admin_config/main.json", "r", encoding="utf-8") as file:
        file_data = json.load(file)
        file_data[build]["materials"].append(material)

    with open('./admin_config/main.json', 'w') as file:
        json.dump(file_data, file, ensure_ascii=False, indent=4)

    await message.answer(text=f'{material} material added for the <u>{build}</u> object',
                         reply_markup=menu_selection_kb)
    await state.clear()



