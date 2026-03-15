from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "img" / "services"


@dataclass(frozen=True)
class CarouselSpec:
    key: str
    title: str
    images: list[str]  # web paths, e.g. /img/services/deck-1.jpg


def is_service_page(html: str) -> bool:
    # Service/service+location pages share these patterns.
    if "class=\"blog-hero\"" in html:
        return False
    return (
        "class=\"page-hero\"" in html
        and "class=\"cta-section\"" in html
        and "id=\"reviews-embed\"" in html
    )


def detect_service_key(path: Path, html: str) -> str | None:
    p = "/" + str(path.relative_to(ROOT)).replace("\\", "/")
    p = p.lower()
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    h1 = re.sub(r"<[^>]+>", " ", h1_match.group(1)) if h1_match else ""
    h1 = re.sub(r"\s+", " ", h1).strip().lower()

    def has(*parts: str) -> bool:
        return any(part in p for part in parts) or any(part in h1 for part in parts)

    if has("deck-railings", "deck railing"):
        return "deck-railings"
    if has(
        "deck-builder",
        "deck-contractor",
        "deck building",
        "deck builder",
        "deck contractor",
        "wood deck",
        "deck repair",
    ):
        return "deck"
    if has("basement", "basement renovation"):
        return "basement"
    if has("bathroom", "bathroom renovation"):
        return "bathroom"
    if has("fence", "fencing"):
        return "fence"
    if has("plumbing"):
        return "plumbing"
    if has("electrical"):
        return "electrical"
    if has("painting"):
        return "painting"
    if has("canopy", "awning"):
        return "canopy"
    if has("carpenter", "carpentry"):
        return "carpentry"
    if has("landscap"):
        return "landscaping"
    if has("interlocking", "paver", "paving"):
        return "interlocking"
    if has("demolition"):
        return "demolition"
    if has("excavation"):
        return "excavation"
    if has("christmas", "lights"):
        return "christmas"
    if has("general-contractor", "general contractor", "contractor"):
        return "contractor"
    if has("home-renovation", "home renovation", "renovation") and "basement" not in p and "bathroom" not in p:
        return "home-renovation"
    if has("handyman"):
        return "handyman"

    return None


def ensure_svg(path: Path, title: str, subtitle: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    safe_title = title.replace("&", "&amp;")
    safe_sub = subtitle.replace("&", "&amp;")
    svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1600\" height=\"900\" viewBox=\"0 0 1600 900\">
  <defs>
    <linearGradient id=\"g\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\">
      <stop offset=\"0\" stop-color=\"#4f8cff\" stop-opacity=\"0.22\"/>
      <stop offset=\"0.55\" stop-color=\"#ffffff\" stop-opacity=\"0\"/>
      <stop offset=\"1\" stop-color=\"#ff6b35\" stop-opacity=\"0.22\"/>
    </linearGradient>
  </defs>
  <rect width=\"1600\" height=\"900\" fill=\"#ffffff\"/>
  <rect width=\"1600\" height=\"900\" fill=\"url(#g)\"/>
  <rect x=\"64\" y=\"64\" width=\"1472\" height=\"772\" rx=\"36\" fill=\"#ffffff\" fill-opacity=\"0.72\" stroke=\"#e6eaf0\" stroke-width=\"2\"/>
  <text x=\"120\" y=\"460\" font-family=\"Inter,Segoe UI,Roboto,Arial,sans-serif\" font-size=\"72\" font-weight=\"800\" fill=\"#121826\">{safe_title}</text>
  <text x=\"120\" y=\"540\" font-family=\"Inter,Segoe UI,Roboto,Arial,sans-serif\" font-size=\"34\" font-weight=\"600\" fill=\"#6b7280\">{safe_sub}</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")


def build_image_list(key: str) -> tuple[list[str], list[Path]]:
    # Returns web paths and a list of SVG files to ensure.
    ensure: list[Path] = []

    def web(name: str) -> str:
        return f"/img/services/{name}"

    if key == "deck-railings":
        # Uses existing SVG covers + one generated.
        ensure_svg(IMG_DIR / "deck-railings-5.svg", "Deck Railings", "Installation & Upgrades")
        return (
            [
                web("deck-railings-1.svg"),
                web("deck-railings-2.svg"),
                web("deck-railings-3.svg"),
                web("deck-railings-4.svg"),
                web("deck-railings-5.svg"),
            ],
            ensure,
        )

    # Prefer prefix-1..4.jpg when present; otherwise fall back to generated SVG placeholders.
    prefix = key

    extra_map = {
        "deck": "deck-user-1.jpg",
        "fence": "fence-user-1.jpg",
        "canopy": "canopy-user-1.jpg",
        "interlocking": "interlocking-user-1.jpg",
        "plumbing": "plumbing-user-1.jpg",
    }

    def slide(i: int) -> str:
        jpg_name = f"{prefix}-{i}.jpg"
        if (IMG_DIR / jpg_name).exists():
            return web(jpg_name)
        svg_name = f"{prefix}-{i}.svg"
        title = {
            "basement": "Basement Renovation",
            "bathroom": "Bathroom Renovation",
            "deck": "Deck Building",
            "fence": "Fence Installation",
            "handyman": "Handyman",
            "plumbing": "Plumbing",
            "electrical": "Electrical",
            "painting": "Painting",
            "contractor": "General Contractor",
            "carpentry": "Carpentry",
            "canopy": "Canopy & Awnings",
            "landscaping": "Landscaping",
            "interlocking": "Interlocking & Paving",
            "demolition": "Demolition",
            "excavation": "Excavation",
            "christmas": "Christmas Lights",
            "home-renovation": "Home Renovation",
        }.get(prefix, prefix.replace("-", " ").title())
        ensure_svg(IMG_DIR / svg_name, title, f"Gallery image {i}")
        return web(svg_name)

    base = [slide(1), slide(2), slide(3), slide(4)]

    extra = extra_map.get(prefix)
    if extra and (IMG_DIR / extra).exists():
        return (base + [web(extra)], ensure)

    # Generate a 5th SVG slide
    svg_name = f"{prefix}-5.svg"
    title = {
        "basement": "Basement Renovation",
        "bathroom": "Bathroom Renovation",
        "deck": "Deck Building",
        "fence": "Fence Installation",
        "handyman": "Handyman",
        "plumbing": "Plumbing",
        "electrical": "Electrical",
        "painting": "Painting",
        "contractor": "General Contractor",
        "carpentry": "Carpentry",
        "canopy": "Canopy & Awnings",
        "landscaping": "Landscaping",
        "interlocking": "Interlocking & Paving",
        "demolition": "Demolition",
        "excavation": "Excavation",
        "christmas": "Christmas Lights",
        "home-renovation": "Home Renovation",
    }.get(prefix, prefix.replace("-", " ").title())

    subtitle = "Toronto & GTA"
    ensure_svg(IMG_DIR / svg_name, title, subtitle)
    return (base + [web(svg_name)], ensure)


