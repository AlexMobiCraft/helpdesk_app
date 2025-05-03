'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { Box, TextField, Button, Alert, CircularProgress } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { AxiosResponse } from 'axios';

interface FormData { name: string; description?: string }
interface Props { status: FormData & { id: number } }

/**
 * Форма редактирования статуса
 */
export default function EditStatusForm({ status }: Props) {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  const isMutating = useIsMutating({ mutationKey: ['admin-statuses'] }) > 0;
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    defaultValues: { name: status.name, description: status.description || '' }
  });
  const updateMutation = useMutation<AxiosResponse, Error, FormData>({
    mutationFn: data => api.put(`/api/v1/statuses/admin/statuses/${status.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-statuses'] });
      router.push('/admin/statuses');
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
      {updateMutation.isError && <Alert severity="error">{t('statuses.error')}</Alert>}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={isMutating}>
          {t('statuses.edit')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
