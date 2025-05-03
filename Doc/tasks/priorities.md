# План реализации страницы «Приоритеты»

Необходимо создать страницу управления приоритетами заявок по аналогии со страницей статусов `/admin/statuses`.

## 1. Навигация (выполнено)
- В `frontend/app/admin/layout.tsx` добавить кнопку «Приоритеты» (`t('priorities.title')`) с переходом на `/admin/priorities`.

## 2. Локализация (выполнено)
1. В каждом файле `frontend/locales/{ru,en,sl}/common.json`
   - Добавить корневой раздел `"priorities"` с ключами:
     - title: «Приоритеты» / «Priorities» / «Prioritete»
     - new: «Новый приоритет» / «New Priority» / «Nov prioritet»
     - name: «Название» / «Name» / «Ime»
     - description: «Описание» / «Description» / «Opis»
     - order: "Порядок" / "Order" / "Zaporedje"
     - create, edit, delete, actions, error, loading

## 3. Маршруты и файлы
```
frontend/app/admin/priorities/
├─ page.tsx            # список приоритетов
├─ new/
│  └─ page.tsx         # страница создания
│  └─ NewPriorityForm.tsx
└─ edit/[priority_id]/
   └─ page.tsx         # страница редактирования
   └─ EditPriorityForm.tsx
```

## 4. Список (page.tsx)
- Использовать `useQuery` с `queryKey: ['admin-priorities', skip]`
- GET `/api/v1/priorities/admin/priorities?skip={skip}&limit={limit}`
- Маппить из `priority_id` → `id` и `display_order` → `display_order`
- Интеграция пагинации (`skip`, `limit`) и кнопки Prev/Next, как на страницах ролей/статусов.
- Выводить `PriorityList` с таблицей и кнопками редактирования/удаления.

## 5. Компонент PriorityList
- Колонки: Name, Order, Actions
- Иконки:
  - Edit → ссылка `/admin/priorities/edit/${id}`
  - Delete → мутация DELETE и `invalidateQueries(['admin-priorities'])`
- Уникальные ключи строк: `priority-${id}` с fallback на `idx`.

## 6. Формы создания и редактирования
- NewPriorityForm:
  - `useForm<FormData>` с полями `name`, `description`, `display_order`
  - `useMutation` POST `/api/v1/priorities/admin/priorities`
  - При успехе переадресация на `/admin/priorities` и `invalidateQueries`
- EditPriorityForm:
  - Принимает `priority: { id, name, description, display_order }`
  - `useMutation` PUT `/api/v1/priorities/admin/priorities/${id}`

## 7. Обработка ошибок и загрузки
- `isLoading` → `<CircularProgress />`
- Ошибки → `<Alert severity="error">{t('priorities.error')}</Alert>`
- Создание/редактирование → отдельные ключи `error_create`/`error_update`.

## 8. Документация 
- `Doc/PROJECT_STRUCTURE.md`: добавить раздел `admin/priorities`.
- `Doc/API_endpoints_V1.1.md`: убедиться в наличии эндпоинтов `/api/v1/priorities/admin/priorities…`.
- `Doc/README.md`: обновить секцию Admin, добавить пункт "Приоритеты".
- `Doc/Technical_specification.md`: описать UI и поведение списка приоритетов.
- Проверить CRUD-поток: список, создание, редактирование, удаление

---
