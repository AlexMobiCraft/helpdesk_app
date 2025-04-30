# Документация проекта “helpdesk_app"

---

## Содержание

1. [Введение](#1-введение)  
2. [Установка и запуск](#2-установка-и-запуск)  
3. [Структура проекта](#3-структура-проекта)  
4. [Техническое задание](#4-техническое-задание)  
5. [План разработки](#5-план-разработки)  
6. [API Эндпоинты](#6-api-эндпоинты)  
   - [6.1 Аутентификация](#61-аутентификация)  
   - [6.2 Пользователи](#62-пользователи)  
   - [6.3 Заявки (Tickets)](#63-заявки-tickets)  
   - [6.4 Административные операции](#64-административные-операции)  
   - [6.5 Справочники](#65-справочники-device-types-priorities-statuses-roles)  
   - [6.6 Работа с файлами](#66-работа-с-файлами)  
   - [6.7 Отчёты](#67-отчёты)  
7. [HTTP Статусы ошибок](#7-http-статусы-ошибок)  
8. [Структура ошибки валидации (422)](#8-структура-ошибки-валидации-422)  
9. [Дополнительно](#9-дополнительно)  

---

## 1. Введение

Это веб‑приложение (PWA) для службы технической поддержки.  
Пользователи могут создавать заявки на ремонт/сервис, прикладывать файлы; техники — брать заявки в работу, менять статус, оставлять заметки; администратор — управлять справочниками, пользователями и выгружать отчёты.

---

## 2. Установка и запуск

### 2.0. Быстрая смена IP (Frontend/Backend)

**Если IP-адрес Windows-компьютера изменился:**

#### Фронтенд (Next.js):
1. Откройте файл `frontend/.env.local` и пропишите актуальный IP:
   ```
   HOST_IP=ВАШ_АКТУАЛЬНЫЙ_IP
   NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
   ```
2. Вся конфигурация фронтенда (`frontend/next.config.js` и `frontend/src/api/axios.ts`) автоматически подхватит новый IP из переменной окружения `HOST_IP`.
3. Перезапустите сервер фронтенда:
   ```sh
   npx next dev --hostname 0.0.0.0 --port 3000
   ```

#### Бэкенд (FastAPI):
1. Откройте файл `.env` в корне проекта и пропишите:
   ```
   HOST_IP=ВАШ_АКТУАЛЬНЫЙ_IP
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://${HOST_IP}:3000
   ```
2. Благодаря настройкам в `app/core/config.py` и `main.py`, список разрешённых источников CORS будет автоматически обновлён.
3. Перезапустите сервер backend (FastAPI).

**Важно:**
- Для работы шаблона `${HOST_IP}` в ALLOWED_ORIGINS используйте python-dotenv-expand или реализуйте замену переменных в config.py.
- После смены IP достаточно изменить его в одном месте (`.env` для backend и `.env.local` для frontend) и перезапустить сервисы.

---

### 2.1. Backend (FastAPI + PostgreSQL)

1. Клонировать репозиторий и перейти в корень:
   ```ps1
   git clone <repo_url> helpdesk_app
   cd helpdesk_app
   ```

2. Создать виртуальное окружение и установить зависимости:
   ```ps1
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Запустить БД в Docker:
   ```ps1
   docker-compose up -d db
   ```

4. Применить миграции:
   ```ps1
   alembic upgrade head
   ```

5. Запустить сервер:
   ```ps1
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 2.2. Frontend (Next.js)

1. Перейти в папку фронтенда:
   ```ps1
   cd frontend
   npm install
   npm run dev
   ```
2. По умолчанию доступно на `http://localhost:3000`.


## 3. Структура проекта
```
helpdesk_app/
├── .env                     # Переменные окружения для backend (БД, секреты)
├── .gitignore               # Файлы и папки, игнорируемые git
├── .venv/                   # Виртуальное окружение Python (игнорируется git)
├── venv/                    # Альтернативное виртуальное окружение Python (игнорируется git)
├── .vscode/                 # Настройки VS Code (опционально)
├── .windsurfrules           # Конфиг windsurf (если используется)
├── alembic.ini              # Конфиг Alembic
├── alembic/                 # Миграции БД Alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/            # Версии миграций
├── app/                     # Backend-приложение (FastAPI)
│   ├── .env                 # (опционально) локальные переменные окружения backend
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/   # Эндпоинты API:
│   │           ├── admin.py            # Эндпоинты для администрирования
│   │           ├── auth.py             # Аутентификация и авторизация
│   │           ├── device_types.py     # Типы устройств
│   │           ├── devices.py          # Устройства
│   │           ├── priorities.py       # Приоритеты заявок
│   │           ├── roles.py            # Роли пользователей
│   │           ├── statuses.py         # Статусы заявок
│   │           ├── tickets.py          # Работа с заявками
│   │           └── users.py            # Пользователи
│   ├── core/                # Конфиги, зависимости, безопасность
│   ├── crud/                # CRUD-операции для моделей
│   ├── db/                  # Работа с БД
│   ├── models/              # SQLAlchemy-модели
│   ├── schemas/             # Pydantic-схемы
│   └── main.py              # Точка входа FastAPI
├── docker-compose.yml       # Docker Compose для запуска сервисов
├── frontend/                # Frontend-приложение (Next.js)
│   ├── .env.local           # Переменные окружения для frontend
│   ├── .gitignore
│   ├── .next/               # Сборка Next.js (игнорируется git)
│   ├── .prettierignore
│   ├── .prettierrc
│   ├── README.md
│   ├── app/                 # Страницы и layout Next.js (admin, tickets, user и др.)
│   │   ├── admin/               # Админ-панель
│   │   │   └── devices/
│   │   │       ├── page.tsx                 # Список устройств
│   │   │       ├── DeviceList.tsx           # Компонент таблицы устройств
│   │   │       ├── new/
│   │   │       │   ├── page.tsx             # Страница создания устройства
│   │   │       │   └── NewDeviceForm.tsx    # Компонент формы создания устройства
│   │   │       └── edit/
│   │   │           └── [device_id]/
│   │   │               ├── page.tsx         # Страница редактирования устройства
│   │   │               └── EditDeviceForm.tsx # Компонент формы редактирования устройства
│   │   └── users/
│   │       ├── page.tsx                 # Список пользователей
│   │       ├── edit/[user_id]/EditUserForm.tsx  # Форма редактирования пользователя
│   │       └── new/
│   │           ├── page.tsx             # Страница создания нового пользователя
│   │           └── NewUserForm.tsx      # Компонент формы создания пользователя
│   ├── locales/             # Локализации
│   │   ├── en/
│   │   │   └── common.json  # Английский перевод
│   │   ├── ru/
│   │   │   └── common.json  # Русский перевод
│   │   └── sl/
│   │       └── common.json  # Словенский перевод
│   ├── public/              # Статические файлы (иконки, изображения)
│   ├── src/                 # Логика, api, store, хуки, темы
│   ├── node_modules/        # Зависимости npm (игнорируется git)
│   ├── package.json         # Зависимости и скрипты npm
│   ├── package-lock.json    # Лок-файл npm
│   ├── tsconfig.json        # Конфиг TypeScript
│   ├── next.config.js/ts    # Конфиг Next.js
│   ├── postcss.config.mjs   # Конфиг PostCSS
├── requirements.txt         # Python-зависимости
├── uploads/                 # Загружаемые пользователями файлы (игнорируется git)
└── Doc/                     # Документация проекта
    ├── API_endpoints_V1.1.md
    ├── HTTP_status_code.md
    ├── HTTP_status_422.md
    ├── PROJECT_STRUCTURE.md
    ├── Plan.md
    └── Technical_specification.md
```


## 4. Техническое задание

### 4.1. Роли пользователей

- **user** – создаёт заявки, прикладывает файлы, отслеживает статус.  
- **technician** – берёт заявки в работу, меняет статус, оставляет примечания, редактирует закрытые заявки.  
- **admin** – управляет пользователями, техникой, справочниками, выгружает отчёты.  

### 4.2. Основные таблицы БД

| Таблица                  | Описание                                             |
|--------------------------|------------------------------------------------------|
| `users`                  | Пользователи                                         |
| `user_roles`             | Роли пользователей (`user`, `admin`, `technician`)   |
| `tickets`                | Заявки                                               |
| `devices`                | Устройства                                           |
| `device_types`           | Типы устройств                                       |
| `priorities`             | Приоритеты заявок                                    |
| `statuses`               | Статусы заявок                                       |  
| `files`                  | Файлы, прикреплённые к заявкам                       |
| `technician_assignments` | Назначения техников на заявку                        |

_Подробные схемы и поля см. в [Doc/Technical_specification.md](/Doc/Technical_specification.md)._  

---

## 5. План разработки

1. **Backend (FastAPI)**  
   - Настройка окружения и БД (PostgreSQL + Alembic).  
   - Модели, миграции, начальные справочники и админ.  
   - JWT‑аутентификация, CRUD для справочников, пользователей, устройств.  
   - Логика заявок: создание, просмотр, обновление, статусы, файлы, назначение техников, отчёты.

2. **Frontend (Next.js)**  
   - Инициализация, PWA, линтеры.  
   - Аутентификация и защищённые маршруты.  
   - Страницы: вход, список/детали заявок, админ‑панель.  
   - Формы для создания/редактирования, загрузки файлов, назначения.

3. **Тестирование и деплой**  
   - Unit, интеграционные, E2E‑тесты.  
   - Dockerfile, CI/CD, PWA‑настройки.

---

## 6. API Эндпоинты

Все пути начинаются с префикса `/api`. Полная спецификация — в [Doc/API_endpoints_V1.1.md](/Doc/API_endpoints_V1.1.md).

### 6.1 Аутентификация

- **POST** `/api/auth/login`  
  Получение JWT (OAuth2PasswordRequestForm).  
  ```json
  {
    "access_token": "...",
    "token_type": "bearer"
  }
  ```
- **GET** `/api/users/me`  
  Информация по текущему JWT.

### 6.2 Пользователи

- **GET** `/api/users/me` — профиль текущего пользователя.  
- **GET** `/api/admin/users` — список всех (admin).  
- **POST** `/api/admin/users` — создание (admin).  
- **PATCH** `/api/users/me` — обновление своих данных.  
- **PATCH** `/api/users/me/password` — смена пароля.  
- **PATCH** `/api/admin/users/{user_id}/password` — сброс пароля (admin).  
- **PATCH** `/api/admin/users/{user_id}/role` — изменение роли (admin).  

### 6.3 Заявки (Tickets)

- **POST** `/api/tickets` — создать заявку.  
- **GET** `/api/tickets` — список (фильтры, пагинация).  
- **GET** `/api/tickets/{id}` — детали.  
- **PATCH** `/api/tickets/{id}` — обновить поля (описание, приоритет).  
- **PATCH** `/api/tickets/{id}/status` — сменить статус.  
- **POST** `/api/tickets/{id}/assign` — назначить техника.  
- **DELETE** `/api/tickets/{id}/unassign/{tech_id}` — снять техника.  
- **POST** `/api/tickets/{id}/files` — загрузить файл.  
- **DELETE** `/api/tickets/{id}/files/{file_id}` — удалить файл.  
- **DELETE** `/api/tickets/{id}` — удалить заявку (admin).  

### 6.4 Административные операции

- **POST** `/api/admin/tickets` — создать от имени любого пользователя.  
- **GET** `/api/admin/reports/tickets` — экспорт отчёта (CSV).

### 6.5 Справочники (device-types, priorities, statuses, roles)

- **GET** `/api/device-types`  
- **POST/PATCH/DELETE** `/api/admin/device-types`  
- Аналогично для `/priorities`, `/statuses`, `/roles` (с префиксом `/api/admin` для изменений).

### 6.6 Работа с файлами

- Файлы хранятся локально (разработка) или в облаке (продакшен).  
- Эндпоинты: см. раздел 6.3.

### 6.7 Отчёты

- **GET** `/api/admin/reports/tickets` — выгрузка CSV по заявкам.

---

## 7. HTTP Статусы ошибок

_См. [Doc/HTTP_status_code.md](/Doc/HTTP_status_code.md)._  

- **400 Bad Request**  
- **401 Unauthorized**  
- **403 Forbidden**  
- **404 Not Found**  
- **409 Conflict**  
- **422 Unprocessable Entity**  
- **500 Internal Server Error**  
- **503 Service Unavailable**

---

## 8. Структура ошибки валидации (422)

```json
{
  "detail": [
    {
      "loc": ["body","field_name"],
      "msg": "Сообщение об ошибке",
      "type": "validation_error_type"
    }
  ]
}
```

---

## 9. Дополнительно

- Полная структура проекта — [Doc/PROJECT_STRUCTURE.md](/Doc/PROJECT_STRUCTURE.md).  
- Технические детали и схемы БД — [Doc/Technical_specification.md](/Doc/Technical_specification.md).  
- План работы — [Doc/Plan.md](/Doc/Plan.md).  
- Полная спецификация API — [Doc/API_endpoints_V1.1.md](/Doc/API_endpoints_V1.1.md).

---

> Все документы находятся в папке `Doc/`. Поддерживайте их в актуальном состоянии вместе с кодом.
