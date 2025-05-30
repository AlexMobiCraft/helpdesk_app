# PROJECT_STRUCTURE.md
## Актуальная структура проекта

Ниже приведена структура директорий и файлов проекта с кратким описанием назначения каждого элемента.

### Краткое описание ключевых папок и файлов:
- **app/** — Backend (FastAPI): API, модели, схемы, CRUD, настройки, миграции.
- **frontend/** — Frontend (Next.js): страницы, компоненты, локализация, store, api, статика.
- **alembic/** — Миграции БД.
- **Doc/** — Документация.
- **uploads/** — Файлы, загружаемые пользователями.
- **.env, .env.local** — переменные окружения.
- **docker-compose.yml** — запуск сервисов через Docker.
- **requirements.txt, package.json** — зависимости Python и npm.

### Примечания:
- `uploads/`, `.venv/`, `venv/`, `node_modules/`, `.next/` обычно игнорируются git.
- `frontend/app/` содержит страницы и компоненты Next.js.
- `app/` — backend FastAPI (эндпоинты, модели, схемы, CRUD, ядро).
- `Doc/` — документация проекта.
- `frontend/` — Frontend-приложение (Next.js).

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
│   │   │   │      └── [device_id]/
│   │   │   │          ├── page.tsx          # Страница редактирования устройства
│   │   │   │          └── EditDeviceForm.tsx # Компонент формы редактирования устройства
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
│   │   │   │          ├── page.tsx       # Страница редактирования приоритета
│   │   │   │          └── EditPriorityForm.tsx # Компонент формы редактирования приоритета
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

Если структура изменится, не забудьте обновить этот файл.