# robots.txt audit · pre-launch

Date · 28 April 2026
Scope · `/public/robots.txt` for the 1 June 2026 static launch on Vercel
File · `public/robots.txt`

---

## 1. Old vs new (high-level diff)

| Area | Before | After |
|---|---|---|
| Header | "Production robots.txt" only | Adds `Last updated: 2026-04-28` for ops traceability |
| Dashboard disallow | `/dashboard-cliente`, `/es/dashboard-cliente`, `/usuaris`, `/es/usuarios` | Same set retained; verified each path exists in `public/` |
| WordPress legacy | 6 entries | Same 6 entries (kept; defensive) |
| Tracking params | `s`, `p`, `utm_`, `ref`, `fbclid`, `gclid` | Same six, normalised with trailing `*` on `fbclid`/`gclid`/`utm_` for parameter-suffix matching |
| Internal/test files | (none) | Adds `/_test_dir.txt`, `/serve.py`, `/serve_preview.py`, `/dashboard-guard.js` |
| Asset allow-list | `/css/`, `/js/`, `/img/`, `/fonts/` | Unchanged |
| Per-bot crawl-delay | Single global `Crawl-delay: 1` | Removed global delay (most engines now use Search Console throttling); explicit `Crawl-delay: 5` for AhrefsBot, SemrushBot, MJ12bot |
| AI scrapers | (none) | 9 explicit `Disallow: /` blocks (GPTBot, ChatGPT-User, anthropic-ai, ClaudeBot, PerplexityBot, CCBot, Bytespider, Google-Extended) |
| Sitemap | `https://papik.cat/sitemap.xml` | Same · verified file exists at `public/sitemap.xml` and resolves under the production hostname declared in CLAUDE.md and `vercel.json` |

---

## 2. Paths from the proposed template that were dropped

The brief proposed several paths that do not exist in this repo. Per the user's instruction ("don't disallow paths that don't exist"), they were omitted to keep the file clean and signal intent accurately:

- `/dashboard-admin` · not present
- `/dashboard-arquitecto` · not present
- `/dashboard-empleado` · not present
- `/dashboard-secretario` · not present
- `/api/` · not present (the static build has no Vercel serverless functions; forms backend is external)
- `/_t.html` · not present (only `_test_dir.txt` exists)
- `/assets/` · not present (assets live under `/css`, `/js`, `/img`, `/fonts`)

If any of these are added later (e.g., a Vercel function for forms, or new dashboard roles), the corresponding `Disallow` lines should be re-added at the same time.

## 3. Paths added beyond the template

Verified to exist in `public/` and worth blocking:

- `/_test_dir.txt` · sentinel file
- `/serve.py`, `/serve_preview.py` · local dev scripts shipped to public/
- `/dashboard-guard.js` · client-side auth gate (not a page, but listed defensively to prevent indexing as a JS resource snippet in some engines)

## 4. Rationale · AI scraper blocks

PAPIK has shipped ~95.000 words of editorial copy across CA + ES + EN, including the `/patrimonis` and financial-article content where the brand voice and Eskimohaus® positioning constitute commercial IP. Rationale per agent:

- **GPTBot** (OpenAI) · primary training crawler for GPT models
- **ChatGPT-User** (OpenAI) · live retrieval agent invoked by ChatGPT browsing tools
- **anthropic-ai**, **ClaudeBot** · Anthropic crawlers; both names are honoured per their docs
- **PerplexityBot** · Perplexity AI search/training
- **CCBot** · Common Crawl, the corpus most foundation models train on
- **Bytespider** · ByteDance / Doubao
- **Google-Extended** · Google's training opt-out token (separate from Googlebot, which we want for Search)

Note · `Google-Extended` opts out of Bard/Gemini training **without** affecting Search visibility. This was added beyond the brief because PAPIK's positioning depends on organic Search visibility and explicitly should not block Googlebot itself.

## 5. Unusual decisions

1. **Removed the global `Crawl-delay: 1`** · Google ignores it, Bing now negotiates via Bing Webmaster Tools, and a `1` directive on a static site amounts to noise. Replaced with explicit `5s` delays for the three SEO-tool crawlers (Ahrefs, Semrush, MJ12) that historically generate the most non-revenue traffic on small business sites.

2. **Did not block `xmlrpc.php` or `/?author=` again** · already covered by the WordPress legacy block; kept for defence-in-depth even though the static site has no PHP runtime.

3. **`Sitemap` is declared once** · only `sitemap.xml` exists at `public/sitemap.xml`. If a `sitemap-images.xml` is added later, declare it as a second `Sitemap:` line.

4. **No `Host:` directive** · non-standard, ignored by Googlebot; canonical hostname is enforced via `vercel.json` redirects.

5. **No locale-specific blocks for `/en/`** · the EN tree mirrors the CA root and contains no dashboards or admin paths (verified). No additional disallows needed.

---

## 6. Post-launch verification checklist

- T-0 · Fetch `https://papik.cat/robots.txt` and diff against this file
- T-0 · Submit `https://papik.cat/sitemap.xml` in Google Search Console
- T+1 · Run Search Console "robots.txt Tester" against five sample URLs (homepage, an article, `/pressupost`, `/dashboard-cliente`, `/wp-admin/`)
- T+7 · Confirm zero AI-scraper hits in Vercel Analytics under the blocked user-agents
