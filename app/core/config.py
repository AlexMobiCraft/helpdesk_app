import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings # Импортируем BaseSettings из нового пакета
from pydantic import Field, field_validator # Field остается в основном пакете pydantic
from typing import List # Добавить импорт List

# Определяем путь к .env файлу относительно текущего файла config.py
# Это делает путь более надежным, независимо от того, откуда запускается приложение
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def expand_env_vars(value: str) -> str:
    """Заменяет ${VAR} или $VAR в строке на значение переменной окружения."""
    import re
    pattern = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z0-9_]+)')
    def replacer(match):
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, '')
    return pattern.sub(replacer, value)

class Settings(BaseSettings):
    """Класс для хранения настроек приложения."""
    host_ip: str = Field(default=os.getenv("HOST_IP", "127.0.0.1"))

    # Настройки CORS: загружаем строку из env, разбиваем на список
    ALLOWED_ORIGINS: str = Field(default=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))

    @property
    def allowed_origins_list(self) -> List[str]:
        # Автоматическая подстановка переменных окружения в ALLOWED_ORIGINS
        expanded = expand_env_vars(self.ALLOWED_ORIGINS)
        return [origin.strip() for origin in expanded.split(",") if origin.strip()]

    # Настройки JWT
    # Используем os.getenv для чтения из переменных окружения,
    # предоставляя значения по умолчанию для разработки.
    # В продакшене КРАЙНЕ ВАЖНО установить надежный SECRET_KEY!
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "your_very_secret_key_for_dev_only"))
    ALGORITHM: str = Field(default=os.getenv("ALGORITHM", "HS256"))
    # Время жизни токена доступа в минутах
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))

    # Настройки базы данных
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@host:port/db"))

    # Настройки загрузки файлов
    UPLOAD_DIRECTORY: str = Field(default=os.getenv("UPLOAD_DIRECTORY", "uploads"))

    class Config:
        # Указываем Pydantic искать переменные окружения без учета регистра
        case_sensitive = False
        # Указываем Pydantic Settings, что нужно загружать переменные из .env файла
        # (Это уже должно быть сделано через load_dotenv, но иногда полезно указать явно)
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()