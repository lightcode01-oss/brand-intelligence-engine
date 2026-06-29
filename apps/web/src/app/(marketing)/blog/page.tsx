import type { Metadata } from 'next';
import React from 'react';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { BlogCard } from '@/components/marketing/BlogCard';
import { getAllPosts } from '@/lib/blog';
import { generateSEO } from '@/lib/seo';

export const metadata: Metadata = generateSEO({
  title: 'Blog',
  description:
    'Read our latest insights, tutorials, and guides about brand strategy, naming principles, domain acquisition, and startup legal advice.',
  keywords: ['nomen blog', 'brand naming tips', 'domain strategy articles', 'startup naming resources'],
  path: '/blog',
});

export default async function BlogPage() {
  const posts = await getAllPosts();
  const featuredPost = posts.find((p) => p.featured) || posts[0];
  const regularPosts = posts.filter((p) => p.slug !== featuredPost?.slug);

  return (
    <Section className="pt-32">
      <SectionHeading
        eyebrow="Nomen Journal"
        title="Insights for brand builders"
        description="Thoughtful writing on naming, trademarks, domain strategy, and startup brand growth."
      />

      {/* Featured post */}
      {featuredPost && (
        <div className="mb-16">
          <h2 className="mb-6 text-xs font-semibold uppercase tracking-widest text-slate-400">
            Featured Article
          </h2>
          <BlogCard post={featuredPost} featured={true} className="w-full" />
        </div>
      )}

      {/* Regular posts */}
      <div>
        <h2 className="mb-6 text-xs font-semibold uppercase tracking-widest text-slate-400">
          Latest Publications
        </h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {regularPosts.map((post) => (
            <BlogCard key={post.slug} post={post} />
          ))}
        </div>
      </div>
    </Section>
  );
}
