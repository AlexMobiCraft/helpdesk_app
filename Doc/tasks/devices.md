# План реализации: Страница списка устройств

**Цель:** Создать страницу `/admin/devices` со списком устройств в стиле страницы списка пользователей.

## 1. Backend (API)
1. Проверить в `Doc/API_endpoints_V1.1.md` наличие:
   - **GET** `/api/device-types` — список типов устройств.
   - **GET** `/api/devices` — список устройств (с фильтрацией, пагинацией).
2. При необходимости скорректировать описание или добавить следующие эндпоинты:
   - **POST** `/api/admin/devices` — создание устройства.
   - **PATCH** `/api/admin/devices/{id}` — обновление данных устройства.
   - **DELETE** `/api/admin/devices/{id}` — удаление устройства.
3. Убедиться, что все эндпоинты имеют зависимости `Depends(get_current_admin_user)` для защиты.

## 2. Frontend
1. Создать директорию:
   ```
   frontend/app/admin/devices/
   ├── page.tsx             # Страница списка устройств
   └── DeviceList.tsx       # Компонент таблицы
   ```
2. В `page.tsx`:
   - Импортировать `useQuery` из React Query для запроса GET `/api/devices`.
   - Отобразить компонент `DeviceList`, передав полученные данные.
3. В `DeviceList.tsx`:
   - Использовать MUI-компоненты (`Table`, `TableRow`, `TableCell`, `Button`).
   - Колонки: №, Название, Тип устройства, Инвентарный номер, Действия (Редактировать, Удалить).
4. Реализовать кнопки:
   - **Создать**: ведёт на `/admin/devices/new` или открывает модал.
   - **Редактировать**: `/admin/devices/edit/{id}`.
   - **Удалить**: вызывает DELETE-мутацию c `useMutation`.
5. Валидация форм создания/редактирования через `react-hook-form`.
6. После успешных операций инвалидировать кэш React Query (`invalidateQueries(['admin-devices'])`).

## 3. Локализация
1. Добавить в `frontend/locales/ru/common.json`, `en/common.json`, `sl/common.json` раздел:
   ```json
   "devices": {
     "title": "Устройства",         // "Devices" / "Naprave"
     "new": "Новое устройство",    // "New device" / "Nov naprava"
     "name": "Название",           // "Name" / "Ime"
     "type": "Тип устройства",     // "Type" / "Tip naprave"
     "inventoryNumber": "Инв. номер", // "Inventory #" / "Št. inventarja"
     "create": "Создать",           // "Create" / "Ustvari"
     "edit": "Редактировать",       // "Edit" / "Uredi"
     "delete": "Удалить",           // "Delete" / "Izbriši"
     "actions": "Действия",         // "Actions" / "Dejanja"
     "error": "Ошибка загрузки устройств", // etc.
     "loading": "Загрузка..."
   }
   ```
2. Использовать `t('devices.title')` и другие ключи в UI.

## 4. Навигация и доступ
1. В компоненте навигации (`Sidebar` или `Header`) добавить ссылку:
   ```jsx
   <NavLink href="/admin/devices">{t('devices.title')}</NavLink>
   ```
2. Убедиться, что страница доступна только администраторам (через защиту маршрутов).

## 5. Обновление документации
1. `Doc/PROJECT_STRUCTURE.md`: добавить раздел `admin/devices`.
2. `Doc/README.md`: обновить структуру проекта и секцию API Эндпоинты.
3. `Doc/Technical_specification.md`: в разделе 3.4 (Справочник оборудования) отразить новые UI-моменты.

## 6. Тестирование
1. Написать unit-тесты для `DeviceList.tsx`.
2. E2E-тест на создание, редактирование и удаление устройства (Cypress или Playwright).
3. Проверить работу локализации на всех языках.

## 7. Создание страницы добавления устройства
1. Создать `frontend/app/admin/devices/new/page.tsx` и компонент `NewDeviceForm.tsx`.
2. Использовать `react-hook-form` для управления формой.
3. Поля формы:
   - `name`: название устройства.
   - `device_type_id`: выбор типа устройства из GET `/api/device-types`.
   - `inventory_number`: инвентарный номер.
4. При сабмите:
   - Вызвать `api.post('/api/v1/devices/admin/devices', {...})`.
   - При успехе: показать уведомление и перенаправить на `/admin/devices`.
   - При ошибке: показать сообщение об ошибке `t('devices.error')`.
5. Сделать локализацию новых элементов интерфейса

## 8. Создание страницы редактирования устройства
1. Создать `frontend/app/admin/devices/edit/[device_id]/page.tsx` и компонент `EditDeviceForm.tsx`.
2. Загрузить данные устройства с помощью `useQuery`:
   ```js
   api.get(`/api/v1/devices/admin/devices/${device_id}`)
   ```
3. Заполнить форму начальными данными.
4. При сабмите:
   - Вызвать `api.patch(`/api/v1/devices/admin/devices/${device_id}`, {...})`.
   - По успеху: инвалидировать кэш `['admin-devices']` и перенаправиться на `/admin/devices`.
   - По ошибке: показать сообщение об ошибке `t('devices.error')`.
5. Сделать локализацию новых элементов интерфейса

## 9. Стиль и адаптивность
1. Использовать MUI-компоненты для форм (`TextField`, `Select`, `Button`, `Grid`).
2. Обеспечить адаптивность: использовать `Stack` или `Grid` для мобильных устройств.

## 10. Логирование ошибок
1. На клиенте: логировать ошибки API через `console.error` или Sentry.
2. На сервере: убедиться, что ошибки устройств логируются в формате JSON.

---
