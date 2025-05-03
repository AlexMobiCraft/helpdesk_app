# План реализации: Страница списка статусов

**Цель:** Создать страницу `/admin/statuses` со списком статусов задач по аналогии с `/admin/roles`.

## 1. Backend (API)
1. Проверить в `Doc/API_endpoints_V1.1.md` наличие эндпоинтов:
   - **GET** `/api/v1/statuses/admin/statuses` — получить список статусов (параметры `skip`, `limit`).
   - **GET** `/api/v1/statuses/admin/statuses/{status_id}` — получить детали статуса.
   - **POST** `/api/v1/statuses/admin/statuses` — создать новый статус.
   - **PUT** `/api/v1/statuses/admin/statuses/{status_id}` — обновить статус.
   - **DELETE** `/api/v1/statuses/admin/statuses/{status_id}` — удалить статус.
2. Убедиться, что все эндпоинты защищены `Depends(get_current_admin_user)`.

## 2. Frontend
1. Создать директорию `frontend/app/admin/statuses/`:
   ```text
   frontend/app/admin/statuses/
   ├── page.tsx                 # Страница списка статусов
   ├── StatusList.tsx           # Компонент таблицы статусов
   ├── new/
   │   ├── page.tsx             # Страница создания статуса
   │   └── NewStatusForm.tsx    # Форма создания
   └── edit/[status_id]/
       ├── page.tsx             # Страница редактирования статуса
       └── EditStatusForm.tsx   # Форма редактирования статуса
   ```
2. В `page.tsx`:
   - Использовать React Query v5 (`useQuery`) для GET списка.
   - Передать данные в `<StatusList>`.
   - Реализовать пагинацию (Prev/Next) как в `/admin/roles`.
3. В `StatusList.tsx`:
   - Отобразить MUI `<Table>` с колонками: `name`, `description`, `actions`.
   - Кнопки «Редактировать» и «Удалить» (`useMutation` DELETE + `invalidateQueries`).
4. Форма создания (`NewStatusForm.tsx`):
   - `react-hook-form` + валидация.
   - `useMutation` POST + `invalidateQueries`.
5. Форма редактирования (`EditStatusForm.tsx`):
   - `useParams` для `status_id`, `useQuery` для GET деталей.
   - `react-hook-form` с `defaultValues`.
   - `useMutation` PUT/PATCH + `invalidateQueries`.

## 3. Локализация
- Добавить ключи в `frontend/locales/{ru,en,sl}/common.json`:
  ```json
  "statuses": {
    "title": "Статусы",
    "new": "Новый статус",
    "name": "Название",
    "description": "Описание",
    "create": "Создать",
    "edit": "Изменить",
    "delete": "Удалить",
    "actions": "Действия",
    "error": "Ошибка при загрузке статусов",
    "loading": "Загрузка..."
  }
  ```

## 4. Навигация
- В `frontend/app/admin/layout.tsx` добавить кнопку `/admin/statuses` с переводом `t('admin.statuses')` рядом с остальными разделами.

## 5. Тестирование
- Покрыть компонент `StatusList` и формы unit-тестами.

## 6. Обновление документации
1. `Doc/PROJECT_STRUCTURE.md`: добавить раздел `admin/statuses`.
2. `Doc/API_endpoints_V1.1.md`: убедиться в наличии эндпоинтов `/api/v1/statuses/admin/statuses…`.
3. `Doc/README.md`: обновить секцию Admin, добавить пункт "Статусы".
4. `Doc/Technical_specification.md`: описать UI и поведение списка статусов.

## 7. Стиль и адаптивность
1. Использовать MUI-компоненты (`TextField`, `Select`, `Button`, `Grid`/`Stack`).
2. Обеспечить адаптивность для мобильных устройств.

## 8. Логирование ошибок
1. Клиент: `console.error` или Sentry.
2. Сервер: логировать ошибки в формате JSON.
