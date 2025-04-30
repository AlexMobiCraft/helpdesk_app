# Файл: app/db/base.py
# Этот файл нужен, чтобы импортировать все модели SQLAlchemy.
# Когда Alembic будет импортировать Base из base_class, он также сможет
# через этот файл "увидеть" все модели, которые от Base наследуются.

from app.db.base_class import Base
from app.models.user import User
from app.models.device_type import DeviceType
from app.models.priority import Priority
from app.models.status import Status
from app.models.device import Device
from app.models.file import File
from app.models.technician_assignment import TechnicianAssignment
from app.models.ticket import Ticket
# Когда появятся другие модели, добавляй их импорты сюда:
# 
# 
# 
# 
# 
# 