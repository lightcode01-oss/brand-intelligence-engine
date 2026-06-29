import type { MetadataRoute } from 'next';
import { getAllPosts } from '@/lib/blog';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://nomen.ai';

  const routes = [
    '',
    '/features',
    '/pricing',
    '/blog',
    '/docs',
    '/about',
    '/contact',
    '/faq',
    '/careers',
    '/privacy',
    '/terms',
    '/cookies',
    '/dmca',
    '/changelog',
    '/status',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  try {
    const posts = await getAllPosts();
    const blogRoutes = posts.map((post) => ({
      url: `${baseUrl}/blog/${post.slug}`,
      lastModified: new Date(post.publishedAt),
      changeFrequency: 'weekly' as const,
      priority: 0.6,
    }));
    return [...routes, ...blogRoutes];
  } catch {
    return routes;
  }
}
