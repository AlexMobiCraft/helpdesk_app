#!/bin/bash

# Скрипт для обновления проекта с GitHub и его полного перезапуска.
# Предполагается, что этот скрипт находится в корневой директории проекта.

# Останавливать выполнение скрипта при любой ошибке
set -e

# --- Конфигурация ---
GIT_BRANCH_TO_UPDATE="main" # Измените на 'master' или вашу основную ветку, если нужно

# --- Определение директории скрипта и переход --- 
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR" || { echo "Ошибка: не удалось перейти в директорию скрипта $SCRIPT_DIR"; exit 1; }

PROJECT_ROOT_DIR=$(pwd)

echo "== Запуск скрипта обновления и перезапуска для проекта: $PROJECT_ROOT_DIR =="

# --- 1. Остановка существующих сервисов --- 
echo "
[1/8] Остановка существующих сервисов..."
# Используем pkill для более надежной остановки. 
# Игнорируем ошибки, если процессы не найдены (они могут быть уже остановлены).
# Бэкенд (Uvicorn/FastAPI)
sudo pkill -f "uvicorn app.main:app" || echo "Процесс Uvicorn не найден или уже остановлен."
# Фронтенд (Next.js dev server)
sudo pkill -f "next dev" || echo "Процесс Next.js (dev) не найден или уже остановлен."
sleep 2 # Даем время процессам завершиться
echo "Сервисы (uvicorn, next dev) должны быть остановлены."

# --- 2. Обновление из Git --- 
echo "
[2/8] Обновление проекта из Git-репозитория (ветка: $GIT_BRANCH_TO_UPDATE)..."

echo "  Сохранение локальных изменений (git stash)..."
# Проверяем, есть ли что сташить, чтобы избежать ошибки, если сташ пуст
if ! git diff-index --quiet HEAD --; then
    git stash push -u -m "Auto-stash before update by update.sh" # Сообщение изменено на update.sh
    STASH_APPLIED=true
else
    echo "  Нет локальных изменений для сохранения."
    STASH_APPLIED=false
fi

echo "  Переключение на ветку '$GIT_BRANCH_TO_UPDATE'..."
git checkout "$GIT_BRANCH_TO_UPDATE"

echo "  Получение последних изменений (git pull https://github.com/AlexMobiCraft/helpdesk_app.git $GIT_BRANCH_TO_UPDATE)..."
git pull https://github.com/AlexMobiCraft/helpdesk_app.git "$GIT_BRANCH_TO_UPDATE"

if [ "$STASH_APPLIED" = true ] ; then
    echo "  Попытка применить ранее сохраненные изменения (git stash pop)..."
    # Пытаемся применить сташ. Если будут конфликты, скрипт остановится из-за 'set -e'.
    # В этом случае конфликты нужно будет разрешить вручную.
    if git stash pop; then
        echo "  Локальные изменения успешно применены."
    else
        echo "ПРЕДУПРЕЖДЕНИЕ: Не удалось автоматически применить сохраненные изменения (git stash pop)."
        echo "Возможно, есть конфликты. Пожалуйста, разрешите их вручную."
        echo "Вы можете найти сохраненные изменения с помощью 'git stash list'."
        # exit 1 # Раскомментируйте, если хотите прерывать скрипт при конфликте сташа
    fi
fi
echo "Проект успешно обновлен из Git."

# --- 3. Обновление Python зависимостей --- 
echo "
[3/8] Обновление Python зависимостей..."
if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install -r requirements.txt
    deactivate
    echo "Python зависимости обновлены."
else
    echo "ПРЕДУПРЕЖДЕНИЕ: Виртуальное окружение .venv не найдено. Пропуск обновления Python зависимостей."
fi

# --- 4. Запуск Docker-контейнера БД (если не запущен) --- 
echo "
[4/8] Проверка и запуск контейнера БД (PostgreSQL через Docker Compose)..."

