'use client';

import React from 'react';
import AdminLayout from '../../../layout';
import { useTranslation } from 'react-i18next';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import EditPriorityForm from './EditPriorityForm';

interface Priority {
  id: number;
  name: string;
  description?: string;
  display_order: number;
}

/**
 * Шаг 7: Страница редактирования приоритета
 */
export default function EditPriorityPage() {
  const { t } = useTranslation();
  const { priority_id } = useParams();
  const id = Number(priority_id);
  if (isNaN(id)) {
    return (
      <AdminLayout>
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{t('priorities.error')}</Alert>
        </Box>
      </AdminLayout>
    );
  }
  const { data: priority, isLoading, error } = useQuery<Priority>({
    queryKey: ['admin-priority', id],
    queryFn: () =>
      api
        .get<{ priority_id: number; name: string; description?: string; display_order: number }>(
          `/api/v1/priorities/admin/priorities/${id}`
        )
        .then(res => ({
          id: res.data.priority_id,
          name: res.data.name,
          description: res.data.description,
          display_order: res.data.display_order,
        })),
    enabled: !isNaN(id),
  });

  if (isLoading) return <CircularProgress />;
  if (error || !priority) return <Alert severity="error">{t('priorities.error')}</Alert>;

  return (
    <AdminLayout>
      <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
        <Typography variant="h5" gutterBottom>
          {t('priorities.edit')} {priority.name}
        </Typography>
        <EditPriorityForm priority={priority} />
      </Box>
    </AdminLayout>
  );
}
