# План реализации: Страница списка ролей

**Цель:** Создать страницу `/admin/roles` со списком ролей пользователей в стиле страницы `/admin/devices`.

## 1. Backend (API)
1. Проверить в `Doc/API_endpoints_V1.1.md` наличие эндпоинтов:
   - **GET** `/api/v1/users/admin/roles` — получить список ролей (skip, limit).
   - **GET** `/api/v1/users/admin/roles/{role_id}` — получить детали роли.
   - **POST** `/api/v1/users/admin/roles` — создать роль.
   - **PATCH** `/api/v1/users/admin/roles/{role_id}` — обновить роль.
   - **DELETE** `/api/v1/users/admin/roles/{role_id}` — удалить роль.
2. Убедиться, что все эндпоинты защищены `Depends(get_current_admin_user)`.

## 2. Frontend
1. Создать директорию:
   ```
   frontend/app/admin/roles/
   ├── page.tsx        # Страница списка ролей
   └── RoleList.tsx    # Компонент таблицы ролей
   ```
2. В `page.tsx`:
   - Импортировать `useQuery` из React Query для GET `/api/v1/users/admin/roles?skip=<skip>&limit=<limit>`.
   - Отобразить компонент `RoleList`, передав полученные данные.
   - Реализовать пагинацию (Prev/Next) и фильтрацию по skip/limit аналогично `/admin/devices`.
3. В `RoleList.tsx`:
   - Использовать MUI-компоненты (`Table`, `TableRow`, `TableCell`, `Button`).
   - Колонки: №, Название роли, Описание, Действия (Редактировать, Удалить).
4. Реализовать кнопки:
   - **Создать**: ведёт на `/admin/roles/new` или открывает модал.
   - **Редактировать**: ведёт на `/admin/roles/edit/{id}`.
   - **Удалить**: вызывает DELETE-мутацию c `useMutation`.
5. После успешных операций инвалидировать кэш React Query:
   ```js
   invalidateQueries(['admin-roles'])
   ```

## 3. Локализация
1. Добавить в `frontend/locales/ru/common.json`, `en/common.json`, `sl/common.json` раздел:
   ```json
   "roles": {
     "title": "Роли",
     "new": "Новая роль",
     "name": "Название",
     "description": "Описание",
     "create": "Создать",
     "edit": "Редактировать",
     "delete": "Удалить",
     "actions": "Действия",
     "error": "Ошибка загрузки ролей",
     "loading": "Загрузка..."
   }
   ```
2. Использовать `t('roles.title')` и другие ключи в UI.

## 4. Навигация и доступ
1. В компоненте навигации (`Sidebar` или `Header`) добавить ссылку:
   ```jsx
   <NavLink href="/admin/roles">{t('roles.title')}</NavLink>
   ```
2. Убедиться, что страница доступна только администраторам.

## 5. Страница создания роли
1. Создать `frontend/app/admin/roles/new/page.tsx` и компонент `NewRoleForm.tsx`.
2. Поля формы: `name`, `description`.
3. При сабмите: POST `/api/v1/users/admin/roles`.
4. При успехе: уведомление и переход на `/admin/roles`.
5. При ошибке: отображать `t('roles.error')`.
6. Локализация новых элементов.

## 6. Страница редактирования роли
1. Создать `frontend/app/admin/roles/edit/[role_id]/page.tsx` и `EditRoleForm.tsx`.
2. Загрузить данные роли через GET `/api/v1/users/admin/roles/{role_id}`.
3. При сабмите: PATCH `/api/v1/users/admin/roles/{role_id}`.
4. При успехе: `invalidateQueries(['admin-roles'])` и переход на `/admin/roles`.
5. При ошибке: отображать `t('roles.error')`.
6. Локализация новых элементов.

## 7. Стиль и адаптивность
1. Использовать MUI-компоненты (`TextField`, `Select`, `Button`, `Grid`/`Stack`).
2. Обеспечить адаптивность для мобильных устройств.

## 8. Логирование ошибок
1. Клиент: `console.error` или Sentry.
2. Сервер: логировать ошибки в формате JSON.

## 9. Обновление документации
1. `Doc/PROJECT_STRUCTURE.md`: добавить раздел `admin/roles`.
2. `Doc/README.md`: обновить секцию Admin, добавить пункт "Роли".
3. `Doc/Technical_specification.md`: описать UI и поведение списка ролей.

## 10. Тестирование
1. Unit-тесты для `RoleList.tsx`.
2. Проверить работу локализации на всех языках.

---
