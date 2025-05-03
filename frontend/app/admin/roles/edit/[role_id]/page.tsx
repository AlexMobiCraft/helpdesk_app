'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import EditRoleForm from './EditRoleForm';

interface Role {
  id: number;
  name: string;
  description?: string;
}

/**
 * Страница редактирования роли
 */
export default function EditRolePage() {
  const { t } = useTranslation();
  const { role_id } = useParams();
  const id = Number(role_id);
  const { data: role, isLoading, error } = useQuery<Role, Error>({
    queryKey: ['admin-role', id],
    queryFn: () => api.get<Role>(`/api/v1/users/admin/roles/${id}`).then(res => res.data),
  });

  if (isLoading) return <CircularProgress />;
  if (error || !role) return <Alert severity="error">{t('roles.error')}</Alert>;

  return (
    <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t('roles.edit')} {role.name}
      </Typography>
      <EditRoleForm role={role} />
    </Box>
  );
}
