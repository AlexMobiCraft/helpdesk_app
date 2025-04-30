'use client';

import React from 'react';
import { AppBar, Toolbar, Container } from '@mui/material';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AppBar position="static" color="primary">
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
