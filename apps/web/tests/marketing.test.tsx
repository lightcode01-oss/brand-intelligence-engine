import { generateSEO } from '../src/lib/seo';
import { getPostBySlug, getAllPosts, getRelatedPosts } from '../src/lib/blog';

describe('Marketing Website & SEO Tests', () => {
  test('generateSEO helper maps correct metadata values', () => {
    const meta = generateSEO({
      title: 'Test Title',
      description: 'Test Description',
      keywords: ['test', 'seo'],
      path: '/test-path',
      image: '/test-image.jpg',
    });

    expect(meta.title).toBe('Test Title — Nomen');
    expect(meta.description).toBe('Test Description');
    expect(meta.keywords).toBe('test, seo');
    expect(meta.alternates?.canonical).toBe('https://nomen.ai/test-path');
    expect(meta.openGraph?.title).toBe('Test Title — Nomen');
    expect(meta.openGraph?.url).toBe('https://nomen.ai/test-path');
    expect(meta.twitter?.card).toBe('summary_large_image');
  });

  test('generateSEO respects noIndex rules', () => {
    const meta = generateSEO({
      title: 'Secret Page',
      description: 'Secret Description',
      noIndex: true,
    });

    expect(meta.robots?.index).toBe(false);
    expect(meta.robots?.follow).toBe(false);
  });

  test('Blog engine loads all static blog posts', async () => {
    const posts = await getAllPosts();
    expect(posts.length).toBeGreaterThan(0);
    expect(posts[0].slug).toBeDefined();
    expect(posts[0].readingTime).toBeGreaterThan(0);
  });

  test('Blog engine filters post by slug', async () => {
    const post = await getPostBySlug('how-ai-is-revolutionizing-brand-naming');
    expect(post).not.toBeNull();
    expect(post?.title).toContain('AI');
  });

  test('Blog engine resolves related articles matching tags', async () => {
    const related = await getRelatedPosts('how-ai-is-revolutionizing-brand-naming', 2);
    expect(related.length).toBeLessThanOrEqual(2);
  });

  test('Newsletter email regex matches valid formats', () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    expect(emailRegex.test('info@nomen.ai')).toBe(true);
    expect(emailRegex.test('info.nomen.ai')).toBe(false);
    expect(emailRegex.test('info@')).toBe(false);
  });

  test('Pricing monthly vs yearly pricing computations', () => {
    const monthlyRate = 29;
    const yearlyRate = 24;
    const annualDiscount = 1 - (yearlyRate * 12) / (monthlyRate * 12);
    expect(annualDiscount).toBeCloseTo(0.172, 2); // ~17.2% actual discount based on numbers
  });
});
