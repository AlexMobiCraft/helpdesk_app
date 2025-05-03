'use client';

import React, { useState } from 'react';
import AdminLayout from '../layout';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import Link from 'next/link';
import RoleList from './RoleList';

/**
 * Страница списка ролей с пагинацией
 */
export default function AdminRolesPage() {
  const { t } = useTranslation();
  const [skip, setSkip] = useState(0);
  const limit = 10;
  const { data: roles, isLoading, error } = useQuery({
    queryKey: ['admin-roles', skip],
    queryFn: () =>
      api
        .get('/api/v1/users/admin/roles', { params: { skip, limit } })
        .then(res => res.data),
  });

  return (
    <AdminLayout>
      <Box sx={{ mt: 4 }}>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <Link href="/admin" passHref>
            <Button variant="outlined">{t('admin.back')}</Button>
          </Link>
          <Link href="/admin/roles/new" passHref>
            <Button variant="contained" color="primary">{t('roles.new')}</Button>
          </Link>
        </Box>
        <Typography variant="h4" gutterBottom>
          {t('roles.title')}
        </Typography>
        {isLoading && <CircularProgress />}
        {error && <Alert severity="error">{t('roles.error')}</Alert>}
        {roles && (
          <>
            <RoleList roles={roles} />
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
                disabled={roles.length < limit}
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
