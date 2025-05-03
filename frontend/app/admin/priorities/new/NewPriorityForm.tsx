'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { Box, TextField, Button, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';

interface FormData {
  name: string;
  description?: string;
  display_order: number;
}

/**
 * Шаг 6.1: Форма создания приоритета
 */
export default function NewPriorityForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();
  const createMutation = useMutation({
    mutationFn: (data: FormData) => api.post('/api/v1/priorities/admin/priorities', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-priorities'] });
      router.push('/admin/priorities');
    },
  });

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(data => createMutation.mutate(data))}
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <TextField
        label={t('priorities.name')}
        {...register('name', { required: true })}
        error={!!errors.name}
        helperText={errors.name ? t('common.required') : ''}
        fullWidth
      />
      <TextField
        label={t('priorities.description')}
        {...register('description')}
        fullWidth
      />
      <TextField
        label={t('priorities.order')}
        type="number"
        {...register('display_order', { required: true, valueAsNumber: true })}
        error={!!errors.display_order}
        helperText={errors.display_order ? t('common.required') : ''}
        fullWidth
      />
      {createMutation.isError && (
        <Alert severity="error">{t('priorities.error_create')}</Alert>
      )}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          type="submit"
          variant="contained"
          disabled={createMutation.isLoading}
        >
          {t('priorities.create')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
