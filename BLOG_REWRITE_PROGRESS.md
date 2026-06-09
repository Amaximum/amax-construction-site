# Прогресс переписывания блогов в новый SEO-формат

Чеклист обновляется по мере работы. Файл лежит в репо — после `git pull`
на любом компьютере видно актуальное состояние.

## Структура нового формата (10 обязательных блоков на статью)

1. `<title>` ≤ 60 символов + уникальный H1
2. `<p class="lede">` — 50–80 слов, ключевик в первых 100 символах
3. `<aside class="key-takeaways">` — 4–6 буллетов
4. `<nav class="toc">` — якоря совпадают с id у H2
5. 6–10 секций H2 с `id`
6. Локальный контекст Toronto (климат, цены CAD, OBC, Tarion/ESA где применимо)
7. HowTo-схема с 5 шагами в `@graph` JSON-LD
8. Сравнительная таблица или callout-stat
9. FAQ-стиль внутри article-body (отдельный `id="faq"` блок не трогаем)
10. `<aside class="author-block">` + `<section class="sources">` + `<div class="article-cta">` с `/book-X.html`

Плюс: BlogPosting + HowTo + BreadcrumbList в `@graph`, og:type=article,
`dateModified=2026-06-08`, CSS cache `?v=20260606a`.

## Готово (8 верхнеуровневых статей в новом формате)

- [x] 3-easy-ways-to-care-for-your-deck-so-it-always-looks-great (Batch 1)
- [x] affordable-basement-renovation-toronto-guide (Batch 1)
- [x] avoid-handyman-scams (Batch 1)
- [x] benefits-of-interlocking-pavers-in-toronto (Batch 1)
- [x] a-look-at-tips-to-remodel-your-basement-with-low-ceiling (Batch 2)
- [x] a-review-of-the-7-best-handyman-services-in-toronto-2023 (Batch 2)
- [x] accessorizing-renovated-bathroom-toronto (Batch 2)
- [x] affordable-home-renovation-tips-toronto (Batch 2)

Плюс 6 постов в `/blog/*` уже в новом формате (commit 1ff86eab).

## Осталось переписать (66 верхнеуровневых статей)

### Batch 3 (в процессе)

- [x] 5-types-of-landscaping-features-you-can-find-in-toronto → /book-landscaping.html
- [ ] advantages-of-hiring-a-handyman → /book-handy.html
- [ ] amazing-decks-in-richmond-hill → /book-deck.html
- [ ] avoiding-general-contractor-scams → /book-contractor.html

### Очередь (62 статьи)

