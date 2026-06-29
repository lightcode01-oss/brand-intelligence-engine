import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Section } from '@/components/marketing/Section';
import { BlogCard } from '@/components/marketing/BlogCard';
import { getPostBySlug, getRelatedPosts, getAllPosts } from '@/lib/blog';
import { generateSEO, breadcrumbSchema } from '@/lib/seo';
import { Calendar, Clock, ArrowLeft } from 'lucide-react';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPostBySlug(slug);
  if (!post) return {};
  return generateSEO({
    title: post.title,
    description: post.description,
    keywords: post.tags,
    path: `/blog/${slug}`,
    type: 'article',
    publishedAt: post.publishedAt,
    author: post.author,
  });
}

// Next.js static generation
export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);
  if (!post) {
    notFound();
  }

  const relatedPosts = await getRelatedPosts(slug, 3);

  const formattedDate = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(post.publishedAt));

  const jsonLd = breadcrumbSchema([
    { name: 'Home', url: '/' },
    { name: 'Blog', url: '/blog' },
    { name: post.title, url: `/blog/${post.slug}` },
  ]);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Section className="pt-32" narrow>
        <div className="mb-8">
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-600 hover:text-indigo-700"
          >
            <ArrowLeft size={16} />
            Back to publications
          </Link>
        </div>

        <article className="space-y-6">
          <header className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700"
                >
                  {tag}
                </span>
              ))}
            </div>

            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
              {post.title}
            </h1>

            <p className="text-lg text-slate-500 leading-relaxed font-medium">
              {post.description}
            </p>

            <div className="flex items-center gap-6 border-y border-slate-100 py-4 text-sm text-slate-400">
              <span className="font-semibold text-slate-700">{post.author}</span>
              <span className="flex items-center gap-1.5">
                <Calendar size={14} />
                <time dateTime={post.publishedAt}>{formattedDate}</time>
              </span>
              <span className="flex items-center gap-1.5">
                <Clock size={14} />
                {post.readingTime} min read
              </span>
            </div>
          </header>

          {/* Simple Markdown Render using styled typography blocks */}
          <div className="text-slate-700 leading-relaxed space-y-6 pt-4 text-base md:text-lg">
            {post.content.split('\n\n').map((paragraph, idx) => {
              if (paragraph.startsWith('## ')) {
                return (
                  <h2 key={idx} className="text-2xl font-bold text-slate-900 pt-6 pb-2">
                    {paragraph.replace('## ', '')}
                  </h2>
                );
              }
              if (paragraph.startsWith('### ')) {
                return (
                  <h3 key={idx} className="text-xl font-bold text-slate-900 pt-4 pb-1">
                    {paragraph.replace('### ', '')}
                  </h3>
                );
              }
              if (paragraph.startsWith('- ')) {
                return (
                  <ul key={idx} className="list-disc pl-6 space-y-2 py-2" role="list">
                    {paragraph.split('\n').map((li, lIdx) => (
                      <li key={lIdx}>{li.replace('- ', '')}</li>
                    ))}
                  </ul>
                );
              }
              return <p key={idx}>{paragraph}</p>;
            })}
          </div>
        </article>
      </Section>

      {/* Related articles */}
      {relatedPosts.length > 0 && (
        <section className="bg-slate-50 py-16 border-t border-slate-200" aria-label="Related Publications">
          <div className="mx-auto max-w-7xl px-6">
            <h2 className="text-2xl font-bold text-slate-900 mb-8">Related publications</h2>
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {relatedPosts.map((rPost) => (
                <BlogCard key={rPost.slug} post={rPost} />
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  );
}
