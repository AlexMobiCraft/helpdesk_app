'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { AxiosResponse } from 'axios';
import { Box, TextField, Button, Alert, CircularProgress } from '@mui/material';

interface NewRoleFormData {
  name: string;
  description?: string;
}

/**
 * Компонент формы создания новой роли
 */
export default function NewRoleForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors } } = useForm<NewRoleFormData>({ defaultValues: { name: '', description: '' } });

  const createMutation = useMutation<AxiosResponse<any>, Error, NewRoleFormData>({
    mutationFn: data => api.post('/api/v1/users/admin/roles', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      router.push('/admin/roles');
    },
    onError: () => console.error('Error creating role')
  });

  const onSubmit = (data: NewRoleFormData) => {
    createMutation.mutate(data);
  };

  if (createMutation.status === 'pending') return <CircularProgress />;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField
        label={t('roles.name')}
        {...register('name', { required: true })}
        error={!!errors.name}
        helperText={errors.name ? t('common.required') : ''}
        fullWidth
      />
      <TextField
        label={t('roles.description')}
        {...register('description')}
        fullWidth
      />
      {createMutation.isError && <Alert severity="error">{t('roles.error')}</Alert>}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={createMutation.status === 'pending'}>{t('roles.create')}</Button>
        <Button variant="outlined" onClick={() => router.back()}>{t('admin.back')}</Button>
      </Box>
    </Box>
  );
}
