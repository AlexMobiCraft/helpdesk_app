"use client";

import React from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import NewDeviceForm from './NewDeviceForm.tsx';

export default function NewDevicePage() {
  const { t } = useTranslation();
  return (
    <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t('devices.new')}
      </Typography>
      <NewDeviceForm />
    </Box>
  );
}
