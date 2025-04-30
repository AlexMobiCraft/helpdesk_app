# План реализации функционала изменения пароля пользователя администратором

## Анализ текущей ситуации

- В форме редактирования пользователя (`EditUserForm.tsx`) отсутствует функционал изменения пароля
- В API существует эндпоинт для смены пароля самим пользователем (`/api/v1/users/me/password`)
- В API также существует специальный эндпоинт для изменения пароля администратором (`/api/v1/users/admin/users/{user_id}/password`) с методом `POST`
- Необходимо реализовать интерфейс для использования существующего API-эндпоинта

## Задачи для реализации

### 1. Модификация компонента EditUserForm.tsx

1. Добавить отдельную форму для изменения пароля, которая будет показываться/скрываться по кнопке:
   ```typescript
   // Интерфейс для формы изменения пароля
   type PasswordFormData = {
     password: string;
     confirm_password: string;
   };
   ```

2. Добавить состояния для управления формой пароля:
   ```typescript
   const [showPasswordFields, setShowPasswordFields] = useState<boolean>(false);
   const [passwordError, setPasswordError] = useState<string | null>(null);
   
   // Отдельный useForm для формы пароля
   const passwordForm = useForm<PasswordFormData>({
     defaultValues: {
       password: '',
       confirm_password: ''
     }
   });
   ```

3. Добавить в компонент отдельную секцию для изменения пароля:
   ```tsx
   {/* Секция изменения пароля */}
   <Box mt={4}>
     <Button 
       variant="outlined" 
       onClick={() => setShowPasswordFields(!showPasswordFields)}
       startIcon={showPasswordFields ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
     >
       {t('users.changePassword')}
     </Button>
     
     {showPasswordFields && (
       <Box mt={2} component="form" onSubmit={passwordForm.handleSubmit(handlePasswordSubmit)}>
         <Grid container spacing={2}>
           <Grid item xs={12} md={6}>
             <TextField
               fullWidth
               label={t('users.newPassword')}
               type="password"
               {...passwordForm.register('password', { required: true })}
               error={!!passwordForm.formState.errors.password || !!passwordError}
               helperText={passwordForm.formState.errors.password ? t('common.required') : ''}
             />
           </Grid>
           <Grid item xs={12} md={6}>
             <TextField
               fullWidth
               label={t('users.confirmPassword')}
               type="password"
               {...passwordForm.register('confirm_password', { required: true })}
               error={!!passwordForm.formState.errors.confirm_password || !!passwordError}
               helperText={passwordError || (passwordForm.formState.errors.confirm_password ? t('common.required') : '')}
             />
           </Grid>
           <Grid item xs={12}>
             <Button 
               type="submit" 
               variant="contained" 
               color="primary"
               disabled={passwordMutation.isPending}
             >
               {passwordMutation.isPending ? <CircularProgress size={24} /> : t('users.resetPassword')}
             </Button>
           </Grid>
         </Grid>
       </Box>
     )}
   </Box>
   ```

4. Реализовать валидацию паролей в функции отправки формы:
   ```typescript
   const handlePasswordSubmit = (data: PasswordFormData) => {
     // Проверка совпадения паролей
     if (data.password !== data.confirm_password) {
       setPasswordError(t('users.passwordsDoNotMatch'));
       return;
     }
     
     // Проверка минимальной длины пароля
     if (data.password.length < 8) {
       setPasswordError(t('users.passwordTooShort'));
       return;
     }
     
     // Сброс ошибок
     setPasswordError(null);
     
     // Вызов мутации для изменения пароля
     passwordMutation.mutate({ new_password: data.password });
   };
   ```

5. Обеспечить очистку полей пароля при закрытии формы:
   ```typescript
   useEffect(() => {
     if (!showPasswordFields) {
       passwordForm.reset();
       setPasswordError(null);
     }
   }, [showPasswordFields, passwordForm]);

### 2. Модификация API-запроса

1. Создать отдельную функцию мутации для изменения пароля, которая будет использовать специальный эндпоинт:
   ```typescript
   const passwordMutation = useMutation<void, Error, { new_password: string }>({  
     mutationFn: (passwordData): Promise<void> => {
       return api.post<void>(`/api/v1/users/admin/users/${userId}/password`, {
         new_password: passwordData.new_password
       }).then(() => {});
     },
     onSuccess: () => {
       // Очистка полей пароля и отображение сообщения об успехе
       setShowPasswordFields(false);
       // Сброс значений полей пароля
       reset({ password: '', confirm_password: '' });
       // Отображение уведомления об успешном изменении пароля
       toast.success(t('users.passwordResetSuccess'));
     },
     onError: (error) => {
       // Обработка ошибок от сервера
       toast.error(t('users.passwordResetError'));
       console.error('Password reset error:', error);
     }
   });
   ```

2. Создать отдельную функцию для отправки формы изменения пароля:
   ```typescript
   const handlePasswordSubmit = (data: { password: string, confirm_password: string }) => {
     // Проверка совпадения паролей
     if (data.password !== data.confirm_password) {
       setPasswordError(t('users.passwordsDoNotMatch'));
       return;
     }
     
     // Сброс ошибок
     setPasswordError(null);
     
     // Вызов мутации для изменения пароля
     passwordMutation.mutate({ new_password: data.password });
   };
   ```

### 3. Обработка ошибок

1. Обработка ошибок валидации пароля на стороне клиента:
   ```typescript
   // Проверка совпадения паролей
   if (data.password !== data.confirm_password) {
     setPasswordError(t('users.passwordsDoNotMatch'));
     return;
   }
   
   // Проверка минимальной длины пароля
   if (data.password.length < 8) {
     setPasswordError(t('users.passwordTooShort'));
     return;
   }
   ```

2. Обработка ошибок от сервера в мутации:
   ```typescript
   onError: (error) => {
     // Отображение ошибки пользователю
     toast.error(t('users.passwordResetError'));
     console.error('Password reset error:', error);
   }
   ```

### 4. Локализация

1. Добавить новые ключи в файлы локализации для текстов, связанных с изменением пароля:
   ```json
   {
     "users": {
       "changePassword": "Изменить пароль",
       "newPassword": "Новый пароль",
       "confirmPassword": "Подтвердите пароль",
       "resetPassword": "Сбросить пароль",
       "passwordsDoNotMatch": "Пароли не совпадают",
       "passwordTooShort": "Пароль должен содержать не менее 8 символов",
       "passwordResetSuccess": "Пароль успешно изменен",
       "passwordResetError": "Ошибка при изменении пароля"
     }
   }
   ```

## Примечания по безопасности

1. Пароль должен передаваться только по HTTPS
2. Не сохранять пароль в состоянии после успешной отправки
3. Очищать поля пароля при отмене изменений или успешном сбросе
4. На сервере пароль хешируется перед сохранением в базу данных (уже реализовано в API)
5. Использовать отдельный POST-запрос для изменения пароля вместо включения пароля в общий запрос обновления пользователя

## Тестирование

1. Проверить валидацию паролей на клиенте:
   - Проверка на совпадение паролей
   - Проверка на минимальную длину пароля

2. Проверить успешное изменение пароля:
   - Отправка запроса на API-эндпоинт `/api/v1/users/admin/users/{user_id}/password`
   - Проверка возможности входа с новым паролем

3. Проверить обработку ошибок от сервера:
   - Имитация ошибки сервера
   - Проверка отображения сообщения об ошибке

4. Проверить работу интерфейса:
   - Показ/скрытие формы изменения пароля
   - Очистка полей при закрытии формы
   - Отображение индикатора загрузки при отправке запроса