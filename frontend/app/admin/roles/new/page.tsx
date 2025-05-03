'use client';

import React from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import NewRoleForm from './NewRoleForm';

/**
 * Страница создания новой роли
 */
export default function NewRolePage() {
  const { t } = useTranslation();
  return (
    <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t('roles.new')}
      </Typography>
      <NewRoleForm />
    </Box>
  );
}
