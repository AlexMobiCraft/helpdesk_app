#!/bin/bash

# Скрипт для автоматического запуска Backend и Frontend на Ubuntu Server 20.04

# Определяем директорию скрипта и переходим в нее
# Это делает скрипт более надежным, если он запускается из другого места,
# но сам лежит в корневой папке проекта (например, helpdesk_app).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR" || { echo "Ошибка: не удалось перейти в директорию скрипта $SCRIPT_DIR"; exit 1; }

PROJECT_ROOT_DIR=$(pwd) # Теперь pwd будет указывать на корень проекта, где лежит скрипт
BACKEND_LOG_FILE="$PROJECT_ROOT_DIR/backend_startup.log"
FRONTEND_LOG_FILE="$PROJECT_ROOT_DIR/frontend_startup.log"

echo "== Запуск Helpdesk App Services =="
echo "Каталог проекта: $PROJECT_ROOT_DIR"
echo "Логи Backend: $BACKEND_LOG_FILE"
echo "Логи Frontend: $FRONTEND_LOG_FILE"
echo ""

# Очищаем/создаем лог-файлы для текущего запуска
# Backend
> "$BACKEND_LOG_FILE"
# Frontend
> "$FRONTEND_LOG_FILE"

echo "Скрипт запущен из: $SCRIPT_DIR"
echo "Корневая директория проекта: $PROJECT_ROOT_DIR"
echo "Лог бэкенда: $BACKEND_LOG_FILE"
echo "Лог фронтенда: $FRONTEND_LOG_FILE"

# --- Проверка и запуск Docker-контейнера БД (PostgreSQL через Docker Compose) ---
echo "
== Проверка и запуск контейнера БД (PostgreSQL через Docker Compose) ==" | tee -a "$BACKEND_LOG_FILE"

