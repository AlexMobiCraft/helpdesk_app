# Файл: app/schemas/file.py
from pydantic import BaseModel, Field
import datetime
from typing import Optional

# Базовая схема для файла, содержащая общие поля
class FileBase(BaseModel):
    file_name: str = Field(..., max_length=255, description="Оригинальное имя файла")
    file_type: str = Field(..., max_length=100, description="MIME-тип файла")
    file_size: int = Field(..., gt=0, description="Размер файла в байтах")

# Схема для создания записи о файле в БД (не используется напрямую в API)
class FileCreate(FileBase):
    file_path: str = Field(..., description="Путь к файлу в хранилище")
    ticket_id: int = Field(..., description="ID заявки, к которой прикреплен файл")

# Схема для чтения данных о файле (возвращается из API)
class FileRead(FileBase):
    file_id: int = Field(..., description="Уникальный ID файла")
    ticket_id: int = Field(..., description="ID заявки, к которой прикреплен файл")
    uploaded_at: datetime.datetime = Field(..., description="Дата и время загрузки файла")
    file_path: str = Field(..., description="Путь к файлу в хранилище (может быть относительным или URL)")

    class Config:
        # В Pydantic v2: orm_mode теперь называется from_attributes
        from_attributes = True
