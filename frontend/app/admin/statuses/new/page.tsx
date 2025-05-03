'use client';

import React from 'react';
import AdminLayout from '../../layout';
import { useTranslation } from 'react-i18next';
import { Box, Typography } from '@mui/material';
import NewStatusForm from './NewStatusForm';

/**
 * Страница создания нового статуса
 */
export default function NewStatusPage() {
  const { t } = useTranslation();
  return (
    <AdminLayout>
      <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
        <Typography variant="h5" gutterBottom>
          {t('statuses.new')}
        </Typography>
        <NewStatusForm />
      </Box>
    </AdminLayout>
  );
}
