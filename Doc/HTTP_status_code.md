> **Примечание**: Структура ошибки валидации соответствует формату ошибок FastAPI по умолчанию, что удобно при использовании этого фреймворка.

# Основные HTTP Статус-коды ошибок

## 400 Bad Request
*  **Описание:** Запрос не может быть обработан из-за ошибки на стороне клиента (например, неверный формат json).

*  **Тело ответа:**
    ```json
    {
         "detail": "Сообщение об ошибке формата запроса." 
    }
    ```
## 401 Unauthorized
*  **Описание:** Ошибка аутентификации. Клиент не предоставил валидные учетные данные (например, отсутствует или недействителен JWT токен).

*  **Тело ответа:**
    ```json
    { 
        "detail": "Необходима аутентификация." 
    }
    ```
    или

    ```json
    {
         "detail": "Неверные учетные данные." 
    }
    ```
## 403 Forbidden
*  **Описание:** Доступ запрещен. Клиент аутентифицирован, но не имеет прав на выполнение данного действия (например, обычный пользователь пытается удалить заявку).

*  **Тело ответа:**
    ```json
    {
     "detail": "Недостаточно прав для выполнения операции." 
    }
    ```
## 404 Not Found
*  **Описание:** Запрошенный ресурс не найден (например, /api/tickets/99999 или /api/users/nonexistent).

*  **Тело ответа:**
    ```json
    { 
        "detail": "Ресурс не найден." 
    }
    ```
    (или более конкретно, например: "Заявка не найдена.")

## 409 Conflict
*  **Описание:** Запрос не может быть выполнен из-за конфликта с текущим состоянием ресурса (например, попытка создать пользователя с уже существующим username).

*  **Тело ответа:**
    ```json
    {
         "detail": "Конфликт ресурса. Например, пользователь с таким именем уже существует." 
    }
    ```
## 422 Unprocessable Entity
*  **Описание:** Запрос синтаксически корректен, но содержит семантические ошибки (например, не прошли проверки валидации данных).

*  **Тело ответа:**
Структура ошибки валидации (см. выше).

## 500 Internal Server Error
*  **Описание:** Произошла непредвиденная ошибка на сервере.

*  **Тело ответа:**
    ```json
    {
         "detail": "Внутренняя ошибка сервера." 
    }
    ```
    (В режиме разработки может содержать больше деталей.)

## 503 Service Unavailable
*  **Описание:** Сервер временно недоступен (например, на техническом обслуживании или перегружен).

*  **Тело ответа:**
    ```json
    {
         "detail": "Сервис временно недоступен." 
    }
    ```