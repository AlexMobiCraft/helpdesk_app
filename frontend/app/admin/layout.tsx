'use client';

import React from 'react';
import { AppBar, Toolbar, Container, Button } from '@mui/material';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();

  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Link href="/admin/roles" passHref>
            <Button color="inherit">{t('roles.title')}</Button>
          </Link>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