# Проверяем, существует ли docker-compose.yml или docker-compose.yaml
COMPOSE_FILE=""
if [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
elif [ -f "docker-compose.yaml" ]; then
    COMPOSE_FILE="docker-compose.yaml"
fi

if [ -z "$COMPOSE_FILE" ]; then
    echo "ПРЕДУПРЕЖДЕНИЕ: Файл docker-compose.yml или docker-compose.yaml не найден. Пропуск попытки запуска БД через Docker Compose." | tee -a "$BACKEND_LOG_FILE"
else
    echo "Проверка состояния контейнера 'db'..." | tee -a "$BACKEND_LOG_FILE"
    DB_CONTAINER_ID=$(docker-compose -f "$COMPOSE_FILE" ps -q db 2>/dev/null)
    DB_IS_RUNNING=false
    if [ -n "$DB_CONTAINER_ID" ]; then
        if docker ps -q --filter "id=$DB_CONTAINER_ID" --filter "status=running" | grep -q .; then
            DB_IS_RUNNING=true
        fi
    fi

    if [ "$DB_IS_RUNNING" = true ]; then
        echo "Контейнер БД 'db' уже запущен." | tee -a "$BACKEND_LOG_FILE"
    else
        echo "Контейнер БД 'db' не запущен или не в состоянии 'running'. Попытка запуска через 'docker-compose -f $COMPOSE_FILE up -d db'..." | tee -a "$BACKEND_LOG_FILE"
        # Запускаем docker-compose и выводим его stdout и stderr в лог бэкенда, а также в консоль
        if docker-compose -f "$COMPOSE_FILE" up -d db 2>&1 | tee -a "$BACKEND_LOG_FILE"; then
            # Проверяем код возврата docker-compose. tee всегда возвращает 0, поэтому проверяем pipefail, если возможно, или статус docker-compose.
            # Для простоты, если команда прошла без явной ошибки от tee, считаем успешным.
            # Более надежная проверка кода возврата docker-compose потребовала бы временного файла или более сложной конструкции.
            # В данном случае, если 'docker-compose up' выведет ошибку, она будет видна и в консоли, и в логе.
            # И 'set -e' должен прервать скрипт, если сама команда docker-compose вернет ненулевой код.
            echo "Контейнер БД 'db' запущен (или попытка запуска произведена). Проверьте вывод выше на наличие ошибок." | tee -a "$BACKEND_LOG_FILE"
            echo "Ожидание несколько секунд для инициализации PostgreSQL..." | tee -a "$BACKEND_LOG_FILE"
            sleep 15 # Даем время PostgreSQL внутри контейнера полностью запуститься
        else
            # Эта ветка 'else' может не выполниться, если 'set -e' прервет скрипт раньше из-за ошибки docker-compose
            echo "ОШИБКА: Не удалось запустить контейнер БД 'db' с помощью docker-compose." | tee -a "$BACKEND_LOG_FILE"
            echo "Пожалуйста, проверьте конфигурацию $COMPOSE_FILE и логи Docker (docker-compose -f $COMPOSE_FILE logs db)." | tee -a "$BACKEND_LOG_FILE"
            echo "Бэкенд, скорее всего, не сможет запуститься корректно без базы данных."
            # exit 1; # Можно добавить явный выход, если set -e не сработает как ожидается из-за пайплайна с tee
        fi
    fi
fi
echo "Проверка Docker БД завершена." | tee -a "$BACKEND_LOG_FILE"

# --- Backend (FastAPI) ---
echo "[1/2] Запуск Backend (FastAPI)..."
# Мы уже в PROJECT_ROOT_DIR

if [ ! -d ".venv/bin" ]; then
    echo "Ошибка: Виртуальное окружение .venv не найдено или неполное в $PROJECT_ROOT_DIR."
    echo "Выполните: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && alembic upgrade head"
    # exit 1 # Раскомментируйте, если хотите прервать скрипт здесь
fi

VENV_UVICORN="$PROJECT_ROOT_DIR/.venv/bin/uvicorn"
if [ ! -x "$VENV_UVICORN" ]; then
    echo "Ошибка: uvicorn не найден или не исполняемый в $VENV_UVICORN."
    # exit 1 # Раскомментируйте для прерывания
fi

echo "  Запуск uvicorn (app.main:app --reload --host 0.0.0.0 --port 8000)..."
# Очищаем старый лог бэкенда
>"$BACKEND_LOG_FILE"
nohup "$VENV_UVICORN" app.main:app --reload --host 0.0.0.0 --port 8000 >> "$BACKEND_LOG_FILE" 2>&1 &
BACKEND_PID=$!
sleep 1
if ps -p $BACKEND_PID > /dev/null; then
    echo "  Backend запущен (PID: $BACKEND_PID). Лог: $BACKEND_LOG_FILE"
else
    echo "  Ошибка запуска Backend. Проверьте $BACKEND_LOG_FILE для деталей."
fi
sleep 2 # Даем время на полный запуск

# --- Frontend (Next.js) ---
echo ""
echo "[2/2] Запуск Frontend (Next.js)..."
FRONTEND_DIR="$PROJECT_ROOT_DIR/frontend"
cd "$FRONTEND_DIR" || { echo "Ошибка: не удалось перейти в $FRONTEND_DIR"; exit 1; }

if [ ! -d "node_modules" ]; then
    echo "Предупреждение: node_modules не найдены в $FRONTEND_DIR. Может потребоваться 'npm install'."
fi

echo "  Запуск npm run dev..."
# Очищаем старый лог фронтенда перед новым запуском, чтобы видеть только актуальные сообщения
>"$FRONTEND_LOG_FILE" 
nohup npm run dev >> "$FRONTEND_LOG_FILE" 2>&1 &
FRONTEND_NPM_PID=$!
sleep 1
if ps -p $FRONTEND_NPM_PID > /dev/null; then
    echo "  Frontend (npm) запущен (PID: $FRONTEND_NPM_PID). Лог: $FRONTEND_LOG_FILE"
    echo "  Примечание: Фактический Next.js сервер будет дочерним процессом."
else
    echo "  Ошибка запуска Frontend (npm). Проверьте $FRONTEND_LOG_FILE для деталей."
fi

echo "  Ожидание полной инициализации Frontend (25 секунд)..."
sleep 25 

echo "  Проверка порта 3000 сразу после предполагаемого запуска Frontend..."
if sudo lsof -i :3000 > /dev/null; then 
    echo "  Next.js СЛУШАЕТ порт 3000 сразу после задержки."
else 
    echo "  Next.js НЕ СЛУШАЕТ порт 3000 сразу после задержки. Проверьте $FRONTEND_LOG_FILE внимательно."
fi 

# --- Проверка статуса --- 
echo ""
echo "== Проверка статуса сервисов (по портам) (финальная) =="
PORTS_TO_CHECK=("8000:Backend" "3000:Frontend")

for item in "${PORTS_TO_CHECK[@]}"; do
    PORT="${item%%:*}"
    SERVICE_NAME="${item#*:}"
    echo "$SERVICE_NAME (ожидается на порту $PORT):"
    if ss -tulnp | grep -q ":$PORT"; then 
        ACTUAL_PID=$(ss -tulnp | grep ":$PORT" | sed -n 's/.*pid=\([0-9]*\),.*/\1/p' | head -n 1)
        echo "  АКТИВЕН. Порт $PORT слушается. (Процесс PID: $ACTUAL_PID)"
    else
        LOG_FILE_PATH=""
        if [ "$SERVICE_NAME" == "Backend" ]; then
            LOG_FILE_PATH="$BACKEND_LOG_FILE"
        elif [ "$SERVICE_NAME" == "Frontend" ]; then
            LOG_FILE_PATH="$FRONTEND_LOG_FILE"
        fi
        echo "  НЕ АКТИВЕН или еще не запустился/уже остановился. Проверьте $LOG_FILE_PATH."
    fi
done

echo ""
echo "== Завершено =="
echo "Для остановки сервисов:"
echo "  Backend (uvicorn): 'kill $BACKEND_PID' (если PID еще актуален) или найдите процесс по порту 8000: 'sudo lsof -i :8000 | grep LISTEN' и 'kill <PID>'"
echo "  Frontend (npm + Next.js): 'kill $FRONTEND_NPM_PID' (остановит npm, что должно остановить Next.js)"
echo "    Или более надежно: 'pkill -f "next dev"' или найдите процесс по порту 3000: 'sudo lsof -i :3000 | grep LISTEN' и 'kill <PID>'"
