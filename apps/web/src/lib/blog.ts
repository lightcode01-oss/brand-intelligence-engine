/**
 * Blog content utilities.
 *
 * Reads markdown posts from content/blog/.
 * Extracts frontmatter, calculates reading time, and resolves related posts.
 *
 * Frontmatter schema:
 *   title: string
 *   description: string
 *   author: string
 *   publishedAt: string (ISO date)
 *   tags: string[]
 *   image?: string
 *   featured?: boolean
 */

export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  author: string;
  publishedAt: string;
  tags: string[];
  image: string;
  featured: boolean;
  readingTime: number; // minutes
  content: string;
}

/** Minimal frontmatter parser — no external dependency. */
function parseFrontmatter(raw: string): { data: Record<string, string | boolean | string[]>; content: string } {
  const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!fmMatch) return { data: {}, content: raw };

  const yamlBlock = fmMatch[1];
  const content = fmMatch[2].trim();
  const data: Record<string, string | boolean | string[]> = {};

  for (const line of yamlBlock.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const value = line.slice(colonIdx + 1).trim();

    // Parse array values: [a, b, c]
    if (value.startsWith('[') && value.endsWith(']')) {
      data[key] = value
        .slice(1, -1)
        .split(',')
        .map((v) => v.trim().replace(/['"]/g, ''));
    } else if (value === 'true' || value === 'false') {
      data[key] = value === 'true';
    } else {
      data[key] = value.replace(/^['"]|['"]$/g, '');
    }
  }

  return { data, content };
}

/** Calculates approximate reading time at 200 wpm. */
function calcReadingTime(content: string): number {
  const words = content.trim().split(/\s+/).length;
  return Math.max(1, Math.round(words / 200));
}

import fs from 'fs';
import path from 'path';

/**
 * Returns all blog posts sorted by publishedAt descending.
 * Works in Next.js server components (uses fs).
 */
export async function getAllPosts(): Promise<BlogPost[]> {
  try {
    const blogDir = path.join(process.cwd(), 'content/blog');
    if (fs.existsSync(blogDir)) {
      const files = fs.readdirSync(blogDir);
      const posts: BlogPost[] = [];

      for (const file of files) {
        if (!file.endsWith('.md')) continue;
        const filePath = path.join(blogDir, file);
        const rawContent = fs.readFileSync(filePath, 'utf-8');
        const { data, content } = parseFrontmatter(rawContent);

        posts.push({
          slug: file.replace('.md', ''),
          title: (data.title as string) || '',
          description: (data.description as string) || '',
          author: (data.author as string) || 'Nomen Team',
          publishedAt: (data.publishedAt as string) || new Date().toISOString().split('T')[0],
          tags: (data.tags as string[]) || [],
          image: (data.image as string) || '/blog/placeholder.jpg',
          featured: !!data.featured,
          readingTime: calcReadingTime(content),
          content: content,
        });
      }

      if (posts.length > 0) {
        return posts.sort(
          (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
        );
      }
    }
  } catch (err) {
    console.error('Error reading blog posts from filesystem, falling back to static posts:', err);
  }

  return STATIC_POSTS.sort(
    (a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
  );
}

export async function getPostBySlug(slug: string): Promise<BlogPost | null> {
  try {
    const filePath = path.join(process.cwd(), 'content/blog', `${slug}.md`);
    if (fs.existsSync(filePath)) {
      const rawContent = fs.readFileSync(filePath, 'utf-8');
      const { data, content } = parseFrontmatter(rawContent);
      return {
        slug,
        title: (data.title as string) || '',
        description: (data.description as string) || '',
        author: (data.author as string) || 'Nomen Team',
        publishedAt: (data.publishedAt as string) || new Date().toISOString().split('T')[0],
        tags: (data.tags as string[]) || [],
        image: (data.image as string) || '/blog/placeholder.jpg',
        featured: !!data.featured,
        readingTime: calcReadingTime(content),
        content: content,
      };
    }
  } catch (err) {
    console.error(`Error reading blog post ${slug} from filesystem:`, err);
  }

  return STATIC_POSTS.find((p) => p.slug === slug) ?? null;
}

export async function getRelatedPosts(slug: string, limit = 3): Promise<BlogPost[]> {
  const current = await getPostBySlug(slug);
  if (!current) return [];

  const allPosts = await getAllPosts();
  const others = allPosts.filter((p) => p.slug !== slug);
  const withScore = others.map((p) => ({
    post: p,
    score: p.tags.filter((t) => current.tags.includes(t)).length,
  }));

  return withScore
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((x) => x.post);
}

// ---------------------------------------------------------------------------
// Static blog content — replace with fs-based loader in production
// ---------------------------------------------------------------------------

const STATIC_POSTS: BlogPost[] = [
  {
    slug: 'how-ai-is-revolutionizing-brand-naming',
    title: 'How AI Is Revolutionizing Brand Naming in 2026',
    description:
      'Discover how large language models are transforming the brand discovery process — from weeks of creative workshops to seconds of intelligent generation.',
    author: 'Nomen Team',
    publishedAt: '2026-06-01',
    tags: ['AI', 'Brand Strategy', 'Product'],
    image: '/blog/ai-brand-naming.jpg',
    featured: true,
    readingTime: 7,
    content: `
## The Old Way Was Broken

Building a brand used to start in a conference room. Sticky notes. Whiteboards. Weeks of agency time billed at premium rates. And after all that investment, you still had to run trademark searches manually and hope nothing came back conflicting.

## Enter the Intelligence Layer

Modern brand intelligence platforms like Nomen combine generative AI with real-world data pipelines — trademark databases, domain registrars, social handle availability APIs — into a single coherent workflow.

The result: a brand name candidate that has been scored across linguistic, legal, and digital dimensions before you see it.

## What Makes a Name Good?

Great brand names share measurable characteristics:
- **Pronounceable** in 3+ target languages
- **Memorable** — sub-3 syllable preference
- **Available** — domain + trademark + social handles
- **Distinctive** — low confusion with existing marks

AI excels at generating hundreds of candidates quickly. The intelligence pipeline excels at filtering them down to the handful worth caring about.

## The Nomen Pipeline

Every name generated by Nomen passes through 8 validation stages before reaching your dashboard. Trademark risk is scored. Domain availability is checked live. Social handles are verified. Brand score is computed.

You get a shortlist of names that are actually buildable.

## What's Next

The next frontier is multilingual brand scoring — generating names that work across markets simultaneously, not just the English-speaking world.

This is what we're building at Nomen.
    `.trim(),
  },
  {
    slug: 'domain-availability-guide-2026',
    title: 'The Complete Guide to Domain Availability for Startups',
    description:
      'Everything you need to know about checking domain availability, choosing the right TLD, and building a defensible web presence for your startup.',
    author: 'Nomen Team',
    publishedAt: '2026-05-15',
    tags: ['Domains', 'Startup', 'Guide'],
    image: '/blog/domain-guide.jpg',
    featured: false,
    readingTime: 9,
    content: `
## Why Domain Strategy Matters Early

Your domain is your digital address for the next decade. Getting it wrong early means expensive rebranding, SEO rebuilds, and confused customers.

## TLD Selection

The .com is still king for global B2B and consumer products. But modern startups are successfully launching on .ai, .io, .co, and country-specific TLDs.

Key questions:
- Are you building a global product or a regional one?
- Does your target audience associate .com with credibility?
- Is the .com available at a reasonable price?

## Defensive Registration

Smart founders register multiple TLDs and common misspellings:
- yourname.com (primary)
- yourname.io (redirect)
- yoourname.com (typo redirect)

This prevents competitor squatting and protects brand equity.

## Checking Availability Programmatically

Nomen's domain validation layer checks availability across 50+ TLDs in real time using RDAP and WHOIS protocols, giving you instant clarity on which extensions are available the moment you generate a name.

## Pricing and Acquisition

Premium domains (.com) can cost from $10 to millions. Most new brand names are available in the $10-20/year range. If your preferred .com is taken, consider:
1. Adding a prefix (getbrand.com, usebrand.com, trybrand.com)
2. Choosing an alternative TLD
3. Negotiating acquisition through a domain broker

## Conclusion

Domain availability should be table-stakes in your brand naming process, not an afterthought. With AI-powered tools, you can screen hundreds of candidates against domain availability in seconds.
    `.trim(),
  },
  {
    slug: 'trademark-basics-for-founders',
    title: 'Trademark Basics Every Founder Needs to Know',
    description:
      'A practical primer on trademark registration, why it matters for SaaS companies, common mistakes to avoid, and how to use AI to reduce your legal risk.',
    author: 'Nomen Team',
    publishedAt: '2026-04-22',
    tags: ['Trademark', 'Legal', 'Startup'],
    image: '/blog/trademark-basics.jpg',
    featured: false,
    readingTime: 8,
    content: `
## What Is a Trademark?

A trademark is a legal protection for words, logos, and other identifiers that distinguish your goods and services. It prevents competitors from using confusingly similar marks in your category.

## Why SaaS Companies Get This Wrong

Most founders focus on building product and defer trademark registration. By the time they raise their Series A, they discover:
- A larger competitor holds the mark in their category
- International expansion is blocked by existing registrations
- Rebranding costs exceed the Series A itself

## USPTO vs International

US registration covers the US market. If you plan to expand internationally, you'll need registrations in each target market or an international filing through the Madrid Protocol.

## Nice Classification

Trademarks are categorized by goods/services class (Nice Classification). A mark registered in Class 42 (Software) doesn't protect you in Class 35 (Advertising).

Choose your classes carefully, based on what you're actually building.

## Likelihood of Confusion

The key legal test is "likelihood of confusion" — would consumers confuse your mark with an existing one? Factors include:
- Visual and phonetic similarity
- Relatedness of goods/services
- Strength of the existing mark

## How AI Helps

Nomen's trademark analysis layer queries USPTO TESS and international databases, computes similarity scores, and flags risky names before you invest in building them. This is not legal advice — always consult a trademark attorney — but it dramatically reduces your risk before you engage counsel.

## Next Steps

1. Run a trademark clearance search (Nomen does this for you)
2. Consult a trademark attorney for final clearance
3. File your application as soon as you commit to a name
4. Monitor your mark post-registration for infringers
    `.trim(),
  },
];
