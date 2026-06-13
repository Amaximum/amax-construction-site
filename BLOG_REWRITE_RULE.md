# BLOG REWRITE MASTER RULE (PERMANENT — read before rewriting ANY blog)

Single source of truth for rewriting blog articles to the corporate SEO
standard. Works from any computer (committed to git). When rewriting a blog,
follow EVERY rule below. The reference ("ETALON") blog is:
`avoiding-general-contractor-scams/index.html`.

---

## 0. NON-NEGOTIABLE PRINCIPLES (the user's explicit demands)

1. **UNIQUE content per article.** No templated paragraphs, no copy-paste
   between blogs. Every article is written from scratch for its own topic.
2. **Content MUST match the blog's own URL/slug.** The topic, H1, keywords,
   schema, and examples are derived from the folder name (the URL). A blog at
   `/how-to-repair-wood-decks/` is about repairing wood decks — nothing else.
3. **High SEO quality — act as an SEO specialist.** Search intent first.
   Real keywords, semantic coverage, internal links, clean schema, fast head.
4. **Questions & Answers (FAQ) are MANDATORY.** Every rewritten blog has a
   visible FAQ section (4–6 Q&A) AND matching `FAQPage` JSON-LD schema.
5. **Interesting + genuinely high quality.** Specific numbers, local Ontario/
   Toronto facts, expert tone. No fluff, no keyword stuffing, no filler.

---

## 1. FORMAT DETECTOR (what marks a blog as "done")
`_list_old_blogs.py` flags a blog as NEW format only when ALL are present:
- `class="lede"`  — opening hook paragraph
- `key-takeaways` — the Key Takeaways aside
- `"HowTo"`       — HowTo JSON-LD schema

A fully rewritten blog ALSO adds an `FAQPage` schema + visible FAQ (rule 0.4).

---

## 2. HEAD / SEO (per article, derived from the slug)
- `<title>` ≤ ~60 chars, includes the year + brand (`... | aMaximum`).
- `meta description` — concrete, fact-rich, ≤ ~160 chars, topic-specific.
- `canonical` → the www URL of THIS blog's slug.
- JSON-LD `@graph` containing:
  - `BlogPosting`: headline, datePublished (keep original), dateModified
    (today), author = Organization aMaximum, publisher + logo, description,
    `about[]` (2–3 Things from the topic), `areaServed` (City, usually Toronto).
  - `HowTo`: name, description, `step[]` with position/name/text (real steps
    specific to THIS topic).
  - `FAQPage`: `mainEntity[]` of Question → acceptedAnswer, **matching the
    visible FAQ section word-for-word**.
  - `BreadcrumbList`: Home → Blog → article headline.
- OG tags (`og:type=article`, og:title/description/url, og:image 1200×800 with
  alt) + Twitter `summary_large_image`.

## 3. BODY STRUCTURE (in order)
1. `blog-hero`: `article-meta` (category, "Updated <date>", "N min read") +
   `<h1>` (topic from slug) + intro paragraph with a **real statistic/number**.
2. `<p class="lede">` — italic hook that frames the problem + the local angle.
3. `<aside class="key-takeaways">` — "Key Takeaways", 4–5 bullets, each with
   concrete numbers / laws / standards (not vague advice).
4. `<nav class="toc">` — table of contents with anchor links.
5. `<h2 id="...">` sections matching the TOC anchors. Use **bold lead-ins**,
   real prices/percentages/timelines, Ontario/Toronto specifics.
6. Where useful: `comparison-table` and `callout callout-stat` (a highlighted
   fact/rule).
7. **FAQ section (MANDATORY):** `<section class="faq">` (or equivalent) with
   4–6 `<h3>` questions + answers. Mirror these exactly in `FAQPage` schema.
8. `author-block` — "Written by … editorial team", "Reviewed for accuracy by
   …", disclaimer (not legal/professional advice). E-E-A-T signal.
9. `sources` — authoritative references (ontario.ca, statutes, WSIB, ESA, BBB,
   City of Toronto) with `rel="noopener nofollow"`.
10. `article-cta` — topic-matched CTA + button to the correct one of the 18
    `book-<service>.html` forms.
11. Keep `<!-- BLOG_CTA_INJECTED -->` marker + the Related Service block.

## 4. CONTENT PRINCIPLES
- Localize to Toronto/GTA; cite Ontario law where relevant (CPA, Construction
  Act, ESA, WSIB, OBC, City permits).
- Concrete numbers, costs, percentages, timelines — never generic filler.
- Unique angle per slug; no shared boilerplate between articles.
- Navbar BOOK NOW → the correct one of the 18 forms for the article's topic.
- Tone: expert, helpful, corporate — like a senior SEO + a tradesperson wrote it.

## 5. WORKFLOW
- Sync first (`git fetch` / `git pull --ff-only`) per repo workflow rule.
- Rewrite in batches; after each batch run `_list_old_blogs.py` to confirm the
  blog moved to NEW format, then `git add -A && git commit && git push`.

## 6. VALIDATION & PROGRESS TRACKING
- Per-article QA: `python _blog_qa2.py <slug>` — checks JSON-LD @types, H2 ids
  vs TOC anchors, mojibake, body word count, book CTA href, title length, and
  the flags (key-takeaways / toc / author-block / sources / callouts).
- The per-blog → correct `/book-<service>.html` mapping + the full checklist of
  which blogs are done vs remaining lives in `BLOG_REWRITE_PROGRESS.md`
  (keep it updated as blogs are completed).
- **Banned AI-filler phrases** (QA flags these — never use): "In this article",
  "Let's dive in", "In conclusion", "It's important to note", "Stay tuned",
  "navigate the complexities", "delve into", "in today's fast-paced",
  "Whether you're a homeowner", "When it comes to".
