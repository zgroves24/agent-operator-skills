# Google-Oriented SEO Checklist

Use this as a compact decision checklist. Verify current docs when the exact policy matters.

## Crawl And Index

- Important public pages must return `200` without login, geolocation, or client-only rendering requirements.
- `robots.txt` should manage crawl access, not hide private pages from search. Use `noindex` or authentication for private pages.
- Public SEO pages should not be disallowed in `robots.txt`.
- `robots.txt` should point to the canonical sitemap.
- Sitemaps should contain canonical, index-worthy URLs and omit auth, account, API, redirect-only, search-result, and duplicate URLs.
- Canonicals should be absolute, stable, and match the intended index URL.

## Page Quality

- Every indexable page needs a distinct title, meta description, single H1, canonical URL, and meaningful internal links.
- Hub pages should expose crawl paths into generated or deep pages.
- Visible content should satisfy the query without requiring account creation.
- Keep pricing, app availability, dates, and competitor claims fresh.

## Structured Data

- Add only schema that accurately describes visible page content.
- Validate JSON-LD syntax.
- Avoid FAQ markup for ordinary SaaS/product FAQs because FAQ rich results are highly restricted.
- Avoid SoftwareApplication rich-result markup unless real `offers` plus real `aggregateRating` or `review` data are present.
- BreadcrumbList, Organization, WebSite, Article, and ItemList are usually safer than aggressive rich-result schemas.

## Measurement

- After deployment, check Search Console indexing, sitemap ingestion, queries, impressions, CTR, and page-level clicks.
- Tie landing pages to activation metrics in product analytics, not just traffic.
- Prioritize pages with impressions but low CTR, rankings in positions 8-20, and pages with high organic bounce or low signup conversion.
