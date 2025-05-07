# Документация проекта “helpdesk_app"

---

## Содержание

1. [Введение](#1-введение)  
2. [Установка и запуск](#2-установка-и-запуск)  
3. [Структура проекта](#3-структура-проекта)  
4. [Техническое задание](#4-техническое-задание)  
5. [API Эндпоинты](#5-api-эндпоинты)  
   - [5.1 Аутентификация](#51-аутентификация)  
   - [5.2 Пользователи](#52-пользователи)  
   - [5.3 Заявки (Tickets)](#53-заявки-tickets)  
   - [5.4 Административные операции](#54-административные-операции)  
   - [5.5 Справочники](#55-справочники-device-types-priorities-statuses-roles)  
   - [5.6 Работа с файлами](#56-работа-с-файлами)  
   - [5.7 Отчёты](#57-отчёты)  
6. [HTTP Статусы ошибок](#6-http-статусы-ошибок)  
7. [Структура ошибки валидации (422)](#7-структура-ошибки-валидации-422)  
8. [Дополнительно](#8-дополнительно)  

---

## 1. Введение

Это веб‑приложение (PWA) для службы технической поддержки.  
Пользователи могут создавать заявки на ремонт/сервис, прикладывать файлы; техники — брать заявки в работу, менять статус, оставлять заметки; администратор — управлять справочниками (типы устройств, статусы заявок, приоритеты заявок, роли), пользователями, управлять статусами заявок и выгружать отчёты.

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
0. Убедитесь что установлена версия python3.10 или выше

1. Клонировать репозиторий и перейти в корень:
   ```ps1
   git clone https://github.com/AlexMobiCraft/helpdesk_app.git helpdesk_app
   cd helpdesk_app
   ```

2. Создать виртуальное окружение и установить зависимости:
   ```ps1
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Запустить БД в Docker:

Если Docker не установлен, выполните:
   ```ps1
   sudo apt update
sudo apt install docker.io
   ```
Убедитесь, что Docker установлен:
   ```ps1
   docker --version
   ```
Создайте группу docker (если не создана автоматически):
   ```ps1
sudo groupadd docker
   ```
Добавьте текущего пользователя в группу docker:
   ```ps1
   sudo usermod -aG docker $USER
   ```

   ```ps1
   docker-compose up -d db
   ```

4. Применить миграции:
   ```ps1
   source .venv/bin/activate
   alembic upgrade head
   ```

5. Запустить сервер:
   ```ps1
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 2.2. Frontend (Next.js)
0. Убедитесь что установлен Node.js и npm
Если не установлен, выполните:
   ```ps1
   sudo apt update
sudo apt install nodejs npm
   ```
Убедитесь, что Node.js и npm установлены:
   ```ps1
   node --version
   npm --version
   ```

1. Перейти в папку фронтенда:
   ```ps1
   cd frontend
   npm install
   npm run dev
   ```
2. По умолчанию доступно на `http://localhost:3000`.


## 3. Структура проекта

### 3.1 Краткая структура

```text
.
├── .env                     # Переменные окружения для backend (БД, секреты)
├── .gitignore               # Файлы и папки, игнорируемые git
├── .venv/                   # Виртуальное окружение Python (игнорируется git)
├── venv/                    # Альтернативное виртуальное окружение Python (игнорируется git)
├── .vscode/                 # Настройки VS Code (опционально)
├── .windsurfrules           # Конфиг windsurf (если используется)
├── README.md                # Основной README файл проекта
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
│   ├── app/                 # Страницы и layout Next.js (App Router)
│   │   ├── admin/                # Админ-панель
│   │   │   ├── users/
│   │   │   │   ├── page.tsx               # Список пользователей
│   │   │   │   ├── edit/[user_id]/EditUserForm.tsx  # Форма редактирования пользователя
│   │   │   │   └── new/
│   │   │   │       ├── page.tsx           # Страница создания нового пользователя
│   │   │   │       └── NewUserForm.tsx    # Компонент формы создания пользователя
│   │   │   ├── devices/
│   │   │   │   ├── page.tsx              # Список устройств
│   │   │   │   ├── DeviceList.tsx        # Компонент таблицы устройств
│   │   │   │   ├── new/
│   │   │   │   │   ├── page.tsx              # Страница создания устройства
│   │   │   │   │   └── NewDeviceForm.tsx     # Компонент формы создания устройства
│   │   │   │   └── edit/
│   │   │   │       └── [device_id]/
│   │   │   │           ├── page.tsx          # Страница редактирования устройства
│   │   │   │           └── EditDeviceForm.tsx # Компонент формы редактирования устройства
│   │   │   ├── roles/                # Управление ролями
│   │   │   │   ├── page.tsx               # Список ролей пользователей
│   │   │   │   ├── RoleList.tsx           # Компонент таблицы ролей
│   │   │   │   ├── new/
│   │   │   │   │   ├── page.tsx           # Страница создания новой роли
│   │   │   │   │   └── NewRoleForm.tsx    # Компонент формы создания роли
│   │   │   │   └── edit/
│   │   │   │       └── [role_id]/
│   │   │   │           ├── page.tsx       # Страница редактирования роли
│   │   │   │           └── EditRoleForm.tsx # Компонент формы редактирования роли
│   │   │   ├── priorities/           # Управление приоритетами
│   │   │   │   ├── page.tsx               # Список приоритетов
│   │   │   │   ├── PriorityList.tsx       # Компонент таблицы приоритетов
│   │   │   │   ├── new/
│   │   │   │   │   ├── page.tsx           # Страница создания нового приоритета
│   │   │   │   │   └── NewPriorityForm.tsx # Компонент формы создания приоритета
│   │   │   │   └── edit/
│   │   │   │       └── [priority_id]/
│   │   │   │           ├── page.tsx       # Страница редактирования приоритета
│   │   │   │           └── EditPriorityForm.tsx # Компонент формы редактирования приоритета
│   │   │   └── statuses/             # Управление статусами заявок
│   │   │       ├── page.tsx               # Список статусов
│   │   │       ├── StatusList.tsx         # Компонент таблицы статусов
│   │   │       ├── new/
│   │   │       │   ├── page.tsx           # Страница создания нового статуса
│   │   │       │   └── NewStatusForm.tsx    # Компонент формы создания статуса
│   │   │       └── edit/
│   │   │           └── [status_id]/
│   │   │               ├── page.tsx       # Страница редактирования статуса
│   │   │               └── EditStatusForm.tsx   # Компонент формы редактирования статуса
│   │   ├── login/                # Страница входа
│   │   │   └── page.tsx
│   │   ├── tickets/              # Страницы заявок
│   │   │   ├── [ticket_id]/page.tsx # Просмотр заявки
│   │   │   └── page.tsx           # Список заявок пользователя
│   │   ├── user/                 # Страницы профиля пользователя
│   │   │   └── page.tsx           # Профиль пользователя
│   │   ├── globals.css           # Глобальные стили
│   │   ├── layout.tsx            # Корневой layout
│   │   └── page.tsx              # Корневая страница (возможно, редирект или главная)
│   ├── eslint.config.mjs    # Конфиг ESLint
│   ├── i18n.ts              # Настройка i18next
│   ├── locales/             # Локализации
│   │   ├── en/
│   │   │   └── common.json  # Английский перевод
│   │   ├── ru/
│   │   │   └── common.json  # Русский перевод
│   │   └── sl/
│   │       └── common.json  # Словенский перевод
│   ├── next-env.d.ts        # TypeScript декларации для Next.js
│   ├── next.config.js       # Конфиг Next.js (JavaScript)
│   ├── next.config.ts       # Конфиг Next.js (TypeScript)
│   ├── node_modules/        # Зависимости npm (игнорируется git)
│   ├── package.json         # Зависимости и скрипты npm
│   ├── package-lock.json    # Лок-файл npm
│   ├── postcss.config.mjs   # Конфиг PostCSS
│   ├── public/              # Статические файлы (иконки, изображения)
│   ├── src/                 # Логика, api, store, хуки, темы
│   └── tsconfig.json        # Конфиг TypeScript
├── requirements.txt         # Python-зависимости
├── uploads/                 # Загружаемые пользователями файлы (игнорируется git)
└── Doc/                     # Документация проекта
    ├── API_endpoints_V1.1.md
    ├── HTTP_status_422.md
    ├── HTTP_status_code.md
    ├── Plan.md
    ├── PROJECT_STRUCTURE.md
    └── Technical_specification.md
```

### 3.2 Описание директорий и файлов

Описание директорий и файлов проекта находится в файле [Doc/PROJECT_STRUCTURE.md](/Doc/PROJECT_STRUCTURE.md).

---

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

## 5. API Эндпоинты

Детальное описание всех эндпоинтов находится в файле [Doc/API_endpoints_V1.1.md](/Doc/API_endpoints_V1.1.md).

### 5.1 Аутентификация

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

### 5.2 Пользователи

- **GET** `/api/users/me` — профиль текущего пользователя.  
- **GET** `/api/admin/users` — список всех (admin).  
- **POST** `/api/admin/users` — создание (admin).  
- **PATCH** `/api/users/me` — обновление своих данных.  
- **PATCH** `/api/users/me/password` — смена пароля.  
- **PATCH** `/api/admin/users/{user_id}/password` — сброс пароля (admin).  
- **PATCH** `/api/admin/users/{user_id}/role` — изменение роли (admin).  

### 5.3 Заявки (Tickets)

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

### 5.4 Административные операции

- **POST** `/api/admin/tickets` — создать от имени любого пользователя.  
- **GET** `/api/admin/reports/tickets` — экспорт отчёта (CSV).

### 5.5 Справочники (device-types, priorities, statuses, roles)

- **GET** `/api/device-types`  
- **POST/PATCH/DELETE** `/api/admin/device-types`  
- Аналогично для `/priorities`, `/statuses`, `/roles` (с префиксом `/api/admin` для изменений).

### 5.6 Работа с файлами

- Файлы хранятся локально (разработка) или в облаке (продакшен).  
- Эндпоинты: см. раздел 5.3.

### 5.7 Отчёты

- **GET** `/api/admin/reports/tickets` — выгрузка CSV по заявкам.

---

## 6. HTTP Статусы ошибок

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

## 7. Структура ошибки валидации (422)

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

## 8. Дополнительно

- Полная структура проекта — [Doc/PROJECT_STRUCTURE.md](/Doc/PROJECT_STRUCTURE.md).  
- Технические детали и схемы БД — [Doc/Technical_specification.md](/Doc/Technical_specification.md).  
- План работы — [Doc/Plan.md](/Doc/Plan.md).  
- Полная спецификация API — [Doc/API_endpoints_V1.1.md](/Doc/API_endpoints_V1.1.md).

---

> Все документы находятся в папке `Doc/`. Поддерживайте их в актуальном состоянии вместе с кодом.
