'use client';

import React from 'react';
import { AppBar, Container, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();

  return (
    <>
      <AppBar position="static" color="primary">
        <Link href="/admin/priorities" passHref>
          <Button color="inherit">{t('admin.priorities')}</Button>
        </Link>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
