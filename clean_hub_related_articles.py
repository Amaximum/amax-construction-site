"""Filter related-articles cards on each service hub to match the hub's topic.

Rule: every card in <section id="articles"> on a service hub must be topically
tied to that hub's service. Off-topic cards are removed. If the section ends
up with zero cards, the entire section is stripped.

Run from repo root:
    python clean_hub_related_articles.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Per-hub regex of allowed substrings (matched against href + visible text, lowercased).
HUB_TOPIC = {
    "deck-builder":                            r"(deck|railing|outdoor-living)",
    "deck-railings":                           r"(railing|deck|privacy-screen)",
    "fence-installation":                      r"(fence)",
    "bathroom-renovation":                     r"(bathroom)",
    "basement-renovation":                     r"(basement)",
    "handyman-plumbing-services":              r"(plumb)",
    "canopy":                                  r"(canopy|outdoor-living)",
    "landscaping-services":                    r"(landscap|backyard|outdoor|garden)",
    "general-contractor":                      r"(general[- ]?contract|contractor[- ](?:selection|scam)|contracting|contractor-scam|contractors-industry|scammer.*contractor)",
    "handyman-services":                       r"(handyman)",
    "interlocking-paver-services":             r"(interlock|pav)",
    "carpenter-services":                      r"(carpenter|carpentry)",
    "electrical-handyman-services":            r"(electric)",
    "handyman-painting-services":              r"(paint)",
    "demolition-services":                     r"(demolit|demolish)",
    "excavation-services":                     r"(excavat)",
    "home-renovation":                         r"(home-renovation|renovation)",
    "christmas-lights-installation-toronto-gta": r"(christmas|light)",
}

# Hard-exclude: never allow these on a hub even if a topic word coincidentally matches.
HUB_EXCLUDE = {
    # On handyman hub, links to OTHER service hubs are not articles.
    "handyman-services": [
        r"^/handyman-painting-services/?\s",
        r"^/handyman-plumbing-services/?\s",
    ],
    # On excavation hub, demolition articles are a different service.
    "excavation-services": [
        r"demolit",
    ],
}

OPEN_RE = re.compile(
    r'<section[^>]*\b(?:id="articles"|class="[^"]*related-articles[^"]*")[^>]*>',
    re.I,
)


def find_articles_block(html: str) -> tuple[int, int] | None:
    m = OPEN_RE.search(html)
    if not m:
        return None
    section_open = re.compile(r"<section\b", re.I)
    section_close = re.compile(r"</section>", re.I)
    depth = 1
    pos = m.end()
    while pos < len(html):
        o = section_open.search(html, pos)
        c = section_close.search(html, pos)
        if c is None:
            break
        if o is not None and o.start() < c.start():
            depth += 1
            pos = o.end()
        else:
            depth -= 1
            pos = c.end()
            if depth == 0:
                return m.start(), pos
    return None


# Match a single <a class="card" ...>...</a>
CARD_RE = re.compile(
    r'<a\b[^>]*\bclass="card"[^>]*>.*?</a>',
    re.I | re.S,
)
HREF_RE = re.compile(r'href="([^"]+)"', re.I)


def card_passes(card_html: str, topic_re: re.Pattern[str],
                excludes: list[re.Pattern[str]]) -> bool:
    href_m = HREF_RE.search(card_html)
    href = (href_m.group(1) if href_m else "").lower()
    text = re.sub(r"<[^>]+>", " ", card_html).lower()
    blob = href + " " + text
    for ex in excludes:
        if ex.search(blob):
            return False
    return bool(topic_re.search(blob))


def process_hub(hub: str) -> tuple[bool, int, int, bool]:
    """Returns (modified, kept, removed, section_stripped)."""
    path = ROOT / hub / "index.html"
    if not path.exists():
        return False, 0, 0, False
    html = path.read_text(encoding="utf-8")
    span = find_articles_block(html)
    if span is None:
        return False, 0, 0, False
    start, end = span
    block = html[start:end]

    topic_re = re.compile(HUB_TOPIC[hub], re.I)
    excludes = [re.compile(p, re.I) for p in HUB_EXCLUDE.get(hub, [])]

    cards = CARD_RE.findall(block)
    if not cards:
        return False, 0, 0, False

    kept = 0
    removed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal kept, removed
        c = m.group(0)
        if card_passes(c, topic_re, excludes):
            kept += 1
            return c
        removed += 1
        return ""

    new_block = CARD_RE.sub(repl, block)
    section_stripped = False

    if kept == 0:
        # Strip the whole section.
        new_html = html[:start] + html[end:]
        section_stripped = True
    elif removed == 0:
        return False, kept, 0, False
    else:
        # Tidy up whitespace inside .cards
        new_html = html[:start] + new_block + html[end:]

    path.write_bytes(new_html.encode("utf-8"))
    return True, kept, removed, section_stripped


def main() -> None:
    total_removed = 0
    total_stripped = 0
    for hub in HUB_TOPIC:
        changed, kept, removed, stripped = process_hub(hub)
        marker = " (section dropped)" if stripped else ""
        if changed:
            print(f"[FIX] {hub}: kept {kept}, removed {removed}{marker}")
            total_removed += removed
            if stripped:
                total_stripped += 1
        else:
            print(f"[ok ] {hub}: kept {kept}")
    print(f"\nTotal off-topic cards removed: {total_removed}")
    print(f"Sections entirely dropped: {total_stripped}")


if __name__ == "__main__":
    main()
