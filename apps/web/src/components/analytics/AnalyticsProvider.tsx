'use client';

import React, { useEffect, Suspense } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { pageview, getAnalyticsScript } from '@/lib/analytics';
import Script from 'next/script';

function RouteTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (pathname) {
      const url = searchParams?.toString()
        ? `${pathname}?${searchParams.toString()}`
        : pathname;
      pageview(url);
    }
  }, [pathname, searchParams]);

  return null;
}

export default function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const scriptConfig = getAnalyticsScript();

  // Load custom script configuration for Google Analytics or Plausible
  return (
    <>
      <Suspense fallback={null}>
        <RouteTracker />
      </Suspense>
      {scriptConfig && (
        <Script
          src={scriptConfig.src}
          strategy="afterInteractive"
          {...scriptConfig.attrs}
        />
      )}
      {/* If Google Analytics is loaded, we also need to initialize gtag global array */}
      {process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER === 'ga' && (
        <Script id="ga-init" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_ID || ""}');
          `}
        </Script>
      )}
      {children}
    </>
  );
}
