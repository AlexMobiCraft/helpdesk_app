'use client';

import React from 'react';
import { Container } from '@mui/material';
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
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {children}
      </Container>
    </>
  );
}
