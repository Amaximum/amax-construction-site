# Location Page Master Rule (Single Source of Truth)

This file объединяет все обязательные правила для обновления location pages.

## 1) Content & SEO Strategy Rules

- Use provided reference pages as logic/model only, not as copy template.
- Do not copy paragraphs/sentences/FAQ/conclusions between locations.
- Keep page structure exactly as implemented on target page.
- Do not add/remove/reorder sections.
- Do not change UX flow, existing block layout, or design.
- Do not change internal linking system.
- Do not add/delete/move internal links.
- Do not change anchor text.
- Keep booking forms, CTA blocks, galleries, review widgets, and service cards in place.
- Adapt text to local context (housing types, neighborhood specifics, climate, customer intent).
- Preserve commercial intent and brand tone.

## 2) Keyword Rules (Per Location)

- Build exactly 20 relevant keywords per location.
- Split into:
  - Primary Keywords
  - Secondary Keywords
  - Supporting Keywords
- Integrate keywords naturally across page content.
- No keyword stuffing or meaningless repetition.
- All 20 keywords must be highlighted in bold where requested.

## 3) Title/H1 Rule

- Page title must include current H1 text.
- Recommended format:
  - "{H1} | aMaximum Construction"

## 4) Technical SEO QA Checklist (Required)

Every updated page must pass these checks:

- Page Title
- Meta Description
- Canonical Tag
- H1 Heading
- Heading Hierarchy
- Image Alt Text
- Open Graph Tags
- Twitter Card
- Schema Markup
- FAQ Schema
- Breadcrumb Schema
- robots.txt
- XML Sitemap
- Robots Meta Tag
- llms.txt
- llms.txt Discovery Link
- Viewport Meta
- HTML Lang Attribute
- HTTPS
- Hreflang Tags (optional for single-language site)

## 5) Enforcement in this repo

- Technical checklist validator:
  - `validate_location_page_rules.py`
- Service update scripts currently used:
  - `update_handyman_locations.py`
  - `update_deck_locations.py`

## 6) Run command (example)

```powershell
c:/Users/maxim/Desktop/amax-Construction-site/.venv/Scripts/python.exe .\validate_location_page_rules.py deck-contractor-in-thornhill/index.html
```

A page is acceptable only if summary is PASS.
