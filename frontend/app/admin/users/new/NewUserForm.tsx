"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/api/axios";
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
} from "@mui/material";
import { toast } from "react-toastify";

// Интерфейс для формы создания нового пользователя
interface NewUserFormData {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
  confirm_password: string;
  role_id: number;
}

interface User {
  id: number;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role_id: number;
}

export default function NewUserForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  // Получить список ролей
  const { data: roles } = useQuery<{ id: number; name: string }[], Error>({
    queryKey: ["admin-roles"],
    queryFn: () =>
      api.get<{ id: number; name: string }[]>('/api/v1/users/admin/roles').then((res) => res.data),
  });

  const { register, handleSubmit, formState: { errors } } = useForm<NewUserFormData>({
    defaultValues: {
      first_name: "",
      last_name: "",
      username: "",
      email: "",
      password: "",
      confirm_password: "",
      role_id: roles?.[0]?.id ?? 1,
    },
  });

  // Мутация создания пользователя
  const createUserMutation = useMutation<User, Error, NewUserFormData>({
    mutationFn: (data) =>
      api.post<User>('/api/v1/users/admin/users', {
        first_name: data.first_name,
        last_name: data.last_name,
        username: data.username,
        email: data.email,
        password: data.password,
        role_id: data.role_id,
      }).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      toast.success(t('users.createSuccess') || 'Пользователь создан');
      router.push('/admin/users');
    },
    onError: () => {
      setError(t('users.error_create') || 'Ошибка при создании пользователя');
    },
  });

  const onSubmit = (data: NewUserFormData) => {
    setError(null);
    // Проверка паролей
    if (data.password !== data.confirm_password) {
      setError(t('users.passwordsDoNotMatch') || 'Пароли не совпадают');
      return;
    }
    if (data.password.length < 8) {
      setError(t('users.passwordTooShort') || 'Пароль должен содержать не менее 8 символов');
      return;
    }
    createUserMutation.mutate(data);
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {error && <Alert severity="error">{error}</Alert>}
      <TextField
        label={t('users.firstName') || 'Имя'}
        {...register('first_name', { required: true })}
        error={!!errors.first_name}
        helperText={errors.first_name ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <TextField
        label={t('users.lastName') || 'Фамилия'}
        {...register('last_name', { required: true })}
        error={!!errors.last_name}
        helperText={errors.last_name ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <TextField
        label={t('users.username') || 'Логин'}
        {...register('username', { required: true })}
        error={!!errors.username}
        helperText={errors.username ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <TextField
        label={t('users.email') || 'Email'}
        type="email"
        {...register('email', { required: true })}
        error={!!errors.email}
        helperText={errors.email ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <TextField
        label={t('users.password') || 'Пароль'}
        type="password"
        {...register('password', { required: true })}
        error={!!errors.password}
        helperText={errors.password ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <TextField
        label={t('users.confirmPassword') || 'Подтвердите пароль'}
        type="password"
        {...register('confirm_password', { required: true })}
        error={!!errors.confirm_password}
        helperText={errors.confirm_password ? t('common.required') || 'Обязательное поле' : ''}
        fullWidth
      />
      <FormControl fullWidth>
        <InputLabel id="role-label">{t('users.role') || 'Роль'}</InputLabel>
        <Select
          labelId="role-label"
          label={t('users.role') || 'Роль'}
          defaultValue={roles?.[0]?.id ?? 1}
          {...register('role_id', { valueAsNumber: true })}
        >
          {roles?.map((role) => (
            <MenuItem key={role.id} value={role.id}>
              {role.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={createUserMutation.status === 'pending'}>
          {t('users.create') || 'Создать'}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back') || 'Назад'}
        </Button>
      </Box>
    </Box>
  );
}
