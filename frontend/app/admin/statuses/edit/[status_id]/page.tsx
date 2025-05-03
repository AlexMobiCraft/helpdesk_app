'use client';

import React from 'react';
import AdminLayout from '../../../layout';
import { useTranslation } from 'react-i18next';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import {
  Box, Typography, CircularProgress, Alert
} from '@mui/material';
import EditStatusForm from './EditStatusForm';

interface Status { id: number; name: string; description?: string }

/**
 * Страница редактирования статуса
 */
export default function EditStatusPage() {
  const { t } = useTranslation();
  const { status_id } = useParams();
  const id = Number(status_id);
  if (isNaN(id)) {
    return (
      <AdminLayout>
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{t('statuses.error')}</Alert>
        </Box>
      </AdminLayout>
    );
  }
  const { data: status, isLoading, error } = useQuery<Status>({
    queryKey: ['admin-status', id],
    queryFn: () =>
      api
        .get<{ status_id: number; name: string; description?: string }>(
          `/api/v1/statuses/admin/statuses/${id}`,
        )
        .then(r => {
          const s = r.data;
          return { id: s.status_id, name: s.name, description: s.description };
        }),
    enabled: !isNaN(id),
  });

  if (isLoading) return <CircularProgress />;
  if (error || !status) return <Alert severity="error">{t('statuses.error')}</Alert>;

  return (
    <AdminLayout>
      <Box sx={{ mt: 4, mx: 'auto', maxWidth: 600 }}>
        <Typography variant="h5" gutterBottom>
          {t('statuses.edit')} {status.name}
        </Typography>
        <EditStatusForm status={status} />
      </Box>
    </AdminLayout>
  );
}
