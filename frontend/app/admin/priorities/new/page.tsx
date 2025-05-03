'use client';

import React from 'react';
import AdminLayout from '../../layout';
import { useTranslation } from 'react-i18next';
import { Box, Typography } from '@mui/material';
import NewPriorityForm from './NewPriorityForm';

/**
 * Шаг 5: Страница создания приоритета
 */
export default function NewPriorityPage() {
  const { t } = useTranslation();
  return (
    <AdminLayout>
      <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
        <Typography variant="h5" gutterBottom>
          {t('priorities.new')}
        </Typography>
        <NewPriorityForm />
      </Box>
    </AdminLayout>
  );
}
