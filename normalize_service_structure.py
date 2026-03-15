import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


WHY_CHOOSE_US_SECTION = """<section id=\"why-choose-us\" class=\"island reveal\" style=\"margin-top:18px;\" aria-label=\"Why choose us\">
    <span class=\"shine\" aria-hidden=\"true\"></span>
    <div class=\"section-head\">
        <h2>Why Choose aMaximum Construction?</h2>
        <p>We are a licensed and insured general contractor serving Toronto and the GTA since 2018.</p>
    </div>
    <div class=\"cards\">
        <div class=\"card\">
            <div class=\"icon\">✅</div>
            <h3>Licensed &amp; Insured</h3>
            <p>WSIB clearance, $2M liability insurance, and all permits handled. You are protected from start to finish.</p>
        </div>
        <div class=\"card\">
            <div class=\"icon\">📋</div>
            <h3>Clear Scope &amp; Fixed Price</h3>
            <p>Detailed written quote before any work begins. No hidden fees, no surprise invoices at the end.</p>
        </div>
        <div class=\"card\">
            <div class=\"icon\">🏆</div>
            <h3>One Point of Contact</h3>
            <p>We coordinate all trades under one contract. You deal with us — not a dozen different contractors.</p>
        </div>
        <div class=\"card\">
            <div class=\"icon\">⏱️</div>
            <h3>On Time &amp; On Budget</h3>
            <p>Milestone-based schedule with regular updates. We show up when we say we will and finish when we say we will.</p>
        </div>
        <div class=\"card\">
            <div class=\"icon\">🔨</div>
            <h3>Quality Workmanship</h3>
            <p>Written warranty on all work. We use quality materials and back every job with a workmanship guarantee.</p>
        </div>
        <div class=\"card\">
            <div class=\"icon\">🤝</div>
            <h3>Respectful &amp; Tidy</h3>
            <p>Clean jobsite every day. We treat your home with respect — no mess left behind, no damage to surroundings.</p>
        </div>
    </div>
</section>"""


SECTION_RE_TEMPLATE = r"<section\b[^>]*\bid=(?:\"|'){id}(?:\"|')[^>]*>.*?</section>"


def _extract_first_section(html: str, section_id: str) -> tuple[str, str, str] | None:
    pattern = re.compile(SECTION_RE_TEMPLATE.format(id=re.escape(section_id)), re.IGNORECASE | re.DOTALL)
    match = pattern.search(html)
    if not match:
        return None
    return html[: match.start()], match.group(0), html[match.end() :]


def _remove_first_section(html: str, section_id: str) -> tuple[str, bool]:
    extracted = _extract_first_section(html, section_id)
    if not extracted:
        return html, False
    before, _section, after = extracted
    return before + after, True


def _move_section_before(html: str, moving_id: str, anchor_id: str) -> tuple[str, bool]:
    moving = _extract_first_section(html, moving_id)
    anchor = _extract_first_section(html, anchor_id)
    if not moving or not anchor:
        return html, False

    # If it's already before the anchor, don't touch (idempotent behavior).
    moving_pos = len(moving[0])
    anchor_pos = len(anchor[0])
    if moving_pos < anchor_pos:
        return html, False

    before_m, moving_section, after_m = moving

    html_without_moving = before_m + after_m
    anchor2 = _extract_first_section(html_without_moving, anchor_id)
    if not anchor2:
        return html, False

    before_a, anchor_section, after_a = anchor2

    # Insert moving section immediately before the anchor section
    new_html = before_a + moving_section + "\n" + anchor_section + after_a
    return new_html, True


def _rename_related_articles_to_blogs(section_html: str) -> str:
    # id
    section_html = re.sub(
        r"\bid=(\"|')related-articles(\"|')",
        r"id=\1related-blogs\2",
        section_html,
        flags=re.IGNORECASE,
    )
    # heading text (keep style)
    section_html = section_html.replace(">Related Articles<", ">Related Blog Posts<")
    return section_html


