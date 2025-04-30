"use client";
import * as React from "react";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

// Кэш с уникальным ключом для клиентских стилей
const muiCache = createCache({ key: "mui", prepend: true });

export default function EmotionCacheProvider({ children }: { children: React.ReactNode }) {
  return <CacheProvider value={muiCache}>{children}</CacheProvider>;
}
