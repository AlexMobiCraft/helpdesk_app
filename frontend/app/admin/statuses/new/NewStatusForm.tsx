'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import {
  Box, TextField, Button, Alert
} from '@mui/material';
import { useTranslation } from 'react-i18next';

interface FormData { name: string; description?: string }

/**
 * Форма создания нового статуса
 */
export default function NewStatusForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  const createMutation = useMutation({
    mutationFn: data => api.post('/api/v1/statuses/admin/statuses', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-statuses'] });
      router.push('/admin/statuses');
    },
  });

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(data => createMutation.mutate(data))}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <TextField
        label={t('statuses.name')}
        {...register('name', { required: true })}
        error={!!errors.name}
        helperText={errors.name ? t('common.required') : ''}
        fullWidth
      />
      <TextField
        label={t('statuses.description')}
        {...register('description')}
        fullWidth
      />
      {createMutation.isError && <Alert severity="error">{t('statuses.error_create')}</Alert>}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={createMutation.isLoading}>
          {t('statuses.create')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
