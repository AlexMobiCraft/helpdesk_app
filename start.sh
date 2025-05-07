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
