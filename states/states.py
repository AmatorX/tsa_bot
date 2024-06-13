from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    start_report = State()
    work_time = State()
    building_materials = State()
    material_used = State()
    edit_data = State()
    edit_work_time = State()
    edit_building_materials = State()
    edit_material_used = State()
    add_photo = State()
    end_add_photo = State()
    admin_choose_menu = State()
    admin_select_action_user = State()
    admin_select_crud_user = State()
    admin_select_users = State()
    admin_select_target_group = State()
    admin_move_user_to_group = State()
    admin_delete_user = State()
    admin_add_new_user = State()
    admin_select_object_materials = State()
    admin_edit_materials = State()
    admin_delete_materials = State()
    admin_add_new_material = State()


