'use client';

import React, { useState } from 'react';
import AdminLayout from '../layout';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import Link from 'next/link';
import StatusList from './StatusList';

export default function AdminStatusesPage() {
  const { t } = useTranslation();
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const { data: statuses, isLoading, error } = useQuery({
    queryKey: ['admin-statuses', skip],
    queryFn: () =>
      api.get('/api/v1/statuses/admin/statuses', { params: { skip, limit } })
        .then(res =>
          res.data.map((s: any) => ({ id: s.status_id, name: s.name, description: s.description })),
        ),
  });

  return (
    <AdminLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <Link href="/admin" passHref>
            <Button variant="outlined">{t('admin.back')}</Button>
          </Link>
          <Link href="/admin/statuses/new" passHref>
            <Button variant="contained" color="primary">{t('statuses.new')}</Button>
          </Link>
        </Box>
        <Typography variant="h4" gutterBottom>{t('statuses.title')}</Typography>
        {isLoading && <CircularProgress />}
        {error && <Alert severity="error">{t('statuses.error')}</Alert>}
        {statuses && (
          <>
            <StatusList statuses={statuses} />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button variant="outlined" disabled={skip===0} onClick={()=>setSkip(Math.max(0, skip-limit))}>Prev</Button>
              <Button variant="outlined" disabled={statuses.length<limit} onClick={()=>setSkip(skip+limit)}>Next</Button>
            </Box>
          </>
        )}
      </Box>
    </AdminLayout>
  );
}
