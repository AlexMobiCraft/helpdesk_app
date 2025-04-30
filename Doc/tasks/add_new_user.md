# Задача: Страница "Новый пользователь"

## 1. Цель
Создать новую страницу и форму для ввода данных нового пользователя в админке.

## 2. Эндпоинты (см. API_endpoints_V1.1.md)
- **POST** `/api/v1/users/admin/users` — создание нового пользователя.
- **GET** `/api/v1/users/admin/roles` — получение списка доступных ролей.

## 3. Структура файлов
```
frontend/app/admin/users/new/
├── page.tsx            # Next.js страница
└── NewUserForm.tsx     # React-компонент формы
```  

## 4. Шаги реализации

### 4.1 Локализация
- Добавить ключи в `frontend/public/locales/{ru,en,sl}/common.json`:
  ```jsonc
  "users": {
    "new": "Новый пользователь",
    "create": "Создать",
    "firstName": "Имя",
    "lastName": "Фамилия",
    "username": "Логин",
    "email": "Email",
    "password": "Пароль",
    "confirmPassword": "Подтвердите пароль",
    "role": "Роль",
    "error_create": "Ошибка при создании пользователя"
  }
  ```

### 4.2 UI и логика на фронтенде
1. **page.tsx**
   - Импортировать `NewUserForm`.
   - Разместить заголовок `t('users.new')`.
2. **NewUserForm.tsx**
   - Использовать `react-hook-form` для полей: `first_name`, `last_name`, `username`, `email`, `password`, `confirm_password`, `role_id`.
   - Получить список ролей через `useQuery(['admin-roles'], fetchRoles)`.
   - Мутация `useMutation` для POST `/api/v1/users/admin/users`.
   - В случае успеха — `router.push('/admin/users')` и `toast.success`.
   - В случае ошибки — отобразить `Alert` с `t('users.error_create')`.

### 4.3 Маршрутизация
- В списке пользователей (страница `/admin/users`) кнопка "Новый пользователь" должна ссылаться на `/admin/users/new`.

### 4.4 Тестирование
- Проверить валидацию (требуемые поля, подтверждение пароля).
- Убедиться, что после создания происходит переход на список и новый пользователь появляется в списке.

## 5. Дополнительно
- Добавить unit-тесты для `NewUserForm`.

---
