'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { Box, TextField, Button, Alert, CircularProgress } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { AxiosResponse } from 'axios';

interface FormData { name: string; description?: string; display_order: number; }
interface Props { priority: FormData & { id: number }; }

/**
 * Шаг 6.2: Форма редактирования приоритета
 */
export default function EditPriorityForm({ priority }: Props) {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isMutating = useIsMutating({ mutationKey: ['admin-priorities'] }) > 0;
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      name: priority.name,
      description: priority.description || '',
      display_order: priority.display_order,
    },
  });
  const updateMutation = useMutation<AxiosResponse, Error, FormData>({
    mutationFn: data => api.put(`/api/v1/priorities/admin/priorities/${priority.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-priorities'] });
      router.push('/admin/priorities');
    },
  });

  if (isMutating) return <CircularProgress />;

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(data => updateMutation.mutate(data))}
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
      {updateMutation.isError && (
        <Alert severity="error">{t('priorities.error_update')}</Alert>
      )}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={isMutating}>
          {t('priorities.edit')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
