"use client";

import React from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import EditDeviceForm from './EditDeviceForm';

interface Device {
  device_id: number;
  name: string;
  device_type_id?: number;
  inventory_number?: string;
}

export default function EditDevicePage() {
  const { t } = useTranslation();
  const { device_id } = useParams();
  const id = Number(device_id);

  const { data: device, isLoading, error } = useQuery<Device, Error>({
    queryKey: ['device', id],
    queryFn: () => api.get<Device>(`/api/v1/devices/${id}`).then(res => res.data),
  });

  if (isLoading) return <CircularProgress />;
  if (error || !device) return <Alert severity="error">{t('devices.error')}</Alert>;

  return (
    <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t('devices.edit')} {device.name}
      </Typography>
      <EditDeviceForm device={device} />
    </Box>
  );
}
