"use client";

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import { AxiosResponse } from 'axios';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';

interface NewDeviceFormData {
  device_id: number;
  name: string;
  device_type_id: number;
  inventory_number?: string;
}

export default function NewDeviceForm() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: types = [], isLoading: typesLoading, error: typesError } = useQuery<{ device_type_id: number; name: string }[], Error>({
    queryKey: ['device-types'],
    queryFn: () => api.get<{ device_type_id: number; name: string }[]>('/api/device-types').then(res => res.data),
  });

  const { register, handleSubmit, formState: { errors } } = useForm<NewDeviceFormData>({
    defaultValues: {
      device_id: 0,
      name: '',
      device_type_id: types?.[0]?.device_type_id ?? 0,
      inventory_number: '',
    },
  });

  const createMutation = useMutation<AxiosResponse<any, any>, Error, NewDeviceFormData>({
    mutationFn: data => api.post('/api/v1/devices/admin/devices', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-devices'] });
      router.push('/admin/devices');
    },
    onError: () => alert(t('devices.error')),
  });

  const onSubmit = (data: NewDeviceFormData) => {
    // если пользователь не выбрал тип, используем первый из списка
    if (!data.device_type_id && types.length > 0) {
      data.device_type_id = types[0].device_type_id;
    }
    createMutation.mutate(data);
  };

  if (typesLoading) return <CircularProgress />;
  if (typesError) return <Alert severity="error">{t('devices.error')}</Alert>;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField
        label={t('devices.id')}
        type="number"
        {...register('device_id', { required: true, valueAsNumber: true })}
        error={!!errors.device_id}
        helperText={errors.device_id ? t('common.required') : ''}
        fullWidth
      />
      <TextField
        label={t('devices.name')}
        {...register('name', { required: true })}
        error={!!errors.name}
        helperText={errors.name ? t('common.required') : ''}
        fullWidth
      />
      <FormControl fullWidth error={!!typesError}>
        <InputLabel id="type-label">{t('devices.type')}</InputLabel>
        <Select
          labelId="type-label"
          label={t('devices.type')}
          defaultValue={types?.[0]?.device_type_id ?? ''}
          {...register('device_type_id', { valueAsNumber: true })}
        >
          {types.map(type => (
            <MenuItem key={type.device_type_id} value={type.device_type_id}>
              {type.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <TextField
        label={t('devices.inventoryNumber')}
        {...register('inventory_number')}
        fullWidth
      />
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={createMutation.status === 'pending'}>
          {t('devices.create')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
