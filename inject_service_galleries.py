"""
Inject photo gallery sections into service pages that don't yet have one.
Gallery is placed AFTER the "Why choose us" island section.
Uses the same carousel structure already used sitewide.
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Service keyword → (images list, display label)
# Order matters: most specific keywords first (deck-railing before deck, etc.)
SERVICE_GALLERY = [
    ('deck-railing',      ['deck-railings-1.jpg','deck-railings-2.jpg','deck-railings-3.jpg','deck-railings-4.jpg','deck-railings-5.jpg'], 'Deck Railing'),
    ('deck-railings',     ['deck-railings-1.jpg','deck-railings-2.jpg','deck-railings-3.jpg','deck-railings-4.jpg','deck-railings-5.jpg'], 'Deck Railings'),
    ('deck',              ['deck-1.jpg','deck-2.jpg','deck-3.jpg','deck-4.jpg','deck-user-1.jpg','deck-user-2.jpg'], 'Deck Building'),
    ('basement',          ['basement-1.jpg','basement-2.jpg','basement-3.jpg','basement-4.jpg','basement-5.jpg'], 'Basement Renovation'),
    ('bathroom',          ['bathroom-1.jpg','bathroom-2.jpg','bathroom-3.jpg','bathroom-4.jpg','bathroom-5.jpg'], 'Bathroom Renovation'),
    ('bathrooms',         ['bathroom-1.jpg','bathroom-2.jpg','bathroom-3.jpg','bathroom-4.jpg','bathroom-5.jpg'], 'Bathroom Renovation'),
    ('canopy',            ['canopy-1.jpg','canopy-2.jpg','canopy-3.jpg','canopy-4.jpg','canopy-user-1.jpg'], 'Canopy Installation'),
    ('carpenter',         ['carpentry-1.jpg','carpentry-2.jpg','carpentry-3.jpg','carpentry-4.jpg','carpentry-5.jpg'], 'Carpentry Services'),
    ('christmas',         ['christmas-1.jpg','christmas-2.jpg','christmas-3.jpg','christmas-4.jpg','christmas-5.jpg'], 'Christmas Lights Installation'),
    ('demolition',        ['demolition-1.jpg','demolition-2.jpg','demolition-3.jpg','demolition-4.jpg','demolition-5.jpg'], 'Demolition Services'),
    ('electrical',        ['electrical-1.jpg','electrical-2.jpg','electrical-3.jpg','electrical-4.jpg','electrical-5.jpg'], 'Electrical Services'),
    ('excavation',        ['excavation-1.jpg','excavation-2.jpg','excavation-3.jpg','excavation-4.jpg','excavation-5.jpg'], 'Excavation Services'),
    ('fence',             ['fence-1.jpg','fence-2.jpg','fence-3.jpg','fence-4.jpg','fence-5.jpg'], 'Fence Installation'),
    ('plumbing',          ['plumbing-1.jpg','plumbing-2.jpg','plumbing-3.jpg','plumbing-4.jpg','plumbing-user-1.jpg'], 'Plumbing Services'),
    ('painting',          ['painting-1.jpg','painting-2.jpg','painting-3.jpg','painting-4.jpg','painting-5.jpg'], 'Painting Services'),
    ('handyman',          ['handyman-1.jpg','handyman-2.jpg','handyman-3.jpg','handyman-4.jpg','handyman-5.jpg'], 'Handyman Services'),
    ('interlocking',      ['interlocking-1.jpg','interlocking-2.jpg','interlocking-3.jpg','interlocking-4.jpg','interlocking-user-1.jpg'], 'Interlocking Paving'),
    ('paving',            ['interlocking-1.jpg','interlocking-2.jpg','interlocking-3.jpg','interlocking-4.jpg','interlocking-user-1.jpg'], 'Paving Services'),
    ('landscaping',       ['landscaping-1.jpg','landscaping-2.jpg','landscaping-3.jpg','landscaping-4.jpg','landscaping-5.jpg'], 'Landscaping Services'),
    ('general-contractor',['contractor-1.jpg','contractor-2.jpg','contractor-3.jpg','contractor-4.jpg','contractor-5.jpg'], 'General Contracting'),
    ('renovation-service',['renovation-1.jpg','renovation-2.jpg','renovation-3.jpg','renovation-4.jpg'], 'Renovation Services'),
    ('home-renovation',   ['home-renovation-1.jpg','home-renovation-2.jpg','home-renovation-3.jpg','home-renovation-4.jpg','home-renovation-5.jpg'], 'Home Renovation'),
]


def get_service_for_dir(dir_name):
    dn = dir_name.lower()
    for keyword, images, label in SERVICE_GALLERY:
        if keyword in dn:
            return images, label
    return None, None


def build_gallery_html(images, label):
    slides = ''
    for i, img_file in enumerate(images, 1):
        slides += (
            f'      <figure class="carousel-slide">\n'
            f'        <img src="/img/services/{img_file}" alt="{label} photo {i}" loading="lazy" decoding="async">\n'
            f'      </figure>\n'
        )

    total = len(images)
    html = (
        f'<section id="service-gallery" class="shell" style="padding:24px 0 0;" aria-label="Service gallery">\n'
        f'  <div class="carousel" data-carousel data-carousel-total="{total}">\n'
        f'    <div class="carousel-track" data-carousel-track>\n'
        f'{slides}'
        f'    </div>\n'
        f'    <div class="carousel-controls">\n'
        f'      <button class="carousel-btn" type="button" data-carousel-prev aria-label="Previous image">Prev</button>\n'
        f'      <div class="carousel-dots" data-carousel-dots aria-label="Choose an image"></div>\n'
        f'      <button class="carousel-btn" type="button" data-carousel-next aria-label="Next image">Next</button>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n'
    )
    return html


def inject_gallery(html_path, images, label):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has a carousel/gallery
    if 'data-carousel' in content or 'id="service-gallery"' in content:
        return 'skipped_has_gallery'

    # Must have a "Why choose us" section to know where to inject
    why_marker = 'aria-label="Why choose us"'
    if why_marker not in content:
        return 'skipped_no_why'

    # Find the position of the next <section after "Why choose us" opens
    why_idx = content.index(why_marker)
    try:
        next_section_idx = content.index('<section', why_idx + 100)
    except ValueError:
        return 'skipped_no_next_section'

    gallery_html = build_gallery_html(images, label)
    new_content = content[:next_section_idx] + gallery_html + content[next_section_idx:]

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return 'injected'


def main():
    counts = {'injected': 0, 'skipped_has_gallery': 0, 'skipped_no_why': 0, 'skipped_no_next_section': 0, 'no_match': 0}
    injected_pages = []

    for entry in sorted(os.scandir(BASE_DIR), key=lambda e: e.name):
        if not entry.is_dir():
            continue
        html_path = os.path.join(entry.path, 'index.html')
        if not os.path.exists(html_path):
            continue

        dir_name = entry.name
        images, label = get_service_for_dir(dir_name)
        if images is None:
            counts['no_match'] += 1
            continue

        result = inject_gallery(html_path, images, label)
        counts[result] += 1
        if result == 'injected':
            injected_pages.append(f'  [{label}] {dir_name}')

    print('\n=== Gallery injection results ===')
    for key, val in counts.items():
        print(f'  {key}: {val}')
    print(f'\nInjected into {counts["injected"]} pages:')
    for p in injected_pages:
        print(p)


if __name__ == '__main__':
    main()
