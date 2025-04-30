'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import ClientThemeProvider from './ClientThemeProvider'; 
import EmotionSSRProvider from './emotion-ssr-plugin'; 
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

export default function Providers({ children }: { children: React.ReactNode }) {
  // Используем useState для создания queryClient только один раз на клиенте
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60, // 1 минута
        retry: false, // Не повторять запросы по умолчанию
        refetchOnWindowFocus: false, // Не обновлять при фокусе окна
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {/* Используем EmotionSSRProvider как в исходном layout.tsx */}
      <EmotionSSRProvider>
        <ClientThemeProvider>
          <I18nextProvider i18n={i18n}>
            {children}
          </I18nextProvider>
        </ClientThemeProvider>
      </EmotionSSRProvider>
      {/* Инструменты разработчика React Query (только в режиме разработки) */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
