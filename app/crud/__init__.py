# Файл: app/crud/__init__.py
# Делает CRUD операции доступными напрямую через пакет app.crud

from . import crud_user as user
from . import crud_device_type as device_type # Добавляем импорт для типов устройств
from . import crud_priority as priority # Добавляем импорт для приоритетов
from . import crud_status as status # Добавляем импорт для статусов
from . import crud_device as device # Добавляем импорт для устройств
from . import crud_user_role as user_role # Добавляем импорт для ролей пользователей
from . import crud_ticket as ticket # Добавляем импорт для заявок
from . import crud_technician_assignment as technician_assignment # Добавляем импорт для назначения техников
from . import crud_file as file # Добавляем импорт для файлов

# Это позволяет импортировать и использовать так:
# from app import crud
# user_obj = await crud.user.get_user_by_username(...)
# dt = await crud.device_type.get_device_type(...)
# p = await crud.priority.get_priority(...)
# s = await crud.status.get_status(...)
# d = await crud.device.get_device(...)
# ur = await crud.user_role.get_user_role(...)