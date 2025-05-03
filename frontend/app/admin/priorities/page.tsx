'use client';

import React, { useState } from 'react';
import AdminLayout from '../layout';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import Link from 'next/link';
import PriorityList from './PriorityList';

/**
 * Страница списка приоритетов с пагинацией
 */
export default function AdminPrioritiesPage() {
  const { t } = useTranslation();
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const { data: priorities, isLoading, error } = useQuery({
    queryKey: ['admin-priorities', skip],
    queryFn: () =>
      api
        .get('/api/v1/priorities/admin/priorities', { params: { skip, limit } })
        .then(res =>
          res.data.map((p: any) => ({
            id: p.priority_id,
            name: p.name,
            description: p.description,
            display_order: p.display_order,
          }))
        ),
  });

  return (
    <AdminLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <Link href="/admin" passHref>
            <Button variant="outlined">{t('admin.back')}</Button>
          </Link>
          <Link href="/admin/priorities/new" passHref>
            <Button variant="contained" color="primary">{t('priorities.new')}</Button>
          </Link>
        </Box>
        <Typography variant="h4" gutterBottom>
          {t('priorities.title')}
        </Typography>
        {isLoading && <CircularProgress />}
        {error && <Alert severity="error">{t('priorities.error')}</Alert>}
        {priorities && (
          <>
            <PriorityList priorities={priorities} />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                disabled={skip === 0}
                onClick={() => setSkip(Math.max(0, skip - limit))}
              >
                Prev
              </Button>
              <Button
                variant="outlined"
                disabled={priorities.length < limit}
                onClick={() => setSkip(skip + limit)}
              >
                Next
              </Button>
            </Box>
          </>
        )}
      </Box>
    </AdminLayout>
  );
}
