#!/usr/bin/env python3
"""Find location pages among unclassified ones."""

from pathlib import Path

# Все города GTA
CITIES = ['toronto', 'markham', 'richmond-hill', 'vaughan', 'newmarket', 
          'aurora', 'north-york', 'east-york', 'etobicoke', 'scarborough',
          'woodbridge', 'mississauga', 'brampton', 'oakville', 'burlington',
          'hamilton', 'ajax', 'pickering', 'whitby', 'oshawa', 'concord',
          'maple', 'thornhill', 'unionville', 'king-city', 'bradford', 'gta']

# Не классифицированные
unclassified = [
    'building-a-deck-in-aurora',
    'building-a-small-deck-in-toronto',
    'deck-maintenance-in-markhams-variable-climate',
    'handyman-charges',
    'handyman-drywall-repair',
    'handyman-furniture-assembly',
    'paving-company',
    'pergola-builder',
    'pergola-contractors-toronto',
    'portico-designs',
    'renovation-in-north-york',
    'retaining-wall-contractors-in-gta',
    'roofing-company',
    'sod-installation',
    'client-testimonials',
    'company-policy-of-amaximum-construction',
    'construction-project-in-the-winter',
    'contractor-not-warranty',
    'effective-communication',
    'first-steps-renovation-permits',
    'how-amaximum-repair-damaged-deck-boards',
    'how-can-i-ensure-timely-completion-of-my-deck-construction-project',
    'how-long-does-it-take-to-complete-a-deck-construction-project',
    'installation-timelines',
    'legal-considerations-renovating',
    'material-costs-in-billing-explained',
    'our-work-process',
]

print("=" * 60)
print("АНАЛИЗ НЕ КЛАССИФИЦИРОВАННЫХ СТРАНИЦ")
print("=" * 60)

locations = []
articles = []

for page in unclassified:
    f = Path(page) / 'index.html'
    if f.exists():
        # Проверяем есть ли город
        has_city = any(c in page.lower() for c in CITIES)
        if has_city:
            locations.append(page)
        else:
            articles.append(page)

print(f"\n📍 ЛОКАЦИИ (нужно привязать к сервисам): {len(locations)}")
for p in locations:
    print(f"  - {p}")

print(f"\n📄 СТАТЬИ/ИНФО СТРАНИЦЫ: {len(articles)}")
for p in articles:
    print(f"  - {p}")
