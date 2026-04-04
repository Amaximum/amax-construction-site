#!/usr/bin/env python3
"""
Полный анализ Hub & Spoke структуры.
Находит ВСЕ локации для каждого сервиса и проверяет связи.
"""

import os
import re
from collections import defaultdict

# Сервисные хабы и их паттерны для поиска локаций
SERVICE_HUBS = {
    "deck-builder": {
        "hub": "deck-builder",
        "patterns": [r"deck-build", r"deck-construct", r"deck-.*-in-", r"deck-.*-toronto", r"build.*deck"],
        "keywords": ["deck-build", "deck-construct"]
    },
    "deck-railings-toronto": {
        "hub": "deck-railings-toronto", 
        "patterns": [r"deck-rail", r"railing"],
        "keywords": ["deck-rail", "railing"]
    },
    "fence-installation": {
        "hub": "fence-installation",
        "patterns": [r"fence-", r"fencing"],
        "keywords": ["fence"]
    },
    "bathroom-renovation": {
        "hub": "bathroom-renovation",
        "patterns": [r"bathroom-renov", r"bathroom-remodel"],
        "keywords": ["bathroom-renov", "bathroom-remodel"]
    },
    "basement-renovation": {
        "hub": "basement-renovation",
        "patterns": [r"basement-renov", r"basement-finish"],
        "keywords": ["basement-renov"]
    },
    "handyman-services": {
        "hub": "handyman-services",
        "patterns": [r"handyman-service.*-in-", r"handyman-in-"],
        "keywords": ["handyman-service", "handyman-in-"]
    },
    "general-contractor": {
        "hub": "general-contractor",
        "patterns": [r"general-contractor-in-"],
        "keywords": ["general-contractor-in-"]
    },
    "carpenter-services": {
        "hub": "carpenter-services",
        "patterns": [r"carpenter-", r"carpentry-"],
        "keywords": ["carpenter", "carpentry"]
    },
    "demolition-services": {
        "hub": "demolition-services",
        "patterns": [r"demolition-"],
        "keywords": ["demolition"]
    },
    "interlocking-paver-services": {
        "hub": "interlocking-paver-services",
        "patterns": [r"interlock", r"paver"],
        "keywords": ["interlock", "paver"]
    },
    "christmas-lights-installation-toronto-gta": {
        "hub": "christmas-lights-installation-toronto-gta",
        "patterns": [r"christmas-light"],
        "keywords": ["christmas-light"]
    },
    "home-renovation": {
        "hub": "home-renovation",
        "patterns": [r"home-renov.*-in-", r"home-improvement"],
        "keywords": ["home-renov"]
    },
    "landscaping-services-toronto": {
        "hub": "landscaping-services-toronto",
        "patterns": [r"landscap"],
        "keywords": ["landscap"]
    },
    "handyman-plumbing-services": {
        "hub": "handyman-plumbing-services",
        "patterns": [r"plumb"],
        "keywords": ["plumb"]
    },
    "electrical-handyman-services": {
        "hub": "electrical-handyman-services",
        "patterns": [r"electric"],
        "keywords": ["electric"]
    },
    "handyman-painting-services": {
        "hub": "handyman-painting-services",
        "patterns": [r"paint"],
        "keywords": ["paint"]
    },
    "canopy": {
        "hub": "canopy",
        "patterns": [r"canopy", r"pergola", r"gazebo"],
        "keywords": ["canopy", "pergola", "gazebo"]
    },
    "excavation-services": {
        "hub": "excavation-services",
        "patterns": [r"excavat"],
        "keywords": ["excavat"]
    }
}

# Города GTA
GTA_CITIES = [
    "toronto", "north-york", "east-york", "etobicoke", "scarborough",
    "vaughan", "woodbridge", "richmond-hill", "markham", "aurora",
    "newmarket", "king-city", "nobleton", "whitchurch-stouffville",
    "mississauga", "brampton", "oakville", "burlington", "milton",
    "pickering", "ajax", "oshawa", "unionville", "thornhill",
    "maple", "concord", "kleinburg", "stouffville"
]

def get_all_pages():
    """Получить все папки с index.html"""
    pages = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith(('.', '_')):
            if os.path.exists(os.path.join(item, 'index.html')):
                pages.append(item)
    return pages

def is_location_page(page_name):
    """Проверить, является ли страница локационной (содержит город)"""
    page_lower = page_name.lower()
    for city in GTA_CITIES:
        if city in page_lower:
            return True, city
    return False, None

