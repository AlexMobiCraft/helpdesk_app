"use client";

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useForm, Controller } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import api from '@/api/axios';
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

interface EditDeviceFormProps {
  device: {
    device_id: number;
    name: string;
    device_type_id?: number;
    inventory_number?: string;
  };
}

interface EditDeviceFormData {
  device_id: number;
  name: string;
  device_type_id: number;
  inventory_number?: string;
}

interface DeviceRead { device_id: number; }

export default function EditDeviceForm({ device }: EditDeviceFormProps) {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: types = [], isLoading: typesLoading, error: typesError } = useQuery<
    { device_type_id: number; name: string }[],
    Error
  >({
    queryKey: ['device-types'],
    queryFn: () => api.get<{ device_type_id: number; name: string }[]>('/api/device-types').then(res => res.data),
  });

  const { data: allDevices = [], isLoading: allLoading } = useQuery<DeviceRead[], Error>({
    queryKey: ['admin-devices'],
    queryFn: () => api.get<DeviceRead[]>('/api/v1/devices/admin/devices').then(res => res.data),
  });

  const { register, control, handleSubmit, formState: { errors }, reset } = useForm<EditDeviceFormData>({
    defaultValues: {
      device_id: device.device_id,
      name: device.name,
      device_type_id: device.device_type_id ?? (types[0]?.device_type_id ?? 0),
      inventory_number: device.inventory_number ?? '',
    }
  });

  React.useEffect(() => {
    if (types.length > 0) {
      reset({
        device_id: device.device_id,
        name: device.name,
        device_type_id: device.device_type_id ?? types[0].device_type_id,
        inventory_number: device.inventory_number ?? '',
      });
    }
  }, [types, device, reset]);

  const updateMutation = useMutation<AxiosResponse<any, any>, Error, EditDeviceFormData>({
    mutationFn: data => api.put(`/api/v1/devices/admin/devices/${device.device_id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-devices'] });
      router.push('/admin/devices');
    },
    onError: () => alert(t('devices.error')),
  });

  const onSubmit = (data: EditDeviceFormData) => updateMutation.mutate(data);

  if (typesLoading || allLoading) return <CircularProgress />;
  if (typesError) return <Alert severity="error">{t('devices.error')}</Alert>;

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <TextField
        label={t('devices.id')}
        type="number"
        {...register('device_id', {
          required: t('common.required'),
          valueAsNumber: true,
          validate: value => allDevices.every(dev => dev.device_id !== value || value === device.device_id) || t('devices.idUnique')
        })}
        error={!!errors.device_id}
        helperText={errors.device_id?.message}
        fullWidth
      />
      <TextField
        label={t('devices.name')}
        {...register('name', { required: true })}
        error={!!errors.name}
        helperText={errors.name ? t('common.required') : ''}
        fullWidth
      />

      <Controller
        name="device_type_id"
        control={control}
        defaultValue={device.device_type_id ?? types[0]?.device_type_id}
        render={({ field }) => (
          <FormControl fullWidth error={!!typesError}>
            <InputLabel id="type-label">{t('devices.type')}</InputLabel>
            <Select
              labelId="type-label"
              label={t('devices.type')}
              {...field}
            >
              {types.map(type => (
                <MenuItem key={type.device_type_id} value={type.device_type_id}>
                  {type.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      />

      <TextField
        label={t('devices.inventoryNumber')}
        {...register('inventory_number')}
        fullWidth
      />

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button type="submit" variant="contained" disabled={updateMutation.isPending}>
          {t('devices.edit')}
        </Button>
        <Button variant="outlined" onClick={() => router.back()}>
          {t('admin.back')}
        </Button>
      </Box>
    </Box>
  );
}
