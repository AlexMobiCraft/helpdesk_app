'use client';

import * as React from 'react';
import { ThemeProvider, CssBaseline, useMediaQuery } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import { useMemo } from 'react';

// Динамическая тема по системной цветовой схеме устройства

export default function ClientThemeProvider({ children }: { children: React.ReactNode }) {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: prefersDarkMode ? 'dark' : 'light',
          primary: { main: '#1976d2' },
          secondary: { main: '#dc004e' },
        },
      }),
    [prefersDarkMode]
  );
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
