"""Insert image carousels into service/location pages that are missing them.

Carousel is inserted between </div> of page-hero and <div class="container">.
Image set is chosen by service type from the slug.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# slug -> (image folder prefix, image basenames, alt label)
DECK_IMAGES = [
    "deck-1.jpg", "deck-2.jpg", "deck-3.jpg", "deck-4.jpg",
    "deck-user-1.jpg", "deck-user-2.jpg", "deck-user-3.jpg", "deck-user-4.jpg",
]
RAILING_IMAGES = [
    "deck-railings-1.jpg", "deck-railings-2.jpg", "deck-railings-3.jpg",
    "deck-railings-4.jpg", "deck-railings-5.jpg",
]

TARGETS = {
    "deck-builder-gta":                   ("Deck Builder GTA",                 DECK_IMAGES),
    "deck-builder-schomberg":             ("Deck Builder Schomberg",           DECK_IMAGES),
    "deck-contractor-bradford":           ("Deck Contractor Bradford",         DECK_IMAGES),
    "deck-contractor-burlington":         ("Deck Contractor Burlington",       DECK_IMAGES),
    "deck-contractor-north-york":         ("Deck Contractor North York",       DECK_IMAGES),
    "deck-contractor-scarborough":        ("Deck Contractor Scarborough",      DECK_IMAGES),
    "deck-contractor-woodbridge":         ("Deck Contractor Woodbridge",       DECK_IMAGES),
    "deck-railing-builder-richmond-hill": ("Deck Railing Builder Richmond Hill", RAILING_IMAGES),
    "deck-railing-installer-east-york":   ("Deck Railing Installer East York", RAILING_IMAGES),
}


def build_carousel(label: str, images: list[str]) -> str:
    slides = "\n".join(
        f'        <figure class="carousel-slide"><img src="/img/services/{img}" '
        f'alt="{label} - project photo {i+1}" loading="lazy" decoding="async"></figure>'
        for i, img in enumerate(images)
    )
    return (
        f'\n  <section id="service-gallery" class="shell" style="padding:24px 0 0;" '
        f'aria-label="{label} - project gallery">\n'
        f'    <div class="carousel" data-carousel data-carousel-total="{len(images)}">\n'
        f'      <div class="carousel-track" data-carousel-track>\n'
        f"{slides}\n"
        f'      </div>\n'
        f'      <div class="carousel-controls">\n'
        f'        <button class="carousel-btn" type="button" data-carousel-prev aria-label="Previous image">Prev</button>\n'
        f'        <div class="carousel-dots" data-carousel-dots aria-label="Choose an image"></div>\n'
        f'        <button class="carousel-btn" type="button" data-carousel-next aria-label="Next image">Next</button>\n'
        f'      </div>\n'
        f'    </div>\n'
        f'  </section>\n'
    )


def insert_carousel(html: str, carousel: str) -> str | None:
    # Find the closing </div> of <div class="page-hero">...</div> and insert carousel after it
    # but before <div class="container">.
    pattern = re.compile(
        r'(<div class="page-hero">.*?</div>)(\s*<div class="container">)',
        re.DOTALL,
    )
    m = pattern.search(html)
    if not m:
        return None
    return html[: m.end(1)] + "\n" + carousel + html[m.start(2):]


def main() -> None:
    for slug, (label, images) in TARGETS.items():
        path = ROOT / slug / "index.html"
        if not path.exists():
            print(f"SKIP missing file: {slug}")
            continue
        html = path.read_text(encoding="utf-8")
        if "data-carousel" in html:
            print(f"SKIP already has carousel: {slug}")
            continue
        carousel = build_carousel(label, images)
        new_html = insert_carousel(html, carousel)
        if new_html is None:
            print(f"FAIL no insertion point: {slug}")
            continue
        path.write_text(new_html, encoding="utf-8")
        print(f"OK inserted {len(images)} images: {slug}")


if __name__ == "__main__":
    main()
