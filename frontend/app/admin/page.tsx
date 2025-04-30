"use client";

import React from 'react';
import AdminLayout from './layout';
import Link from 'next/link';
import { Button, Box } from '@mui/material';
import { useTranslation } from 'react-i18next';

export default function AdminPage() {
  const { t } = useTranslation();

  return (
    <AdminLayout>
      <Box sx={{ mb: 2 }}>
        <Link href="/user" passHref>
          <Button variant="outlined">{t('admin.back')}</Button>
        </Link>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 300, mt: 4 }}>
        <Link href="/admin/users" passHref>
          <Button variant="contained" fullWidth>{t('admin.users')}</Button>
        </Link>
        <Link href="/admin/devices" passHref>
          <Button variant="contained" fullWidth>{t('admin.devices')}</Button>
        </Link>
        <Link href="/admin/roles" passHref>
          <Button variant="contained" fullWidth>{t('admin.roles')}</Button>
        </Link>
        <Link href="/admin/priorities" passHref>
          <Button variant="contained" fullWidth>{t('admin.priorities')}</Button>
        </Link>
        <Link href="/admin/statuses" passHref>
          <Button variant="contained" fullWidth>{t('admin.statuses')}</Button>
        </Link>
      </Box>
    </AdminLayout>
  );
}