def _extract_why_choose_us(html: str) -> tuple[str, str, str] | None:
    # Prefer id match
    section_id_match = _extract_first_section(html, "why-choose-us")
    if section_id_match:
        return section_id_match

    # Fallback: aria-label="Why choose us" island section
    pattern = re.compile(
        r"<section\b[^>]*aria-label=(?:\"|')Why choose us(?:\"|')[^>]*>.*?</section>",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return None
    return html[: match.start()], match.group(0), html[match.end() :]


def _ensure_why_choose_us_id(section_html: str) -> tuple[str, bool]:
    if re.search(r"\bid=(\"|')why-choose-us\1", section_html, flags=re.IGNORECASE):
        return section_html, False
    updated = re.sub(
        r"<section\b", "<section id=\"why-choose-us\"", section_html, count=1, flags=re.IGNORECASE
    )
    return updated, True


def _remove_duplicate_why_choose_us(html: str) -> tuple[str, bool]:
    # Remove all but the first occurrence.
    pattern = re.compile(
        r"<section\b[^>]*aria-label=(?:\"|')Why choose us(?:\"|')[^>]*>.*?</section>",
        re.IGNORECASE | re.DOTALL,
    )
    matches = list(pattern.finditer(html))
    if len(matches) <= 1:
        return html, False
    # Keep the first, remove the rest.
    new_html = html
    removed_any = False
    for m in reversed(matches[1:]):
        new_html = new_html[: m.start()] + new_html[m.end() :]
        removed_any = True
    return new_html, removed_any


def _ensure_service_areas_id(html: str) -> tuple[str, bool]:
    if re.search(r"<section\b[^>]*\bid=(\"|')service-areas\1", html, flags=re.IGNORECASE):
        return html, False

    # Find the first <section ...>...</section> that contains an H2 with "Near You" and a list of location links.
    section_re = re.compile(r"<section\b[^>]*>.*?</section>", re.IGNORECASE | re.DOTALL)
    for match in section_re.finditer(html):
        section = match.group(0)
        if re.search(r"<h2[^>]*>[^<]*Near You</h2>", section, flags=re.IGNORECASE):
            if re.search(r"<ul[^>]*>.*?<li>\s*<a\s+href=", section, flags=re.IGNORECASE | re.DOTALL):
                # Add id="service-areas" to the opening <section ...>
                updated = re.sub(
                    r"<section\b(?![^>]*\bid=)",
                    '<section id="service-areas"',
                    section,
                    count=1,
                    flags=re.IGNORECASE,
                )
                new_html = html[: match.start()] + updated + html[match.end() :]
                return new_html, True

    return html, False


def normalize_service_page(html: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    # Only touch service/service+location pages (avoid blog pages).
    # Require JSON-LD `serviceType` to avoid touching general pages that happen
    # to share the hero/CTA/reviews layout (e.g. /why-choose-us/, /what-we-do/).
    is_service = (
        ("class=\"page-hero\"" in html)
        and ("class=\"cta-section\"" in html)
        and ("id=\"reviews-embed\"" in html)
        and ("class=\"blog-hero\"" not in html)
        and ("\"serviceType\"" in html)
    )
    if not is_service:
        return html, changes

    html2, did = _ensure_service_areas_id(html)
    if did:
        changes.append("add service-areas id")
    html = html2

    has_related_blogs = re.search(r"\bid=(\"|')related-blogs\1", html, flags=re.IGNORECASE) is not None
    has_related_articles = re.search(r"\bid=(\"|')related-articles\1", html, flags=re.IGNORECASE) is not None

    if has_related_articles and has_related_blogs:
        html, removed = _remove_first_section(html, "related-articles")
        if removed:
            changes.append("remove related-articles")
    elif has_related_articles and not has_related_blogs:
        extracted = _extract_first_section(html, "related-articles")
        if extracted:
            before, section, after = extracted
            section2 = _rename_related_articles_to_blogs(section)
            html = before + section2 + after
            changes.append("rename related-articles -> related-blogs")
            has_related_blogs = True

    # Enforce ordering: related-blogs directly before reviews-embed
    if has_related_blogs and re.search(r"\bid=(\"|')reviews-embed\1", html, flags=re.IGNORECASE):
        html, moved = _move_section_before(html, "related-blogs", "reviews-embed")
        if moved:
            changes.append("move related-blogs before reviews-embed")

    # Ensure service-areas comes before related-blogs/reviews (when present)
    if re.search(r"\bid=(\"|')service-areas\1", html, flags=re.IGNORECASE):
        anchor = "related-blogs" if re.search(r"\bid=(\"|')related-blogs\1", html, flags=re.IGNORECASE) else "reviews-embed"
        html, moved = _move_section_before(html, "service-areas", anchor)
        if moved:
            changes.append(f"move service-areas before {anchor}")

    # Ensure a single standardized Why choose us section exists and is positioned before related-blogs/reviews
    html, removed_dupes = _remove_duplicate_why_choose_us(html)
    if removed_dupes:
        changes.append("remove duplicate why-choose-us")

    why = _extract_why_choose_us(html)
    if not why:
        # Insert before related-blogs if present else reviews-embed
        anchor = "related-blogs" if re.search(r"\bid=(\"|')related-blogs\1", html, flags=re.IGNORECASE) else "reviews-embed"
        anchor_ex = _extract_first_section(html, anchor)
        if anchor_ex:
            before_a, anchor_section, after_a = anchor_ex
            html = before_a + WHY_CHOOSE_US_SECTION + "\n" + anchor_section + after_a
            changes.append("insert why-choose-us")
    else:
        before_w, why_section, after_w = why
        why_section2, did_id = _ensure_why_choose_us_id(why_section)
        if did_id:
            changes.append("add why-choose-us id")
        html = before_w + why_section2 + after_w

        # Move why-choose-us before related-blogs if present else reviews-embed
        anchor = "related-blogs" if re.search(r"\bid=(\"|')related-blogs\1", html, flags=re.IGNORECASE) else "reviews-embed"
        html, moved = _move_section_before(html, "why-choose-us", anchor)
        if moved:
            changes.append(f"move why-choose-us before {anchor}")

    # Ensure ordering: reviews-embed before faq (if both present)
    if re.search(r"\bid=(\"|')reviews-embed\1", html, flags=re.IGNORECASE) and re.search(
        r"\bid=(\"|')faq\1", html, flags=re.IGNORECASE
    ):
        # If faq occurs before reviews, swap by moving faq after reviews
        reviews_pos = re.search(r"\bid=(\"|')reviews-embed\1", html, flags=re.IGNORECASE)
        faq_pos = re.search(r"\bid=(\"|')faq\1", html, flags=re.IGNORECASE)
        if reviews_pos and faq_pos and faq_pos.start() < reviews_pos.start():
            faq = _extract_first_section(html, "faq")
            reviews = _extract_first_section(html, "reviews-embed")
            if faq and reviews:
                before_f, faq_section, after_f = faq
                html_wo_faq = before_f + after_f
                reviews2 = _extract_first_section(html_wo_faq, "reviews-embed")
                if reviews2:
                    before_r, reviews_section, after_r = reviews2
                    # Put faq right after reviews
                    html = before_r + reviews_section + "\n" + faq_section + after_r
                    changes.append("move faq after reviews-embed")

    return html, changes


def main() -> None:
    html_files = [p for p in ROOT.rglob("*.html") if p.is_file()]

    changed_files: list[tuple[Path, list[str]]] = []

    for path in html_files:
        try:
            html = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            html = path.read_text(encoding="utf-8", errors="ignore")

        new_html, changes = normalize_service_page(html)
        if changes and new_html != html:
            path.write_text(new_html, encoding="utf-8")
            changed_files.append((path, changes))

    print("=== normalize_service_structure ===")
    print(f"Root: {ROOT}")
    print(f"Service pages updated: {len(changed_files)}")
    for p, changes in changed_files[:40]:
        rel = p.relative_to(ROOT)
        print(f"- {rel} :: {', '.join(changes)}")
    if len(changed_files) > 40:
        print(f"... and {len(changed_files) - 40} more")


if __name__ == "__main__":
    main()
