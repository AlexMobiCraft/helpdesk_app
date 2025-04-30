# Файл: app/schemas/__init__.py
# Делает Pydantic схемы доступными напрямую через пакет app.schemas

from .token import Token, TokenData
from .user import UserBase, UserCreate, UserUpdate, UserRead
from . import device_type # Импортируем модуль схем для типов устройств
from . import priority # Импортируем модуль схем для приоритетов
from . import status # Импортируем модуль схем для статусов
from . import device # Импортируем модуль схем для устройств
from . import ticket # Импортируем модуль схем для заявок
from . import technician_assignment # Импортируем модуль схем для назначения техников
from . import file # Импортируем модуль схем для файлов

# Это позволяет импортировать так:
# from app import schemas
# token_data = schemas.TokenData(...)
# user_read = schemas.UserRead(...)
# dt_create = schemas.device_type.DeviceTypeCreate(...)
# p_read = schemas.priority.PriorityRead(...)
# s_update = schemas.status.StatusUpdate(...)
# d_read = schemas.device.DeviceRead(...)