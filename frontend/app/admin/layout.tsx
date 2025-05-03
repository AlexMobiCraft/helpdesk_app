'use client';

import React from 'react';
import { AppBar, Container, Button } from '@mui/material';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';

const LinkComponent = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <Link href={href} passHref>
    {children}
  </Link>
);

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();

  return (
    <>
      <AppBar position="static" color="primary">
          <LinkComponent href="/admin/roles">
            <Button color="inherit">{t('admin.roles')}</Button>
          </LinkComponent>
          <LinkComponent href="/admin/statuses">
            <Button color="inherit">{t('admin.statuses')}</Button>
          </LinkComponent>
          <LinkComponent href="/admin/users">
            <Button color="inherit">{t('admin.users')}</Button>
          </LinkComponent>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
