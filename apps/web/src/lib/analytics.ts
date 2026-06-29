/**
 * Analytics provider abstraction.
 *
 * Supports Google Analytics, Plausible, and PostHog.
 * Provider is driven entirely by environment variables — no IDs in source code.
 *
 * Usage:
 *   import { track } from '@/lib/analytics';
 *   track('signup_button_clicked', { plan: 'pro' });
 */

export type AnalyticsProvider = 'ga' | 'plausible' | 'posthog' | 'none';

declare global {
  interface Window {
    gtag?: (event: string, action: string, properties?: Record<string, unknown>) => void;
    plausible?: (event: string, properties?: { props?: Record<string, unknown> } | string) => void;
    posthog?: {
      capture: (event: string, properties?: Record<string, unknown>) => void;
      identify: (userId: string, traits?: Record<string, string>) => void;
    };
  }
}

const provider = (process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER || 'none') as AnalyticsProvider;

interface EventProperties {
  [key: string]: string | number | boolean | undefined;
}

/** Track a named event with optional properties. */
export function track(event: string, properties?: EventProperties): void {
  if (typeof window === 'undefined') return;

  const props = properties as Record<string, unknown> | undefined;

  switch (provider) {
    case 'ga':
      if (typeof window.gtag === 'function') {
        window.gtag('event', event, props);
      }
      break;

    case 'plausible':
      if (typeof window.plausible === 'function') {
        window.plausible(event, { props });
      }
      break;

    case 'posthog':
      if (typeof window.posthog !== 'undefined') {
        window.posthog.capture(event, props);
      }
      break;

    case 'none':
    default:
      if (process.env.NODE_ENV === 'development') {
        console.debug('[Analytics]', event, properties);
      }
  }
}

/** Identify a logged-in user. */
export function identify(userId: string, traits?: Record<string, string>): void {
  if (typeof window === 'undefined') return;

  switch (provider) {
    case 'posthog':
      if (typeof window.posthog !== 'undefined') {
        window.posthog.identify(userId, traits);
      }
      break;
    case 'none':
    default:
      if (process.env.NODE_ENV === 'development') {
        console.debug('[Analytics.identify]', userId, traits);
      }
  }
}

/** Track a page view manually (for SPAs). */
export function pageview(url: string): void {
  if (typeof window === 'undefined') return;

  switch (provider) {
    case 'ga':
      if (typeof window.gtag === 'function') {
        window.gtag('config', process.env.NEXT_PUBLIC_GA_ID || '', { page_path: url } as Record<string, unknown>);
      }
      break;
    case 'plausible':
      if (typeof window.plausible === 'function') {
        window.plausible('pageview');
      }
      break;
    case 'posthog':
      if (typeof window.posthog !== 'undefined') {
        window.posthog.capture('$pageview', { url } as Record<string, unknown>);
      }
      break;
    default:
      break;
  }
}

/** Returns the analytics head script for the configured provider. */
export function getAnalyticsScript(): { src: string; attrs: Record<string, string> } | null {
  switch (provider) {
    case 'ga':
      return {
        src: `https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`,
        attrs: { async: 'true' },
      };
    case 'plausible':
      return {
        src: 'https://plausible.io/js/script.js',
        attrs: { defer: 'true', 'data-domain': process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN || '' },
      };
    case 'posthog':
      return null; // PostHog initialises via SDK in AnalyticsProvider component
    default:
      return null;
  }
}
