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

## 7) ETALON-Based Keyword Rollout Workflow (PERMANENT RULE)

Это правило закоммичено в git, поэтому доступно с ЛЮБОГО компьютера
пользователя после `git pull`.

### Что просит пользователь (дословно)
"Я даю тебе ЭТАЛОН страницу, на которую ты опираешься, и прописываешь все
остальные location по этому services, собирая keywords."

### Процедура
1. Пользователь указывает ОДИН сервис + ОДНУ location-страницу как ЭТАЛОН
   (reference). Эталон = логика/модель структуры, НЕ шаблон для копипаста.
2. Для КАЖДОЙ остальной location-страницы того же сервиса:
   - Собрать ровно **20 keywords**, разбитых на: **Primary / Secondary /
     Supporting**.
   - Вписать естественно в контент (no stuffing, no повтор).
   - Все 20 keywords выделить **bold** где требуется.
   - Адаптировать под локальный контекст (тип жилья, район, климат, intent).
3. Соблюдать ВСЕ правила разделов 1–4 выше (структура, internal links,
   anchor text, формы, CTA, галереи, review-виджеты, service cards не
   трогать; контент каждой локации уникален; title включает H1).
4. Прогнать `validate_location_page_rules.py` — страница принимается
   только при summary PASS.

### Уже выполнено (git history)
- Handyman locations — 20-keyword clusters + title-h1 (888258c0, 58c2d1f6)
- Deck locations — keyword clusters + title-h1 (b3304c51)
- Fence locations — master rules, КРОМЕ Richmond Hill (5ebdb6a6)
- Plumbing locations — rollout (632c389d)

### Ещё НЕ сделано (кандидаты на продолжение)
basement-renovation, carpenter-services, demolition, general-contractor,
home-renovation, interlocking-stone, electrical, excavation, painting,
canopy, deck-railing, christmas-lights.