def build_spec(key: str) -> CarouselSpec:
    images, _ = build_image_list(key)
    title = {
        "basement": "Basement Renovation",
        "bathroom": "Bathroom Renovation",
        "deck": "Deck Building",
        "deck-railings": "Deck Railings",
        "fence": "Fence Installation",
        "handyman": "Handyman",
        "plumbing": "Plumbing",
        "electrical": "Electrical",
        "painting": "Painting",
        "contractor": "General Contractor",
        "carpentry": "Carpentry",
        "canopy": "Canopy & Awnings",
        "landscaping": "Landscaping",
        "interlocking": "Interlocking & Paving",
        "demolition": "Demolition",
        "excavation": "Excavation",
        "christmas": "Christmas Lights",
        "home-renovation": "Home Renovation",
    }.get(key, key.replace("-", " ").title())

    return CarouselSpec(key=key, title=title, images=images)


def render_carousel(spec: CarouselSpec) -> str:
    # Uses existing design tokens via CSS; inline style only for spacing, matching existing patterns.
    slides_html = []
    for idx, src in enumerate(spec.images, start=1):
        alt = f"{spec.title} photo {idx}"
        slides_html.append(
            "\n".join(
                [
                    "      <figure class=\"carousel-slide\">",
                    f"        <img src=\"{src}\" alt=\"{alt}\" loading=\"lazy\" decoding=\"async\">",
                    "      </figure>",
                ]
            )
        )

    return (
        "\n".join(
            [
                "<section id=\"service-gallery\" class=\"shell\" style=\"padding:24px 0 0;\" aria-label=\"Service gallery\">",
                "  <div class=\"carousel\" data-carousel data-carousel-total=\"5\">",
                "    <div class=\"carousel-track\" data-carousel-track>",
                *slides_html,
                "    </div>",
                "    <div class=\"carousel-controls\">",
                "      <button class=\"carousel-btn\" type=\"button\" data-carousel-prev aria-label=\"Previous image\">Prev</button>",
                "      <div class=\"carousel-dots\" data-carousel-dots aria-label=\"Choose an image\"></div>",
                "      <button class=\"carousel-btn\" type=\"button\" data-carousel-next aria-label=\"Next image\">Next</button>",
                "    </div>",
                "  </div>",
                "</section>",
            ]
        )
        + "\n"
    )


def insert_after_page_hero(html: str, block: str) -> tuple[str, bool]:
    if re.search(r"\bid=(\"|')service-gallery\1", html, flags=re.IGNORECASE):
        return html, False

    # Insert between page-hero and the main container for consistent placement.
    marker = re.search(r"</div>\s*\n\s*<div class=\"container\">", html, flags=re.IGNORECASE)
    if not marker:
        return html, False

    insert_at = marker.start()
    return html[:insert_at] + block + html[insert_at:], True


def iter_html_files() -> Iterable[Path]:
    for p in ROOT.rglob("*.html"):
        if not p.is_file():
            continue
        # Skip template folder.
        if "\\services\\" in str(p).lower():
            continue
        yield p


def main() -> None:
    updated: list[Path] = []
    svg_created: list[Path] = []

    for path in iter_html_files():
        html = path.read_text(encoding="utf-8", errors="ignore")
        if not is_service_page(html):
            continue

        key = detect_service_key(path, html)
        if not key:
            continue

        # Ensure missing SVG 5th slides exist (and for home-renovation)
        imgs, _ = build_image_list(key)
        for src in imgs:
            if src.endswith(".svg"):
                fp = ROOT / src.lstrip("/")
                if fp.exists():
                    continue
                # should have been created by ensure_svg() in build_image_list
                if fp.exists():
                    continue
                svg_created.append(fp)

        spec = build_spec(key)
        block = render_carousel(spec)
        new_html, did = insert_after_page_hero(html, block)
        if did:
            path.write_text(new_html, encoding="utf-8")
            updated.append(path)

    print("=== add_service_carousels ===")
    print(f"Root: {ROOT}")
    print(f"Service pages updated: {len(updated)}")
    print(f"SVG slides ensured: {len([p for p in IMG_DIR.glob('*-5.svg')])}")
    for p in updated[:40]:
        print("-", p.relative_to(ROOT))
    if len(updated) > 40:
        print(f"... and {len(updated) - 40} more")


if __name__ == "__main__":
    main()