def find_service_locations(all_pages, service_config):
    """Найти все локации для сервиса"""
    locations = []
    keywords = service_config["keywords"]
    hub = service_config["hub"]
    
    for page in all_pages:
        if page == hub:
            continue
            
        page_lower = page.lower()
        is_loc, city = is_location_page(page)
        
        if is_loc:
            # Проверяем, относится ли к этому сервису
            for kw in keywords:
                if kw in page_lower:
                    locations.append(page)
                    break
    
    return locations

def check_hub_has_location_section(hub_path):
    """Проверить, есть ли секция локаций в хабе"""
    index_file = os.path.join(hub_path, 'index.html')
    if not os.path.exists(index_file):
        return False, []
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_section = 'location-grid' in content or 'service-locations' in content
    
    # Найти все ссылки на локации
    linked = []
    links = re.findall(r'href="/?([^"]+)/"', content)
    for link in links:
        is_loc, _ = is_location_page(link)
        if is_loc:
            linked.append(link)
    
    return has_section, linked

def main():
    all_pages = get_all_pages()
    print(f"Всего страниц: {len(all_pages)}\n")
    
    print("="*80)
    print("ПОЛНЫЙ АНАЛИЗ HUB & SPOKE СТРУКТУРЫ")
    print("="*80)
    
    missing_sections = []
    missing_links = {}
    
    for service_name, config in SERVICE_HUBS.items():
        hub = config["hub"]
        
        # Найти все локации для сервиса
        locations = find_service_locations(all_pages, config)
        
        # Проверить секцию в хабе
        has_section, linked = check_hub_has_location_section(hub)
        
        # Найти не привязанные локации
        not_linked = [loc for loc in locations if loc not in linked]
        
        # Статус
        if len(locations) == 0:
            status = "⚪ Нет локаций"
        elif not has_section:
            status = "❌ НЕТ СЕКЦИИ ЛОКАЦИЙ"
            missing_sections.append(service_name)
        elif len(not_linked) > 0:
            status = f"⚠️ Не все привязаны ({len(not_linked)} из {len(locations)})"
        else:
            status = "✅ ОК"
        
        print(f"\n{status}")
        print(f"   Сервис: {service_name}")
        print(f"   Hub: {hub}")
        print(f"   Локаций найдено: {len(locations)}")
        print(f"   Привязано в хабе: {len(linked)}")
        
        if locations:
            print(f"   Локации: {', '.join(locations[:5])}{'...' if len(locations) > 5 else ''}")
        
        if not_linked:
            missing_links[service_name] = {
                "hub": hub,
                "locations": locations,
                "not_linked": not_linked,
                "has_section": has_section
            }
            print(f"   ❌ Не привязано: {not_linked}")
    
    print("\n" + "="*80)
    print("ИТОГО")
    print("="*80)
    
    if missing_sections:
        print(f"\n❌ СЕРВИСЫ БЕЗ СЕКЦИИ ЛОКАЦИЙ ({len(missing_sections)}):")
        for s in missing_sections:
            locs = find_service_locations(all_pages, SERVICE_HUBS[s])
            print(f"   - {s}: {len(locs)} локаций")
    
    if missing_links:
        print(f"\n⚠️ СЕРВИСЫ С НЕПРИВЯЗАННЫМИ ЛОКАЦИЯМИ ({len(missing_links)}):")
        for s, data in missing_links.items():
            print(f"   - {s}: {len(data['not_linked'])} не привязано")
    
    # Сохранить данные для исправления
    with open('hub_spoke_fix_data.txt', 'w', encoding='utf-8') as f:
        f.write("# Данные для исправления Hub & Spoke\n\n")
        for service_name, data in missing_links.items():
            f.write(f"\n## {service_name}\n")
            f.write(f"Hub: {data['hub']}\n")
            f.write(f"Has section: {data['has_section']}\n")
            f.write(f"All locations ({len(data['locations'])}):\n")
            for loc in sorted(data['locations']):
                f.write(f"  - {loc}\n")
            f.write(f"Not linked ({len(data['not_linked'])}):\n")
            for loc in sorted(data['not_linked']):
                f.write(f"  - {loc}\n")
    
    print("\n✅ Данные сохранены в hub_spoke_fix_data.txt")

if __name__ == "__main__":
    main()
