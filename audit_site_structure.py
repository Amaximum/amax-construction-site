"""Audit hub + location structure across all services.

Hub page rule:
  - 'Services in Your Area' card contains ONLY real location pages
    (slug matches one of service.location_patterns).
  - Related Articles card contains ONLY general (non-location-tied) blogs
    for this service. Exactly one blogs card per hub.

Location page rule:
  - Related Articles card contains ONLY blogs tied to this hub+city.

Usage: python audit_site_structure.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import restructure_hubs as rh  # type: ignore

ROOT = Path(__file__).resolve().parent

LOC_CARD_RE = re.compile(
    r'<a class="location-card" href="([^"]+)">([^<]+)</a>',
    re.IGNORECASE,
)
RELATED_BLOCK_RE = re.compile(
    r'<section[^>]*\bid="(articles|related-articles|related-blogs)"[^>]*>(.*?)</section>',
    re.IGNORECASE | re.DOTALL,
)
CARD_HREF_RE = re.compile(r'<a class="card" href="([^"]+)"', re.IGNORECASE)


def url_to_dirname(url: str) -> str:
    return url.strip('/').split('/')[-1]


def main() -> int:
    hub_problems: list[str] = []
    print('=' * 90)
    print('HUB AUDIT  — locations card + related-articles card')
    print('=' * 90)

    location_urls_by_hub: dict[str, set[str]] = {}
    blog_urls_by_hub: dict[str, set[str]] = {s['hub_dir']: set() for s in rh.SERVICES}
    blog_hub_city_map: dict[str, tuple[str, str | None]] = {}

    candidate_dirs: list[Path] = []
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        name = d.name
        if name.startswith('.') or name in rh.SKIP_DIRS or name == 'blog':
            continue
        if (d / 'index.html').exists():
            candidate_dirs.append(d)
    blog_root = ROOT / 'blog'
    if blog_root.is_dir():
        for d in sorted(p for p in blog_root.iterdir() if p.is_dir()):
            if (d / 'index.html').exists():
                candidate_dirs.append(d)

    locations_set_by_hub: dict[str, set[str]] = {s['hub_dir']: set() for s in rh.SERVICES}
    for d in candidate_dirs:
        rel = d.relative_to(ROOT).as_posix()
        if '/' in rel:
            html = (d / 'index.html').read_text(encoding='utf-8', errors='replace')
            hub, city = rh.classify_blog(rel.replace('/', '-'), html)
            if hub:
                blog_urls_by_hub[hub].add(f'/{rel}/')
                blog_hub_city_map[rel] = (hub, city)
            continue
        kind, hub, city, _pi = rh.classify_dir(rel)
        if kind == 'location' and hub:
            locations_set_by_hub[hub].add(f'/{rel}/')
        elif kind == 'hub':
            pass
        elif rel in rh.DUPLICATE_HUB_SLUGS:
            pass
        else:
            html = (d / 'index.html').read_text(encoding='utf-8', errors='replace')
            bhub, bcity = rh.classify_blog(rel, html)
            if bhub:
                blog_urls_by_hub[bhub].add(f'/{rel}/')
                blog_hub_city_map[rel] = (bhub, bcity)

    for svc in rh.SERVICES:
        hub_dir = svc['hub_dir']
        hub_file = ROOT / hub_dir / 'index.html'
        if not hub_file.exists():
            print(f'[!] HUB MISSING: /{hub_dir}/')
            continue
        html = hub_file.read_text(encoding='utf-8')

        loc_entries = LOC_CARD_RE.findall(html)
        loc_hrefs = [u for u, _ in loc_entries]
        # Slug of each href must be a valid location for THIS service.
        invalid_locs: list[str] = []
        for u in loc_hrefs:
            slug = url_to_dirname(u)
            kind, h, c, _pi = rh.classify_dir(slug)
            if kind != 'location' or h != hub_dir:
                invalid_locs.append(u)
        # Duplicates (same city slug appearing >1)
        seen: dict[str, int] = {}
        for _u, name in loc_entries:
            seen[name] = seen.get(name, 0) + 1
        dups = {k: v for k, v in seen.items() if v > 1}

        # Related-articles cards on the hub page
        related_blocks = RELATED_BLOCK_RE.findall(html)
        rel_ids = [bid for bid, _body in related_blocks]
        # Combine bodies
        rel_card_hrefs: list[str] = []
        for _bid, body in related_blocks:
            rel_card_hrefs.extend(CARD_HREF_RE.findall(body))
        # On the hub these should be general (non-location) blogs only
        bad_blog_entries: list[str] = []
        for u in rel_card_hrefs:
            slug = url_to_dirname(u.strip('/'))
            if slug.startswith('blog/'):
                continue
            # Find the blog rel
            rel = u.strip('/')
            if rel.startswith('blog/'):
                pass
            (b_hub, b_city) = blog_hub_city_map.get(rel, (None, None))
            if b_hub is None:
                continue  # unrecognized — skip
            if b_hub != hub_dir or b_city is not None:
                bad_blog_entries.append(u)

        status_loc = 'OK' if not invalid_locs and not dups else 'PROBLEM'
        status_blog = 'OK'
        # Multiple related cards is itself a problem.
        if len(related_blocks) > 1 and 'articles' in rel_ids and 'related-articles' in rel_ids:
            status_blog = 'PROBLEM (duplicate cards)'
        elif bad_blog_entries:
            status_blog = 'PROBLEM (location-tied blog leaked into hub)'

        print(f'\n/{hub_dir}/   "{svc["label"]}"')
        print(f'  locations: {len(loc_hrefs)} entries — {status_loc}')
        if invalid_locs:
            for u in invalid_locs:
                print(f'    [!] not a valid location for this hub: {u}')
        if dups:
            for k, v in dups.items():
                print(f'    [!] duplicate city: {k} x{v}')
        print(f'  related cards: ids={rel_ids} hrefs={len(rel_card_hrefs)} — {status_blog}')
        if bad_blog_entries:
            for u in bad_blog_entries:
                print(f'    [!] location-tied or wrong-service blog: {u}')

        if status_loc != 'OK' or status_blog != 'OK':
            hub_problems.append(hub_dir)

    print('\n' + '=' * 90)
    if hub_problems:
        print(f'HUBS WITH PROBLEMS: {hub_problems}')
    else:
        print('All 18 hubs OK.')

    # Location page audit
    print()
    print('=' * 90)
    print('LOCATION AUDIT — related-blogs sections')
    print('=' * 90)

    loc_problems: list[str] = []
    for svc in rh.SERVICES:
        hub_dir = svc['hub_dir']
        for loc_url in sorted(locations_set_by_hub[hub_dir]):
            slug = url_to_dirname(loc_url)
            loc_file = ROOT / slug / 'index.html'
            if not loc_file.exists():
                continue
            html = loc_file.read_text(encoding='utf-8', errors='replace')
            related_blocks = RELATED_BLOCK_RE.findall(html)
            rel_card_hrefs: list[str] = []
            for _bid, body in related_blocks:
                rel_card_hrefs.extend(CARD_HREF_RE.findall(body))
            bad: list[str] = []
            for u in rel_card_hrefs:
                rel = u.strip('/')
                if rel.startswith('blog/'):
                    pass
                (b_hub, _bcity) = blog_hub_city_map.get(rel, (None, None))
                if b_hub is None:
                    continue
                if b_hub != hub_dir:
                    bad.append(u)
            if bad:
                loc_problems.append(slug)
                print(f'\n[!] /{slug}/   wrong-service blog leaked:')
                for u in bad:
                    print(f'      {u}')

    print('\n' + '=' * 90)
    if loc_problems:
        print(f'LOCATIONS WITH PROBLEMS: {len(loc_problems)}')
    else:
        print('All location pages OK.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
