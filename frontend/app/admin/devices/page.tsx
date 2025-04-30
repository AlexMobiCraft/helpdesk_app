"use client";

import React from 'react';
import AdminLayout from '../layout';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import Link from 'next/link';
import DeviceList from './DeviceList.tsx';

export default function AdminDevicesPage() {
  const { t } = useTranslation();

  const { data: devices, isLoading, error } = useQuery({
    queryKey: ['admin-devices'],
    queryFn: () => api.get('/api/v1/devices/admin/devices').then(res => res.data),
  });

  return (
    <AdminLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <Link href="/admin" passHref>
            <Button variant="outlined">{t('admin.back')}</Button>
          </Link>
          <Link href="/admin/devices/new" passHref>
            <Button variant="contained" color="primary">{t('devices.new')}</Button>
          </Link>
        </Box>
        <Typography variant="h4" gutterBottom>{t('devices.title')}</Typography>
        {isLoading && <CircularProgress />}
        {error && <Alert severity="error">{t('devices.error')}</Alert>}
        {devices && <DeviceList devices={devices} />}
      </Box>
    </AdminLayout>
  );
}
