# -*- coding: utf-8 -*-
"""
Remove Toronto-city emphasis from service HUB pages, leaving the focus on
GTA / Greater Toronto Area. Protects: site footer, location cards, blog cards
with Toronto-themed slugs, spoke-page links containing 'toronto', JSON-LD
addressLocality, and any anchor whose href contains 'toronto'.

Applies to all hub index.html pages (the 19 hubs besides deck-builder, which
was already processed manually).
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent

HUBS = [
    "deck-railings",
    "fence-installation",
    "bathroom-renovation",
    "basement-renovation",
    "handyman-plumbing-services",
    "canopy",
    "landscaping-services",
    "general-contractor",
    "handyman-services",
    "interlocking-paver-services",
    "carpenter-services",
    "electrical-handyman-services",
    "handyman-painting-services",
    "demolition-services",
    "excavation-services",
    "home-renovation",
    "christmas-lights-installation-toronto-gta",
    "handyman-drywall-repair",
    "handyman-furniture-assembly",
]

# Patterns of regions to PROTECT (leave Toronto mentions untouched).
# Order matters: bigger blocks first.
PROTECT_PATTERNS = [
    # Whole footer
    re.compile(r"<footer\b.*?</footer>", re.IGNORECASE | re.DOTALL),
    # JSON-LD addressLocality (postal address of business)
    re.compile(r'"addressLocality"\s*:\s*"Toronto"'),
    # Any anchor whose href contains 'toronto' (location cards, spoke links,
    # blog cards with toronto in slug, related-articles cards)
    re.compile(r'<a\b[^>]*href="[^"]*toronto[^"]*"[^>]*>.*?</a>',
               re.IGNORECASE | re.DOTALL),
]

# Replacements applied to the unprotected text only. Order matters.
REPLACEMENTS = [
    # Title/meta variants
    (re.compile(r"Toronto\s*&amp;amp;\s*GTA"), "GTA"),
    (re.compile(r"Toronto\s*&amp;\s*GTA"), "GTA"),
    (re.compile(r"Toronto\s*&\s*GTA"), "GTA"),
    (re.compile(r"Toronto,\s*GTA"), "GTA"),
    # Service schema name like "Toronto & GTA" (already handled above)
    # Prose patterns
    (re.compile(r"across Toronto and the Greater Toronto Area"),
     "across the Greater Toronto Area"),
    (re.compile(r"in Toronto and the Greater Toronto Area"),
     "across the Greater Toronto Area"),
    (re.compile(r"throughout Toronto and the GTA"), "throughout the GTA"),
    (re.compile(r"Toronto and the GTA"), "the GTA"),
    (re.compile(r"\bToronto and surrounding areas\b"), "the GTA"),
    (re.compile(r"\bToronto building codes\b"), "GTA building codes"),
    (re.compile(r"\bToronto weather\b"), "GTA weather"),
    (re.compile(r"\bToronto winters\b"), "GTA winters"),
    (re.compile(r"\bToronto homeowners\b"), "GTA homeowners"),
    (re.compile(r"\bToronto homes\b"), "GTA homes"),
    (re.compile(r"\bToronto properties\b"), "GTA properties"),
    (re.compile(r"\bToronto neighbourhoods\b"), "GTA neighbourhoods"),
    (re.compile(r"\bToronto bylaws\b"), "GTA bylaws"),
    (re.compile(r"\bToronto permits\b"), "GTA permits"),
    (re.compile(r"\bToronto area\b"), "GTA"),
    (re.compile(r"\bGreater Toronto Area\b"), "Greater Toronto Area"),  # noop, safety
    (re.compile(r"\bserving Toronto\b"), "serving the GTA"),
    # Generic: "in Toronto" → "in the GTA" (after the above more specific rules)
    (re.compile(r"\bin Toronto\b(?!\s*and the Greater)"), "in the GTA"),
    # "for Toronto" → "for the GTA"
    (re.compile(r"\bfor Toronto\b"), "for the GTA"),
    # "across Toronto" → "across the GTA"
    (re.compile(r"\bacross Toronto\b"), "across the GTA"),
    # Bare "Toronto" inside questions: "cost in Toronto?" already handled.
]


def protect(text: str):
    """Replace protected regions with placeholders; return (masked_text, mapping)."""
    mapping = {}
    counter = [0]

    def stash(m):
        counter[0] += 1
        key = f"\x00PROTECT_{counter[0]}\x00"
        mapping[key] = m.group(0)
        return key

    for pat in PROTECT_PATTERNS:
        text = pat.sub(stash, text)
    return text, mapping


def restore(text: str, mapping: dict) -> str:
    for key, original in mapping.items():
        text = text.replace(key, original)
    return text


def process(slug: str) -> tuple[bool, int, list[str]]:
    f = ROOT / slug / "index.html"
    if not f.exists():
        return False, 0, [f"NOT FOUND: {f}"]
    original = f.read_text(encoding="utf-8")
    masked, mapping = protect(original)

    new = masked
    applied = []
    for pat, repl in REPLACEMENTS:
        new2, n = pat.subn(repl, new)
        if n:
            applied.append(f"{pat.pattern} x{n}")
        new = new2

    restored = restore(new, mapping)
    if restored == original:
        return True, 0, ["no changes"]

    # Count remaining Toronto mentions for reporting
    remaining = len(re.findall(r"\bToronto\b", restored))
    f.write_bytes(restored.encode("utf-8"))
    return True, len(applied), applied + [f"remaining 'Toronto' mentions (protected/expected): {remaining}"]


def main():
    print(f"Processing {len(HUBS)} hub pages...\n")
    for slug in HUBS:
        ok, n, notes = process(slug)
        flag = "OK" if ok else "FAIL"
        print(f"[{flag}] {slug}  ({n} pattern groups applied)")
        for line in notes:
            print(f"    - {line}")
        print()


if __name__ == "__main__":
    main()