- [ ] backyard-demolition-services-landscaper → /book-demolition.html
- [ ] backyard-oasis-in-richmond-hill → /book-landscaping.html
- [ ] basement-renovation-costs-toronto-guide → /book-basement.html
- [ ] bathroom-renovation → /book-bathroom.html
- [ ] blog-carpenter-services-toronto-gta → /book-carpentry.html
- [ ] bright-ideas-christmas-light-displays → /book-christmas.html
- [ ] building-a-deck-in-aurora → /book-deck.html
- [ ] choose-right-decking-material-landscape → /book-deck.html
- [ ] choosing-perfect-deck-contractor → /book-deck.html
- [ ] choosing-right-decking-material-landscape → /book-deck.html
- [ ] choosing-the-best-fence-contractor → /book-fence.html
- [ ] construction-project-in-the-winter → /book-renovation.html
- [ ] contractor-not-warranty → /book-contractor.html
- [ ] contractor-warranty-client-materials-guide → /book-contractor.html
- [ ] custom-decks-richmond-hill → /book-deck.html
- [ ] effective-communication → /book-contractor.html
- [ ] electing-materials-bathroom-renovation-toronto → /book-bathroom.html
- [ ] elegant-bathroom-makeovers-selecting-the-right-renovation-services-in-toronto → /book-bathroom.html
- [ ] essential-deck-maintenance-for-newmarket-homes → /book-deck.html
- [ ] expensive-parts-basement-renovation → /book-basement.html
- [ ] expert-demolition-services-a-maximum-construction → /book-demolition.html
- [ ] expert-insights-crafting-excellence-with-torontos-general-contracting-services → /book-contractor.html
- [ ] expert-richmond-hill-deck-builders-quality-decks → /book-deck.html
- [ ] expert-tips → /book-renovation.html
- [ ] exploring-the-benefits-of-outdoor-living-spaces-enhancing-your-home-and-lifestyle → /book-landscaping.html
- [ ] find-perfect-deck-contractor → /book-deck.html
- [ ] first-steps-renovation-permits → /book-renovation.html
- [ ] general-contractor-services-2 → /book-contractor.html
- [ ] handyman-charges → /book-handy.html
- [ ] how-amaximum-repair-damaged-deck-boards → /book-deck.html
- [ ] how-can-i-ensure-timely-completion-of-my-deck-construction-project → /book-deck.html
- [ ] how-long-does-it-take-to-complete-a-deck-construction-project → /book-deck.html
- [ ] how-to-avoid-injury-while-hanging-christmas-lights → /book-christmas.html
- [ ] how-to-repair-wood-decks → /book-deck.html
- [ ] installation-timelines → /book-renovation.html
- [ ] is-it-cheaper-to-build-your-own-deck-aurora → /book-deck.html
- [ ] is-it-really-worth-it-to-renovate-a-basement → /book-basement.html
- [ ] legal-considerations-renovating → /book-renovation.html
- [ ] material-costs-in-billing-explained → /book-contractor.html
- [ ] navigating-basement-renovation-in-toronto-top-contractors-to-consider → /book-basement.html
- [ ] navigating-permits-regulations-bathroom-renovation-toronto → /book-bathroom.html
- [ ] professional-demolition-services → /book-demolition.html
- [ ] rate-for-a-handyman → /book-handy.html
- [ ] reasons-to-hire-amaximum-construction-for-basement-renovation-services → /book-basement.html
- [ ] reasons-to-hire-professional-deck-contractors → /book-deck.html
- [ ] renovation-services-in-toronto → /book-renovation.html
- [ ] renovation-services-in-toronto-2 → /book-renovation.html
- [ ] richmond-hill-custom-decks-sustainable-stylish → /book-deck.html
- [ ] scammer-in-contractors-industry-toronto → /book-contractor.html
- [ ] searching-for-the-top-rated-fence-contractors → /book-fence.html
- [ ] selecting-top-notch-handyman-and-contractor-services → /book-handy.html
- [ ] small-contractors-in-toronto → /book-contractor.html
- [ ] supply-my-own-materials → /book-contractor.html
- [ ] top-affordable-small-contractors-in-toronto → /book-contractor.html
- [ ] toronto-deck-builders-combining-aesthetics-with-durability → /book-deck.html
- [ ] torontos-top-rated-fence-contractors-a-comprehensive-comparison → /book-fence.html
- [ ] transforming-spaces-your-trusted-partners-for-home-renovation-in-toronto → /book-renovation.html
- [ ] trusted-small-contractors-toronto → /book-contractor.html
- [ ] ultimate-guide-finding-best-fence-contractor → /book-fence.html
- [ ] understanding-additional-service-costs → /book-contractor.html
- [ ] understanding-cost-building → /book-contractor.html
- [ ] your-guide-to-choose-landscaping-services-in-toronto → /book-landscaping.html

## Команды для проверки

```powershell
# Запустить скрипт-инвентарь (показывает что NEW / OLD)
python _list_old_blogs.py

# QA одной статьи
python _blog_qa2.py <slug>
```

## История коммитов batch-ей

- `1ff86eab` — 6 постов в `/blog/*`
- `73c72df5` — Batch 1 (4 верхнеуровневых)
- `48881090` — фикс хабов deck-builder + 4 хаба
- `969e250f` — site-wide правило hub/location/blog
- `d456744f` — Batch 2 (4 верхнеуровневых)