# Проверяем, существует ли docker-compose.yml или docker-compose.yaml
COMPOSE_FILE=""
if [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
elif [ -f "docker-compose.yaml" ]; then
    COMPOSE_FILE="docker-compose.yaml"
fi

if [ -z "$COMPOSE_FILE" ]; then
    echo "ПРЕДУПРЕЖДЕНИЕ: Файл docker-compose.yml или docker-compose.yaml не найден. Пропуск запуска БД через Docker Compose."
    DB_STARTED_BY_SCRIPT=false
else
    # Проверяем, запущен ли сервис 'db' и находится ли он в состоянии 'running'
    DB_CONTAINER_ID=$(docker-compose -f "$COMPOSE_FILE" ps -q db 2>/dev/null)
    DB_IS_RUNNING=false
    if [ -n "$DB_CONTAINER_ID" ]; then
        if docker ps -q --filter "id=$DB_CONTAINER_ID" --filter "status=running" | grep -q .; then
            DB_IS_RUNNING=true
        fi
    fi

    if [ "$DB_IS_RUNNING" = true ]; then
        echo "  Контейнер БД 'db' уже запущен."
        DB_STARTED_BY_SCRIPT=false
    else
        echo "  Контейнер БД 'db' не запущен или не в состоянии 'running'. Запускаем через 'docker-compose -f $COMPOSE_FILE up -d db'..."
        if docker-compose -f "$COMPOSE_FILE" up -d db; then
            echo "  Контейнер БД 'db' успешно запущен."
            echo "  Ожидание несколько секунд для инициализации PostgreSQL..."
            sleep 15 # Увеличил немного время ожидания для Docker
            DB_STARTED_BY_SCRIPT=true
        else
            echo "ОШИБКА: Не удалось запустить контейнер БД 'db' с помощью docker-compose."
            echo "Пожалуйста, проверьте конфигурацию $COMPOSE_FILE и логи Docker."
            DB_STARTED_BY_SCRIPT=false
            # exit 1 # Раскомментируйте, если хотите прерывать скрипт здесь
        fi
    fi
fi

# --- 5. Применение миграций базы данных --- 
echo "
[5/8] Применение миграций базы данных Alembic..."
if [ -f ".venv/bin/activate" ] && [ -f "alembic.ini" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
    alembic upgrade head
    deactivate
    echo "Миграции базы данных применены."
else
    echo "ПРЕДУПРЕЖДЕНИЕ: .venv или alembic.ini не найдены. Пропуск применения миграций."
fi

# --- 6. Обновление Node.js зависимостей (Frontend) --- 
FRONTEND_DIR="$PROJECT_ROOT_DIR/frontend"
echo "
[6/8] Обновление Node.js зависимостей в $FRONTEND_DIR..."
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_ROOT_DIR"
    echo "Node.js зависимости обновлены."
else
    echo "ПРЕДУПРЕЖДЕНИЕ: Директория frontend или package.json не найдены. Пропуск обновления Node.js зависимостей."
fi

# --- 7. Сборка фронтенда (если используется в продакшене) --- 
# Раскомментируйте этот блок, если у вас есть шаг сборки для продакшена
# echo "
# [7/8] Сборка фронтенда для продакшена..."
# if [ -d "$FRONTEND_DIR" ]; then
#    cd "$FRONTEND_DIR"
#    npm run build # Или ваша команда для сборки
#    cd "$PROJECT_ROOT_DIR"
#    echo "Фронтенд собран."
# else
#    echo "ПРЕДУПРЕЖДЕНИЕ: Директория frontend не найдена. Пропуск сборки фронтенда."
# fi
# Если вы раскомментировали этот шаг, то следующий шаг будет [8/9]

# --- 8. Запуск приложения --- 
echo "
[8/8] Запуск приложения с помощью ./start.sh..."
if [ -f "./start.sh" ]; then
    chmod +x ./start.sh
    ./start.sh
    echo "Скрипт start.sh запущен."
else
    echo "ОШИБКА: Скрипт ./start.sh не найден! Невозможно запустить приложение."
    exit 1
fi

echo "
== Скрипт обновления и перезапуска завершен! =="
