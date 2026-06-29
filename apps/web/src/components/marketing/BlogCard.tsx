import React from 'react';
import Link from 'next/link';
import { Calendar, Clock, ArrowRight } from 'lucide-react';
import { BlogPost } from '@/lib/blog';
import { cn } from '@/lib/utils/cn';

interface BlogCardProps {
  post: BlogPost;
  featured?: boolean;
  className?: string;
}

export function BlogCard({ post, featured = false, className }: BlogCardProps) {
  const formattedDate = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(post.publishedAt));

  return (
    <article
      className={cn(
        'group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-md',
        featured ? 'md:flex' : '',
        className
      )}
    >
      {/* Cover image placeholder */}
      <div
        className={cn(
          'bg-gradient-to-br from-indigo-100 to-violet-100',
          featured ? 'md:w-2/5 md:flex-shrink-0' : 'aspect-[16/9] w-full'
        )}
        aria-hidden="true"
      >
        <div className="flex h-full min-h-[180px] items-center justify-center">
          <div className="text-5xl font-black text-indigo-200 select-none">
            {post.title.charAt(0)}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col p-6">
        {/* Tags */}
        <div className="mb-3 flex flex-wrap gap-2">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h3 className={cn('font-bold leading-tight text-slate-900 group-hover:text-indigo-600 transition-colors', featured ? 'text-2xl' : 'text-lg')}>
          <Link href={`/blog/${post.slug}`} className="after:absolute after:inset-0">
            {post.title}
          </Link>
        </h3>

        {/* Description */}
        <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-500 line-clamp-3">
          {post.description}
        </p>

        {/* Meta */}
        <div className="mt-4 flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Calendar size={12} aria-hidden="true" />
            <time dateTime={post.publishedAt}>{formattedDate}</time>
          </span>
          <span className="flex items-center gap-1">
            <Clock size={12} aria-hidden="true" />
            {post.readingTime} min read
          </span>
        </div>

        {/* Author + Read link */}
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs font-medium text-slate-600">{post.author}</span>
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600">
            Read more
            <ArrowRight size={12} />
          </span>
        </div>
      </div>
    </article>
  );
}
