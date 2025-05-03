'use client';

import React from 'react';
import { AppBar, Container } from '@mui/material';
import { useTranslation } from 'react-i18next';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation();

  return (
    <>
      <AppBar position="static" color="primary">
        {/* Навигационные кнопки удалены */}
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
