"""
Mark form/utility pages as noindex and remove them from sitemap.xml.
- All root-level book-*.html
- /book-now/index.html
- /thank-you-page/index.html
- /sitemap/index.html

Live content (services, locations, blog, hubs) is kept indexable.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITEMAP = ROOT / "sitemap.xml"

# Build the list of form/utility files to mark noindex.
targets: list[Path] = []
targets += sorted(ROOT.glob("book-*.html"))
for sub in ("book-now", "thank-you-page", "sitemap"):
    p = ROOT / sub / "index.html"
    if p.exists():
        targets.append(p)

# URLs (relative paths) to strip from sitemap.
strip_urls: set[str] = set()
for sub in ("book-now", "thank-you-page", "sitemap"):
    strip_urls.add(f"https://amaximumconstruction.com/{sub}/")
for f in ROOT.glob("book-*.html"):
    strip_urls.add(f"https://amaximumconstruction.com/{f.name}")


ROBOTS_RE = re.compile(r'<meta\s+name="robots"\s+content="[^"]*"\s*/?>', re.I)


def ensure_noindex(text: str) -> tuple[str, bool]:
    """Replace existing robots meta with noindex,follow, or insert before </head>."""
    new_meta = '<meta name="robots" content="noindex, follow">'
    if ROBOTS_RE.search(text):
        new_text = ROBOTS_RE.sub(new_meta, text, count=1)
    elif "</head>" in text:
        new_text = text.replace("</head>", f"  {new_meta}\n</head>", 1)
    else:
        return text, False
    return new_text, new_text != text


changed_files: list[str] = []
for f in targets:
    text = f.read_text(encoding="utf-8", errors="ignore")
    new_text, did = ensure_noindex(text)
    if did:
        f.write_bytes(new_text.encode("utf-8"))
        changed_files.append(str(f.relative_to(ROOT).as_posix()))

# Strip <url> blocks whose <loc> is in strip_urls.
sm = SITEMAP.read_text(encoding="utf-8")
removed = 0
for url in strip_urls:
    pattern = re.compile(
        r"\s*<url>\s*<loc>" + re.escape(url) + r"</loc>.*?</url>",
        re.DOTALL,
    )
    new_sm, n = pattern.subn("", sm)
    if n:
        sm = new_sm
        removed += n
SITEMAP.write_bytes(sm.encode("utf-8"))

print(f"Marked noindex on {len(changed_files)} pages:")
for c in changed_files:
    print("  -", c)
print(f"Removed {removed} entries from sitemap.")
