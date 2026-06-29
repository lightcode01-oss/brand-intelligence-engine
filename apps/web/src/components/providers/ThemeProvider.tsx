'use client';

import React, { useEffect } from 'react';
import { useThemeStore } from '@/store/themeStore';

export default function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { setTheme } = useThemeStore();

  useEffect(() => {
    // Read theme preference from local storage
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme_preference') as 'light' | 'dark' | 'system' | null;
      if (stored) {
        setTheme(stored);
      } else {
        setTheme('system');
      }
    }
  }, [setTheme]);

  return <>{children}</>;
}
