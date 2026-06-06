"""Validate a rewritten article (top-level slug or /blog/<slug>/).

Usage: python _blog_qa2.py <slug>
  - <slug> can be 'avoid-handyman-scams' or 'blog/plumbing-emergency-guide'
"""
import json, re, pathlib, sys

slug = sys.argv[1] if len(sys.argv) > 1 else "3-easy-ways-to-care-for-your-deck-so-it-always-looks-great"
p = pathlib.Path(slug) / "index.html"
if not p.exists():
    print(f"!! NOT FOUND: {p}")
    sys.exit(1)
html = p.read_text(encoding="utf-8")

print(f"=== {slug} ===")
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
graph_types = []
for i, b in enumerate(blocks, 1):
    try:
        d = json.loads(b)
        if isinstance(d, dict) and "@graph" in d:
            for g in d["@graph"]:
                graph_types.append(g.get("@type"))
        else:
            graph_types.append(d.get("@type"))
    except Exception as e:
        print(f"  !! JSON parse error block {i}: {e}")
print(f"  JSON-LD @types: {graph_types}")

ids = re.findall(r'<h2 id="([^"]+)"', html)
print(f"  H2 ids ({len(ids)}): {ids}")

toc_match = re.search(r'<nav class="toc"[^>]*>(.*?)</nav>', html, re.S)
if toc_match:
    hrefs = re.findall(r'href="#([^"]+)"', toc_match.group(1))
    missing = [h for h in hrefs if h not in ids]
    print(f"  TOC anchors {len(hrefs)} -> missing: {missing or 'none'}")
else:
    print("  TOC: NOT FOUND")

_moji = re.findall(r'">\?\?+<', html)
print(f"  Mojibake: {len(_moji)}")

# body words: from article-body or content div
m = re.search(r'<div class="article-body">(.*?)</div>\s*</div>\s*<', html, re.S)
if not m:
    m = re.search(r'<div class="content">(.*?)</div>\s*<div class="cta-section">', html, re.S)
if m:
    text = re.sub(r'<[^>]+>', ' ', m.group(1))
    words = [w for w in re.split(r'\s+', text) if re.search(r'\w', w)]
    print(f"  Body words: {len(words)}")
else:
    print("  Body words: COULD NOT EXTRACT")

m = re.search(r'href="(/book-[^"]+\.html)"', html)
print(f"  Book CTA href: {m.group(1) if m else 'MISSING'}")

t = re.search(r'<title>([^<]+)</title>', html)
title = t.group(1) if t else "MISSING"
h = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
h1 = h.group(1) if h else "MISSING"
print(f"  Title ({len(title)}): {title}")
print(f"  H1: {h1}")

flags = {
    'key-takeaways': bool(re.search(r'class="key-takeaways"', html)),
    'toc': bool(re.search(r'class="toc"', html)),
    'author-block': bool(re.search(r'class="author-block"', html)),
    'sources': bool(re.search(r'class="sources"', html)),
    'callouts': len(re.findall(r'class="callout', html)),
}
print("  Flags:", flags)

ai_phrases = ["In this article", "Let's dive in", "In conclusion", "It's important to note",
              "Stay tuned", "navigate the complexities", "delve into", "in today's fast-paced",
              "Whether you're a homeowner", "When it comes to"]
hits = [phr for phr in ai_phrases if phr.lower() in html.lower()]
print(f"  AI-pattern hits: {hits or 'none'}")
