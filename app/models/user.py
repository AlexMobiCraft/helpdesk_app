# Файл: app/models/user.py
import datetime
from sqlalchemy import Integer, String, DateTime, func, Index, ForeignKey # Добавляем ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship # Добавляем relationship
from app.db.base_class import Base # Импортируем наш базовый класс
from typing import List, TYPE_CHECKING # Добавляем List и TYPE_CHECKING

# Импортируем TechnicianAssignment для проверки типов в relationship
if TYPE_CHECKING:
    from .technician_assignment import TechnicianAssignment # type: ignore
    from .user_role import UserRole # Добавляем импорт UserRole

class User(Base):
    """
    Модель пользователя SQLAlchemy.
    """
    __tablename__ = "users" # Указываем имя таблицы в базе данных

    # Определяем колонки с помощью аннотаций типов и mapped_column
    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True, # <-- Добавлено для явного указания AUTO_INCREMENT
        comment="Уникальный идентификатор пользователя (Автоинкремент)"
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False, comment="Уникальный логин пользователя")
    password_hash: Mapped[str] = mapped_column(String, nullable=False, comment="Хэшированный пароль пользователя") # Тип String без длины обычно соответствует TEXT в Postgres
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True, comment="Email пользователя (необязательное поле)")
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Имя пользователя (необязательное поле)")
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Фамилия пользователя (необязательное поле)")
    phone_number: Mapped[str | None] = mapped_column(String(50), comment="Номер телефона пользователя")
    role_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("user_roles.id"), 
        nullable=False,
        index=True,
        comment="Внешний ключ, ID роли пользователя"
    )
    department: Mapped[str | None] = mapped_column(String(255), comment="Отдел пользователя")
    avatar_url: Mapped[str | None] = mapped_column(String, comment="URL аватара пользователя")

    # Автоматически устанавливаемые временные метки
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Время создания записи"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Время последнего обновления записи"
    )

    # Связь с UserRole
    role = relationship("UserRole", back_populates="users")

    # Связь "один ко многим" с TechnicianAssignment (назначения, где пользователь является техником)
    assignments: Mapped[List["TechnicianAssignment"]] = relationship(
        "TechnicianAssignment", back_populates="technician"
    )

    # Метод для удобного представления объекта User при выводе в консоль
    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', name='{self.first_name} {self.last_name}', role_id={self.role_id})>"