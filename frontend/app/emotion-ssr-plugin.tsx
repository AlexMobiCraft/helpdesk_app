'use client';
import * as React from 'react';
import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';

export function useEmotionCache() {
  const cache = React.useMemo(
    () => createCache({ key: 'mui', prepend: true }),
    []
  );
  return cache;
}

export default function EmotionSSRProvider({ children }: { children: React.ReactNode }) {
  const cache = useEmotionCache();
  return <CacheProvider value={cache}>{children}</CacheProvider>;
}
