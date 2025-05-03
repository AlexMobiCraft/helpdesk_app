'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { AxiosResponse } from 'axios';
import { Box, TextField, Button, Alert, CircularProgress } from '@mui/material';

interface EditRoleFormData {
  name: string;
  description?: string;
}

interface EditRoleFormProps {
  role: {
    id: number;
    name: string;
    description?: string;
  };
}

/**
 * Форма редактирования роли
 */
export default function EditRoleForm({ role }: EditRoleFormProps) {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();
  // Флаг активности мутации
  const isMutating = useIsMutating() > 0;

  const { register, handleSubmit, formState: { errors } } = useForm<EditRoleFormData>({
    defaultValues: { name: role.name, description: role.description || '' }
  });

  const updateMutation = useMutation<AxiosResponse<any>, Error, EditRoleFormData>({
    mutationFn: data => api.put(`/api/v1/users/admin/roles/${role.id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      router.push('/admin/roles');
    },
    onError: () => console.error('Error updating role'),
  });

  if (isMutating) {
    return <CircularProgress />;
  }

  return (
    <Box component="form" onSubmit={handleSubmit(data => updateMutation.mutate(data))} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
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
      {updateMutation.isError && <Alert severity="error">{t('roles.error')}</Alert>}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={isMutating}>
          {t('roles.edit')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
