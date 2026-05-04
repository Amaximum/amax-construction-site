"""Insert a 'Near Me' location-card into all handyman service-locations grids."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# Find all handyman pages with service-locations grid
candidates = []
for p in ROOT.glob("handyman-service*/index.html"):
    candidates.append(p)
for p in ROOT.glob("handyman-services-*/index.html"):
    candidates.append(p)
candidates.append(ROOT / "handyman-services" / "index.html")

# Skip the near-me page itself (already self) and vaughan inside main/ (already added)
SKIP = {
    ROOT / "main" / "trusted-local-handyman-services" / "handyman-service-near-me" / "index.html",
}

NEAR_ME_HREF = "/main/trusted-local-handyman-services/handyman-service-near-me/"
NEAR_ME_LINK_RE = re.compile(re.escape(NEAR_ME_HREF))

# Two card formats observed in the codebase
CARD_NEW = (
    f'    <a href="{NEAR_ME_HREF}" class="location-card">Near Me</a>\n'
)
CARD_COMPACT = (
    f'<a class="location-card" href="{NEAR_ME_HREF}">Near Me</a>\n'
)

# Match a location-grid block (not service-card grids)
GRID_RE = re.compile(
    r'(<div class="location-grid">)(.*?)(</div>)',
    re.DOTALL,
)

# Newmarket card line (both formats)
NEWMARKET_RE = re.compile(
    r'(^[ \t]*<a[^>]*?href="/handyman-service-in-newmarket/"[^>]*>Newmarket</a>\s*\n)',
    re.MULTILINE,
)

changed = []
for path in sorted(set(candidates)):
    if path in SKIP or not path.exists():
        continue
    src = path.read_text(encoding="utf-8")

    def process_grid(m):
        grid_inner = m.group(2)
        # Only operate if this grid contains handyman-service location cards
        if "/handyman-service" not in grid_inner and "/handyman-services-" not in grid_inner:
            return m.group(0)
        if NEAR_ME_LINK_RE.search(grid_inner):
            return m.group(0)
        # Decide card style based on existing format inside grid
        compact = bool(re.search(r'<a class="location-card"', grid_inner))
        card = CARD_COMPACT if compact else CARD_NEW
        # Insert before the Newmarket card if present, else at end
        new_inner, n = NEWMARKET_RE.subn(card + r"\1", grid_inner, count=1)
        if n == 0:
            # Append at end (before closing </div>)
            new_inner = grid_inner.rstrip() + "\n" + card
        return m.group(1) + new_inner + m.group(3)

    new_src = GRID_RE.sub(process_grid, src)
    if new_src != src:
        path.write_text(new_src, encoding="utf-8")
        changed.append(path)

print(f"Updated {len(changed)} files:")
for p in changed:
    print(" -", p.relative_to(ROOT))
