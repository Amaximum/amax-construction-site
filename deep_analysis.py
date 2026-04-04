#!/usr/bin/env python3
"""
Глубокий анализ Hub & Spoke структуры сайта.
Проверяет что ВСЕ локационные страницы привязаны к своим сервисным хабам.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Все 18 сервисных хабов
SERVICE_HUBS = {
    'deck-builder': {
        'name': 'Deck Building',
        'keywords': ['deck-builder', 'deck-contractor', 'custom-deck', 'wood-deck-repair', 'deck-building'],
        'hub_path': 'deck-builder',
    },
    'deck-railings': {
        'name': 'Deck Railings', 
        'keywords': ['deck-railing', 'railing-builder', 'railing-installer'],
        'hub_path': 'deck-railings-toronto',
    },
    'fence': {
        'name': 'Fence Installation',
        'keywords': ['fence-contractor', 'fence-install', 'fence-builder', 'fence-company'],
        'hub_path': 'fence-installation',
    },
    'bathroom': {
        'name': 'Bathroom Renovation',
        'keywords': ['bathroom-renovation', 'bathroom-remodel', 'bathrooms-renovation'],
        'hub_path': 'bathroom-renovation',
    },
    'basement': {
        'name': 'Basement Renovation',
        'keywords': ['basement-renovation', 'basement-finish', 'basement-remodel'],
        'hub_path': 'basement-renovation',
    },
    'handyman': {
        'name': 'Handyman Services',
        'keywords': ['handyman-service', 'handyman-services'],
        'hub_path': 'handyman-services',
    },
    'general-contractor': {
        'name': 'General Contractor',
        'keywords': ['general-contractor'],
        'hub_path': 'general-contractor',
    },
    'carpenter': {
        'name': 'Carpentry',
        'keywords': ['carpenter-service', 'carpentry'],
        'hub_path': 'carpenter-services',
    },
    'demolition': {
        'name': 'Demolition',
        'keywords': ['demolition-service'],
        'hub_path': 'demolition-services',
    },
    'interlocking': {
        'name': 'Interlocking Pavers',
        'keywords': ['interlocking', 'paver-service', 'interlock-'],
        'hub_path': 'interlocking-paver-services',
    },
    'christmas-lights': {
        'name': 'Christmas Lights',
        'keywords': ['christmas-light'],
        'hub_path': 'christmas-lights-installation-toronto-gta',
    },
    'home-renovation': {
        'name': 'Home Renovation',
        'keywords': ['home-renovation'],
        'hub_path': 'home-renovation',
    },
    'landscaping': {
        'name': 'Landscaping',
        'keywords': ['landscaping-service'],
        'hub_path': 'landscaping-services-toronto',
    },
    'plumbing': {
        'name': 'Plumbing',
        'keywords': ['plumbing-service', 'handyman-plumbing'],
        'hub_path': 'handyman-plumbing-services',
    },
    'electrical': {
        'name': 'Electrical',
        'keywords': ['electrical-handyman', 'electrical-service'],
        'hub_path': 'electrical-handyman-services',
    },
    'painting': {
        'name': 'Painting',
        'keywords': ['painting-service', 'handyman-painting'],
        'hub_path': 'handyman-painting-services',
    },
    'canopy': {
        'name': 'Canopy & Pergolas',
        'keywords': ['canopy', 'pergola'],
        'hub_path': 'canopy',
    },
    'excavation': {
        'name': 'Excavation',
        'keywords': ['excavation-service'],
        'hub_path': 'excavation-services',
    },
}

# Паттерны для исключения (блоги, статьи)
EXCLUDE_PATTERNS = [
    'blog', 'guide', 'tips', 'review', 'best-', 'how-to', 'benefits-',
    'affordable-', 'essential-', 'exploring-', 'choosing-', 'choose-',
    'avoid-', 'advantages-', 'avoiding-', 'a-look-at-', '-ideas',
    '5-types-', '3-easy-', '7-best-', 'hidden-costs-', 'prepare-',
    'master-', 'ultimate-', 'understanding-', 'backyard-oasis',
    'amazing-decks', 'custom-decks-', 'accessorizing-', 'protect-your-',
    'what-is-', 'why-', 'transform', 'top-', 'trusted-', 'torontos-',
    'trex-', 'your-guide', 'electing-', 'portico-designs', 'popular-',
    'perfect-', 'navigating-', 'maximizing-', 'key-factors', 'innovative-',
    'importance-of-', 'hidden-', 'highlight-', 'enhancing-', 'comparing-',
    'comprehensive-', 'common-', 'create-', 'creating-', 'decoding-',
    'detail-', 'discover-', 'diy-', 'expert-', 'find-', 'getting-',
    'inside-', 'is-it-', 'latest-', 'leading-', 'local-', 'main/',
    'making-', 'modern-', 'must-', 'near-me', 'quality-', 'quick-',
    'real-', 'revamp-', 'reveal-', 'right-', 'selecting-', 'smart-',
    'step-by-step', 'stylish-', 'the-art-', 'the-best-', 'the-cost-',
    'the-importance', 'the-top-', 'the-ultimate', 'things-', 'turn-',
    'ways-to-', 'when-to-', 'where-to-', 'which-', 'winter-', 'worth-',
]

def is_service_page(folder_name: str) -> bool:
    """Проверяет является ли папка сервисной страницей (не блогом)."""
    lower = folder_name.lower()
    return not any(ex in lower for ex in EXCLUDE_PATTERNS)

def classify_page(folder_name: str) -> tuple:
    """Классифицирует страницу по сервису."""
    lower = folder_name.lower()
    
    for service_key, service_info in SERVICE_HUBS.items():
        for keyword in service_info['keywords']:
            if keyword in lower:
                return service_key, service_info['name']
    
    return None, None

def check_hub_has_location(hub_path: str, location_path: str) -> bool:
    """Проверяет есть ли ссылка на локацию в хабе."""
    hub_file = Path(hub_path) / 'index.html'
    if not hub_file.exists():
        return False
    
    content = hub_file.read_text(encoding='utf-8', errors='ignore')
    # Ищем ссылку на локацию
    return f'href="/{location_path}/"' in content or f"href='/{location_path}/'" in content

def main():
    print("=" * 70)
    print("ГЛУБОКИЙ АНАЛИЗ СТРУКТУРЫ САЙТА")
    print("=" * 70)
    
    base = Path('.')
    all_folders = [d.name for d in base.iterdir() if d.is_dir() and (d / 'index.html').exists()]
    
    # Исключаем служебные папки
    exclude_folders = {'locations', 'blog', 'portfolio', 'css', 'js', 'img', 'book-now', 
                       'thank-you-page', 'what-we-do', 'why-choose-us', 'main', 'services',
                       '__pycache__', '.git', 'node_modules'}
    
    all_folders = [f for f in all_folders if f not in exclude_folders]
    
    # Классифицируем все страницы
    service_pages = defaultdict(list)  # service_key -> list of pages
    unclassified = []
    blog_articles = []
    
    for folder in all_folders:
        if not is_service_page(folder):
            blog_articles.append(folder)
            continue
            
        service_key, service_name = classify_page(folder)
        if service_key:
            service_pages[service_key].append(folder)
        else:
            unclassified.append(folder)
    
    # Анализ каждого сервиса
    print("\n" + "=" * 70)
    print("АНАЛИЗ ПО СЕРВИСАМ")
    print("=" * 70)
    
    total_location_pages = 0
    missing_links = defaultdict(list)
    
    for service_key, service_info in SERVICE_HUBS.items():
        pages = service_pages.get(service_key, [])
        hub_path = service_info['hub_path']
        hub_file = Path(hub_path) / 'index.html'
        
        # Считаем локации (исключая сам хаб)
        location_pages = [p for p in pages if p != hub_path]
        total_location_pages += len(location_pages)
        
        hub_exists = hub_file.exists()
        
        # Проверяем ссылки в хабе
        linked_count = 0
        not_linked = []
        
        if hub_exists:
            hub_content = hub_file.read_text(encoding='utf-8', errors='ignore')
            for loc_page in location_pages:
                if f'href="/{loc_page}/"' in hub_content:
                    linked_count += 1
                else:
                    not_linked.append(loc_page)
                    missing_links[service_key].append(loc_page)
        
        status = "✅" if len(not_linked) == 0 and hub_exists else "⚠️"
        hub_status = "✓" if hub_exists else "✗ НЕТ ХАБА!"
        
        print(f"\n{status} {service_info['name']} ({hub_path})")
        print(f"   Hub: {hub_status}")
        print(f"   Локаций: {len(location_pages)}, Привязано: {linked_count}")
        
        if not_linked:
            print(f"   ❌ НЕ ПРИВЯЗАНО ({len(not_linked)}):")
            for nl in not_linked[:5]:
                print(f"      - {nl}")
            if len(not_linked) > 5:
                print(f"      ... и ещё {len(not_linked) - 5}")
    
    # Не классифицированные
    print("\n" + "=" * 70)
    print("НЕ КЛАССИФИЦИРОВАННЫЕ СТРАНИЦЫ")
    print("=" * 70)
    print(f"Всего: {len(unclassified)}")
    for page in sorted(unclassified)[:20]:
        print(f"  - {page}")
    if len(unclassified) > 20:
        print(f"  ... и ещё {len(unclassified) - 20}")
    
    # Статистика
    print("\n" + "=" * 70)
    print("ОБЩАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"Всего папок с index.html: {len(all_folders) + len(blog_articles)}")
    print(f"Сервисных хабов: {len(SERVICE_HUBS)}")
    print(f"Локационных страниц: {total_location_pages}")
    print(f"Блогов/статей: {len(blog_articles)}")
    print(f"Не классифицировано: {len(unclassified)}")
    
    # Страницы с отсутствующими ссылками
    total_missing = sum(len(v) for v in missing_links.values())
    print(f"\n❌ ВСЕГО ОТСУТСТВУЮЩИХ ССЫЛОК: {total_missing}")
    
    if total_missing > 0:
        print("\nДетали:")
        for service_key, pages in missing_links.items():
            if pages:
                print(f"  {SERVICE_HUBS[service_key]['name']}: {len(pages)} страниц")

if __name__ == '__main__':
    main()
