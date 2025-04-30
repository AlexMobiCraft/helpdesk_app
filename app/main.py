# Файл: app/main.py

# --- Остальные импорты ---
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Импортируем настройки из config.py с использованием правильного относительного импорта
from .core.config import settings
# Импортируем роутеры с использованием относительного импорта
from .api.v1.endpoints import ( 
    auth as auth_router, 
    users as users_router, 
    device_types as device_types_router, 
    priorities as priorities_router, 
    statuses as statuses_router, 
    devices as devices_router, 
    roles as roles_router, 
    tickets as tickets_router,
    admin as admin_router # Добавлен импорт admin
)

# Создаем экземпляр FastAPI
# title - будет отображаться в документации API
app = FastAPI(
    title="Helpdesk API",
    description="API для системы управления заявками Helpdesk",
    version="0.1.0", # Добавим версию
    openapi_url="/api/v1/openapi.json", # Стандартный путь для OpenAPI схемы
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Configuration using settings ---
# Список разрешенных origins берем из настроек
origins = settings.allowed_origins_list

# Добавляем Middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Разрешаем запросы от указанных origins
    allow_origin_regex=r"^https?://127\.0\.0\.1:\d+$",
    allow_credentials=True,      # Разрешаем передачу cookies/авторизации
    allow_methods=["*"],         # Разрешаем все HTTP-методы
    allow_headers=["*"],         # Разрешаем все HTTP-заголовки
)
# --- End CORS Configuration ---

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="uploads")

# Подключаем роутеры API
# Используем префикс /api/auth для всех эндпоинтов аутентификации
app.include_router(auth_router.router, prefix="/api/auth")
# Используем префикс /api/users для эндпоинтов пользователей
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"]) # Добавляем тег для группировки в Swagger
# Подключаем роутер для типов устройств
app.include_router(device_types_router.router, prefix="/api") # Префикс /api, теги определены в самом роутере
# Подключаем роутер для приоритетов
app.include_router(priorities_router.router, prefix="/api/v1/priorities", tags=["Priorities"]) # Префикс /api, теги определены в самом роутере
# Подключаем роутер для статусов
app.include_router(statuses_router.router, prefix="/api/v1/statuses", tags=["Statuses"]) # Префикс /api, теги определены в самом роутере
# Подключаем роутер для устройств
app.include_router(devices_router.router, prefix="/api/v1/devices", tags=["Devices"]) # Префикс /api, теги определены в самом роутере
# Подключаем роутер для ролей пользователей
app.include_router(roles_router.router, prefix="/api/v1/users") # Префикс /api/v1/users, теги определены в самом роутере
# Подключаем роутер для заявок
app.include_router(tickets_router.router, prefix="/api/v1/tickets", tags=["Tickets"]) # Префикс /api/tickets
# Подключаем роутер для администратора
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["Admin"]) # Подключен admin_router

# Определяем простой эндпоинт для корневого URL ("/")
@app.get("/")
async def read_root():
    """
    Корневой эндпоинт API.
    Просто возвращает приветственное сообщение.
    """
    return {"message": "Welcome to the Helpdesk API"}

# Добавим еще один тестовый эндпоинт
@app.get("/ping")
async def ping():
    """
    Простой эндпоинт для проверки доступности API.
    """
    return {"message": "pong"}

# Здесь можно добавить обработчики событий startup/shutdown, если нужно
# @app.on_event("startup")
# async def startup_event():
#     # Например, инициализация соединения с БД (если не используется Depends)
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Например, закрытие соединения с БД
#     pass