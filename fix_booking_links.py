"""Fix broken booking CTA buttons across all pages.

Replaces /#contact body CTA links with proper booking form URLs,
and fixes /book-now/ nav links on service-specific pages.
"""
import re, os

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Service-specific CTA fixes: /#contact → /book-*.html ──────────────
cta_fixes = {
    # Service pages
    "canopy/index.html":                                    "/book-canopy.html",
    "excavation-services/index.html":                       "/book-handy.html",
    "fence-installer-aurora/index.html":                    "/book-fence.html",
    "landscaping-services-toronto/index.html":              "/book-interlock.html",
    "privacy-screen-installation-in-north-york/index.html": "/book-railing.html",
    "services/handyman-plumbing.html":                      "/book-plumbing.html",
    # Blog pages
    "blog/basement-renovation-ideas/index.html":            "/book-basement.html",
    "blog/bathroom-renovation-guide/index.html":            "/book-bathroom.html",
    "blog/contractor-selection-guide/index.html":           "/book-handy.html",
    "blog/fence-installation-options/index.html":           "/book-fence.html",
    "blog/plumbing-emergency-guide/index.html":             "/book-plumbing.html",
    # Blog hub
    "amaximum-deck-builder-blog/index.html":                "/book-deck.html",
    # Locations
    "locations/index.html":                                 "/book-now/",
    "locations/toronto/index.html":                         "/book-now/",
    "locations/toronto.html":                               "/book-now/",
    # Portfolio
    "portfolio/index.html":                                 "/book-now/",
    # Generic info pages → generic booking form
    "company-policy-of-amaximum-construction/index.html":   "/book-now/",
    "client-testimonials/index.html":                       "/book-now/",
    "our-work-process/index.html":                          "/book-now/",
    "what-we-do/index.html":                                "/book-now/",
    "why-choose-us/index.html":                             "/book-now/",
    "index-seo-2026.html":                                  "/book-now/",
}

# ── Nav-quote fixes: /book-now/ → specific form on location .html pages ──
nav_fixes = {
    "locations/markham.html":       "/book-handy.html",
    "locations/newmarket.html":     "/book-handy.html",
    "locations/richmond-hill.html": "/book-handy.html",
    "locations/toronto.html":       "/book-handy.html",
    "locations/vaughan.html":       "/book-handy.html",
    "services/handyman-plumbing.html": "/book-plumbing.html",
    "thank-you-page/index.html":    "/book-now/",  # keep generic on thank-you
}

# Also fix body /book-now/ → /book-handy.html on location pages
body_booknow_fixes = {
    "locations/markham.html":       "/book-handy.html",
    "locations/newmarket.html":     "/book-handy.html",
    "locations/richmond-hill.html": "/book-handy.html",
    "locations/toronto.html":       "/book-handy.html",
    "locations/vaughan.html":       "/book-handy.html",
}

changed = 0

# ── Fix body CTA buttons: /#contact → proper booking URL ──────────────
for relpath, target in cta_fixes.items():
    fpath = os.path.join(ROOT, relpath.replace("/", os.sep))
    if not os.path.isfile(fpath):
        print(f"  SKIP (not found): {relpath}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    # Replace /#contact in CTA buttons (class="btn") only
    pattern = r'(<a\s[^>]*class="[^"]*btn[^"]*"[^>]*)\s*href="/#contact"'
    new_html = re.sub(pattern, rf'\1 href="{target}"', html)
    # Also handle reversed order: href before class
    pattern2 = r'(<a\s[^>]*)href="/#contact"([^>]*class="[^"]*btn[^"]*")'
    new_html = re.sub(pattern2, rf'\1href="{target}"\2', new_html)
    if new_html != html:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_html)
        count = html.count('/#contact') - new_html.count('/#contact')
        print(f"  FIXED ({count} btn): {relpath} → {target}")
        changed += 1
    else:
        print(f"  OK (no btn change): {relpath}")

# ── Fix nav-quote buttons: /book-now/ → specific form ─────────────────
for relpath, target in nav_fixes.items():
    if target == "/book-now/":
        continue  # skip if already correct
    fpath = os.path.join(ROOT, relpath.replace("/", os.sep))
    if not os.path.isfile(fpath):
        print(f"  SKIP (not found): {relpath}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    # Replace nav-quote href="/book-now/"
    pattern = r'(<a\s[^>]*class="[^"]*nav-quote[^"]*"[^>]*)\s*href="/book-now/"'
    new_html = re.sub(pattern, rf'\1 href="{target}"', html)
    if new_html != html:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  FIXED nav-quote: {relpath} → {target}")
        changed += 1
    else:
        print(f"  OK (nav-quote): {relpath}")

# ── Fix body /book-now/ CTAs on location pages ────────────────────────
for relpath, target in body_booknow_fixes.items():
    fpath = os.path.join(ROOT, relpath.replace("/", os.sep))
    if not os.path.isfile(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()
    # Replace body btn href="/book-now/" (not nav-quote)
    new_html = html.replace('href="/book-now/" class="btn"', f'href="{target}" class="btn"')
    if new_html != html:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"  FIXED body CTA: {relpath} → {target}")
        changed += 1
    else:
        print(f"  OK (body CTA): {relpath}")

print(f"\nDone! {changed} files updated.")
