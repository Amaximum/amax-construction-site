#!/usr/bin/env python3
"""
Добавляет недостающие локации в хабы сервисов.
"""

import re
from pathlib import Path

# Маппинг хабов и их локационных страниц
FIXES = {
    'deck-railings-toronto': {
        'name': 'Deck Railings',
        'locations': [
            ('deck-railing-installer-in-aurora', 'Aurora'),
            ('deck-railing-installer-east-york', 'East York'),
            ('deck-railing-installer-in-etobicoke', 'Etobicoke'),
            ('deck-railing-installation-in-king-city', 'King City'),
            ('deck-railing-builder-markham', 'Markham'),
            ('deck-railing-installer-in-markham', 'Markham'),
            ('deck-railing-installer-in-newmarket', 'Newmarket'),
            ('deck-railing-installer-in-north-york', 'North York'),
            ('deck-railing-builder-richmond-hill', 'Richmond Hill'),
            ('deck-railing-installer-in-richmond-hill', 'Richmond Hill'),
            ('deck-railing-installer-in-scarborough', 'Scarborough'),
            ('deck-railing-installer-in-toronto', 'Toronto'),
            ('deck-railing-installer-in-vaughan', 'Vaughan'),
            ('deck-railing-vaughan', 'Vaughan'),
            ('deck-railing-installer-in-woodbridge', 'Woodbridge'),
        ],
    },
    'interlocking-paver-services': {
        'name': 'Interlocking Pavers',
        'add_locations': [
            ('interlocking-stone-services-north-york', 'North York'),
        ],
    },
    'landscaping-services-toronto': {
        'name': 'Landscaping',
        'add_locations': [
            ('landscaping-services', 'GTA'),
        ],
    },
}

def generate_locations_section(service_name: str, locations: list) -> str:
    """Генерирует HTML секцию с локациями."""
    # Убираем дубликаты по городу, оставляя первую ссылку
    seen = {}
    unique_locs = []
    for path, city in locations:
        if city not in seen:
            seen[city] = path
            unique_locs.append((path, city))
    
    cards = []
    for path, city in sorted(unique_locs, key=lambda x: x[1]):
        cards.append(f'    <a href="/{path}/" class="location-card">{city}</a>')
    
    section = f'''<section class="island reveal service-locations" id="locations" aria-label="Service locations">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>{service_name} in Your Area</h2>
    <p>We provide professional {service_name.lower()} services across the Greater Toronto Area. Select your location:</p>
  </div>
  <div class="location-grid">
{chr(10).join(cards)}
  </div>
</section>

'''
    return section

def add_locations_to_hub(hub_path: str, service_name: str, locations: list):
    """Добавляет секцию локаций в хаб."""
    hub_file = Path(hub_path) / 'index.html'
    if not hub_file.exists():
        print(f"  ⚠️ Хаб не найден: {hub_file}")
        return False
    
    html = hub_file.read_text(encoding='utf-8')
    
    # Проверяем есть ли уже секция
    if 'id="locations"' in html:
        print(f"  ℹ️ Секция уже есть, обновляем...")
        # Удаляем старую секцию
        pattern = r'<section class="island reveal service-locations" id="locations".*?</section>\s*'
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    # Генерируем новую секцию
    section = generate_locations_section(service_name, locations)
    
    # Ищем место для вставки - перед reviews-embed или FAQ
    if '<section id="reviews-embed"' in html:
        insert_point = html.find('<section id="reviews-embed"')
    elif '<section class="island reveal" id="faq"' in html:
        insert_point = html.find('<section class="island reveal" id="faq"')
    elif '</main>' in html:
        insert_point = html.find('</main>')
    else:
        print(f"  ⚠️ Не найдено место для вставки")
        return False
    
    new_html = html[:insert_point] + section + html[insert_point:]
    hub_file.write_text(new_html, encoding='utf-8')
    print(f"  ✅ Добавлено {len(locations)} локаций")
    return True

def add_missing_to_existing_section(hub_path: str, add_locations: list):
    """Добавляет недостающие локации в существующую секцию."""
    hub_file = Path(hub_path) / 'index.html'
    if not hub_file.exists():
        print(f"  ⚠️ Хаб не найден: {hub_file}")
        return False
    
    html = hub_file.read_text(encoding='utf-8')
    
    for path, city in add_locations:
        link = f'href="/{path}/"'
        if link in html:
            print(f"  ℹ️ {city} уже есть")
            continue
        
        # Добавляем перед </div> закрывающим location-grid
        new_card = f'    <a href="/{path}/" class="location-card">{city}</a>\n  '
        pattern = r'(class="location-grid">\s*(?:<a[^>]+>[^<]+</a>\s*)+)(</div>)'
        
        def replacer(m):
            return m.group(1) + new_card + m.group(2)
        
        new_html, count = re.subn(pattern, replacer, html, flags=re.DOTALL)
        if count > 0:
            html = new_html
            print(f"  ✅ Добавлено: {city}")
    
    hub_file.write_text(html, encoding='utf-8')
    return True

def main():
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ НЕДОСТАЮЩИХ ЛОКАЦИЙ")
    print("=" * 60)
    
    for hub_path, config in FIXES.items():
        print(f"\n📍 {config['name']} ({hub_path})")
        
        if 'locations' in config:
            add_locations_to_hub(hub_path, config['name'], config['locations'])
        
        if 'add_locations' in config:
            add_missing_to_existing_section(hub_path, config['add_locations'])
    
    print("\n" + "=" * 60)
    print("ГОТОВО!")

if __name__ == '__main__':
    main()
