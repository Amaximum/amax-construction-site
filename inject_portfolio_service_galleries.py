from __future__ import annotations

import re
from pathlib import Path

from add_service_carousels import build_spec

ROOT = Path(__file__).resolve().parent
PORTFOLIO = ROOT / "portfolio" / "index.html"

# Canonical service pages to link to from Portfolio.
SERVICE_LINKS: dict[str, str] = {
    "deck": "/deck-builder/",
    "deck-railings": "/deck-railings-toronto/",
    "basement": "/basement-renovation-service-in-toronto/",
    "bathroom": "/bathroom-renovation/",
    "fence": "/fence-contractor-in-toronto/",
    "plumbing": "/handyman-plumbing-services/",
    "electrical": "/electrical-handyman-services/",
    "painting": "/handyman-painting-services/",
    "canopy": "/canopy/",
    "landscaping": "/landscaping-services-toronto/",
    "interlocking": "/interlocking-paver-services/",
    "carpentry": "/carpenter-services/",
    "demolition": "/demolition-services/",
    "excavation": "/excavation-services/",
    "christmas": "/christmas-lights-installation-toronto-gta/",
    "home-renovation": "/home-renovation/",
    "handyman": "/handyman-service-in-toronto/",
    "contractor": "/general-contractor-in-toronto/",
}

ORDER: list[str] = [
    "deck",
    "deck-railings",
    "fence",
    "bathroom",
    "basement",
    "home-renovation",
    "plumbing",
    "electrical",
    "painting",
    "handyman",
    "contractor",
    "carpentry",
    "interlocking",
    "landscaping",
    "demolition",
    "excavation",
    "canopy",
    "christmas",
]

INSERT_BEFORE = "<!-- CTA -->"
SECTION_ID = "portfolio-service-galleries"


def render_carousel_inner(spec_title: str, images: list[str]) -> str:
    slides_html: list[str] = []
    for idx, src in enumerate(images, start=1):
        alt = f"{spec_title} photo {idx}"
        slides_html.append(
            "\n".join(
                [
                    "          <figure class=\"carousel-slide\">",
                    f"            <img src=\"{src}\" alt=\"{alt}\" loading=\"lazy\" decoding=\"async\">",
                    "          </figure>",
                ]
            )
        )

    total = len(images)
    return "\n".join(
        [
            f"        <div class=\"carousel\" data-carousel data-carousel-total=\"{total}\">",
            "          <div class=\"carousel-track\" data-carousel-track>",
            *slides_html,
            "          </div>",
            "          <div class=\"carousel-controls\">",
            "            <button class=\"carousel-btn\" type=\"button\" data-carousel-prev aria-label=\"Previous image\">Prev</button>",
            "            <div class=\"carousel-dots\" data-carousel-dots aria-label=\"Choose an image\"></div>",
            "            <button class=\"carousel-btn\" type=\"button\" data-carousel-next aria-label=\"Next image\">Next</button>",
            "          </div>",
            "        </div>",
        ]
    )


def build_section() -> str:
    cards: list[str] = []

    for key in ORDER:
        if key not in SERVICE_LINKS:
            continue
        spec = build_spec(key)
        href = SERVICE_LINKS[key]

        cards.append(
            "\n".join(
                [
                    "      <div class=\"card\">",
                    f"        <h3 style=\"margin:0 0 10px;\"><a href=\"{href}\" style=\"color: var(--primary); font-weight: 800; text-decoration: none;\">{spec.title}</a></h3>",
                    f"        <p class=\"meta\" style=\"margin:0 0 12px;\">Explore {spec.title.lower()} projects</p>",
                    render_carousel_inner(spec.title, spec.images),
                    "      </div>",
                ]
            )
        )

    return "\n".join(
        [
            f"      <section id=\"{SECTION_ID}\">",
            "        <h2>Service Galleries</h2>",
            "        <p>Browse our photo galleries by service.</p>",
            "        <div class=\"grid\">",
            *cards,
            "        </div>",
            "      </section>",
            "",
        ]
    )


def main() -> int:
    if not PORTFOLIO.exists():
        raise SystemExit(f"Portfolio not found: {PORTFOLIO}")

    html = PORTFOLIO.read_text(encoding="utf-8")

    if SECTION_ID in html:
        print("Portfolio already contains service galleries section; nothing to do.")
        return 0

    if INSERT_BEFORE not in html:
        raise SystemExit(f"Insert marker not found: {INSERT_BEFORE}")

    # Insert inside the <div class="shell"> in <main>.
    section = build_section()
    html = html.replace(INSERT_BEFORE, section + "      " + INSERT_BEFORE, 1)

    PORTFOLIO.write_text(html, encoding="utf-8")
    print("=== inject_portfolio_service_galleries ===")
    print(f"Updated: {PORTFOLIO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
