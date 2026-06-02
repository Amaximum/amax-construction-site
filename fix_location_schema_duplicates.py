#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

TARGETS = [
    "deck-builder-gta/index.html",
    "deck-builder-schomberg/index.html",
    "deck-builder-toronto/index.html",
    "deck-contractor-bradford/index.html",
    "deck-contractor-burlington/index.html",
    "deck-contractor-hamilton/index.html",
    "deck-contractor-scarborough/index.html",
    "deck-contractor-woodbridge/index.html",
    "fence-contractor-in-toronto/index.html",
    "plumbing-services-in-toronto/index.html",
    "plumbing-services-in-markham/index.html",
    "plumbing-services-in-vaughan/index.html",
    "plumbing-services-in-newmarket/index.html",
    "plumbing-services-in-richmond-hill/index.html",
]

CANONICAL_RE = re.compile(
    r"<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>\s*"
    r"|<link\b[^>]*\bhref=[\"'][^\"']+[\"'][^>]*\brel=[\"']canonical[\"'][^>]*>\s*",
    flags=re.IGNORECASE,
)
SCRIPT_RE = re.compile(
    r"<script\s+type=[\"']application/ld\+json[\"']>\s*.*?</script>\s*",
    flags=re.IGNORECASE | re.DOTALL,
)


def dedupe_canonical(html: str) -> str:
    href = None
    href_match = re.search(
        r"<link\b[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*\brel=[\"']canonical[\"'][^>]*>"
        r"|<link\b[^>]*\brel=[\"']canonical[\"'][^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>",
        html,
        flags=re.IGNORECASE,
    )
    if href_match:
        href = href_match.group(1) or href_match.group(2)

    if not href:
        og_url = re.search(
            r"<meta\s+[^>]*property=[\"']og:url[\"'][^>]*content=[\"']([^\"']+)[\"'][^>]*>",
            html,
            flags=re.IGNORECASE,
        )
        if og_url:
            href = og_url.group(1)

    without = CANONICAL_RE.sub("", html)
    if not href:
        return without

    canon_tag = f'<link rel="canonical" href="{href}">\n'
    return without.replace("</head>", canon_tag + "</head>", 1)


def dedupe_faq_schema(html: str) -> tuple[str, int]:
    blocks = list(SCRIPT_RE.finditer(html))
    faq_idx = []
    for i, m in enumerate(blocks):
        if re.search(r'"@type"\s*:\s*"FAQPage"', m.group(0), flags=re.IGNORECASE):
            faq_idx.append(i)

    if len(faq_idx) <= 1:
        return html, len(faq_idx)

    keep = faq_idx[0]
    out = []
    last = 0
    for i, m in enumerate(blocks):
        out.append(html[last : m.start()])
        if i == keep or i not in faq_idx:
            out.append(m.group(0))
        last = m.end()
    out.append(html[last:])
    return "".join(out), 1


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_faq_schema_from_html(html: str) -> str | None:
    sec_match = re.search(
        r"<section[^>]*id=[\"']faq[\"'][^>]*>.*?</section>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not sec_match:
        return None

    section = sec_match.group(0)
    detail_matches = re.findall(
        r"<details[^>]*>.*?<summary>(.*?)</summary>.*?<p>(.*?)</p>.*?</details>",
        section,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not detail_matches:
        return None

    main_entity = []
    for summary_html, answer_html in detail_matches:
        q = strip_tags(summary_html)
        a = strip_tags(answer_html)
        if not q or not a:
            continue
        main_entity.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )

    if not main_entity:
        return None

    obj = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity,
    }
    data = json.dumps(obj, ensure_ascii=True, separators=(",", ": "))
    return (
        '<script type="application/ld+json">\n'
        f"{data}\n"
        "</script>\n"
    )


def inject_faq_schema_if_missing(html: str, faq_count: int) -> str:
    if faq_count > 0:
        return html

    schema = build_faq_schema_from_html(html)
    if not schema:
        return html

    return html.replace("</head>", schema + "</head>", 1)


def process_file(rel_path: str) -> bool:
    path = ROOT / rel_path
    if not path.exists():
        print(f"[miss] {rel_path}")
        return False

    src = path.read_text(encoding="utf-8")
    out = src

    out = dedupe_canonical(out)
    out, faq_count = dedupe_faq_schema(out)
    out = inject_faq_schema_if_missing(out, faq_count)

    if out == src:
        print(f"[skip] {rel_path}")
        return False

    path.write_text(out, encoding="utf-8")
    print(f"[ok]   {rel_path}")
    return True


def main() -> None:
    changed = 0
    for rel in TARGETS:
        if process_file(rel):
            changed += 1
    print(f"Done. {changed}/{len(TARGETS)} files updated.")


if __name__ == "__main__":
    main()
