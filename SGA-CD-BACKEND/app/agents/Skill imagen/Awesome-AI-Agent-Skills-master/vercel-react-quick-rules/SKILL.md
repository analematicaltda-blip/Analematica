---
name: vercel-react-quick-rules
description: Use when a lightweight checklist is needed for React or Next.js performance on Vercel, including data-fetching waterfalls, bundle size, image optimization, streaming, caching, and deployment defaults.
---

# Vercel React Best Practices

Prioritize performance optimization for React and Next.js applications, specifically targeting Vercel deployment environments.

## Core Priorities

1. **Eliminate Waterfalls (Critical)**: Parallelize data fetching.
2. **Bundle Size (Critical)**: Optimize imports and dependencies.
3. **Server Performance (High)**: Efficient use of caching and React Server Components.

## Core Rules

- **async-parallel**: Use `Promise.all` or parallel fetching for independent data.
- **bundle-barrel-imports**: Avoid importing from index/barrel files that pull in unrelated heavy code.
- **server-cache-react**: Use `cache()` from React for request deduplication in Server Components.
- **image-next**: Always use `next/image` with proper `width`, `height`, and `priority` for LCP elements.
- **font-next**: Use `next/font` to optimize font loading and prevent CLS.
- **scripts-next**: Use `next/script` with appropriate strategies (`beforeInteractive`, `afterInteractive`, `lazyOnload`).

## Implementation Workflow

1. Analyze current performance using Core Web Vitals.
2. Identify data fetching waterfalls in `page.tsx` or components.
3. Review `package.json` for heavy or duplicate dependencies.
4. Implement RSC (React Server Components) for data-heavy sections.
5. Apply specific rules from the `rules/` directory (if available) or standard Vercel best practices.

## Validation

- Run `next build` to check bundle sizes.
- Verify that data fetching is parallelized where possible.
- Ensure no client-side-only code is leaking into the server bundle.

