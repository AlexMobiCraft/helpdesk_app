# Файл: app/models/__init__.py
# Делает модели доступными напрямую через пакет app.models

from .user import User
from .device_type import DeviceType
from .priority import Priority
from .status import Status
from .device import Device
from .file import File
from .technician_assignment import TechnicianAssignment
from .ticket import Ticket
from .user_role import UserRole

# Это позволяет импортировать так:
# from app import models
# user = models.User(...)
# ticket = models.Ticket(...)