"""
update_all_pages.py
Standardizes nav (topbar) and footer across all HTML pages.
Also removes duplicate inline <style> blocks and links to external CSS.
"""
import os, re

ROOT = r'c:\Users\maxim\Desktop\amax-Construction-site'
SKIP_FILES = {'index-seo-2026.html', 'service-template.html', 'update_all_pages.py'}

CSS_LINK = '<link rel="stylesheet" href="/css/styles.css">'
ELFSIGHT_WIDGET_BLOCK = """<!-- Elfsight Google Reviews | Untitled Google Reviews -->
<script src=\"https://elfsightcdn.com/platform.js\" async></script>
<div class=\"elfsight-app-b029cad3-6f49-425c-9793-f556870797bb\" data-elfsight-app-lazy></div>"""
GOOGLE_PLACES_KEY = 'AIzaSyBkEKDxWzpZfBitiQc3qURLsYm1r_u8ISc'
PLACES_SCRIPT = f'<script id="google-places-script" src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_PLACES_KEY}&libraries=places&callback=initAddressAutocomplete" async defer></script>'
AUTOCOMPLETE_INLINE = """<script>
function initAddressAutocomplete() {
  const input = document.querySelector('#clientAddress, input[name="address"]');
  if (!input || typeof google === 'undefined' || !google.maps?.places) return;
  const toronto = { lat: 43.6532, lng: -79.3832 };
  const bounds = new google.maps.Circle({ center: toronto, radius: 65000 }).getBounds();
  const autocomplete = new google.maps.places.Autocomplete(input, {
    bounds,
    componentRestrictions: { country: 'ca' },
    fields: ['formatted_address', 'geometry', 'name'],
    types: ['address'],
  });
  autocomplete.setBounds(bounds);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') e.preventDefault();
  });
}
</script>"""

# Legacy floating badge (remove if present)

STANDARD_NAV = """\
<div class="topbar-wrap shell">
  <header class="topbar" role="banner">
    <a class="logo" href="/" aria-label="aMaximum Construction home">
      <img src="/img/logo.png" alt="aMaximum Construction">
    </a>
    <div class="topbar-right">
      <nav class="nav" id="siteNav" aria-label="Main navigation">
        <a href="/">Home</a>
        <a href="/#services">Services</a>
        <a href="/locations/">Locations</a>
        <a href="/blog/">Blog</a>
        <a href="/portfolio/">Portfolio</a>
        <a href="/#contact">Contact</a>
      </nav>
      <a class="btn btn-primary btn-sm nav-quote" href="/#contact">Get Free Quote</a>
      <button class="menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false">&#9776;</button>
    </div>
  </header>
</div>"""

STANDARD_FOOTER = """\
<footer class="site-footer">
  <div class="shell">
    <div class="footer-cols">
      <div class="footer-col footer-brand">
        <a href="/" class="footer-logo-link"><img src="/img/logo.png" alt="aMaximum Construction" class="footer-logo"></a>
        <p>Licensed and insured construction &amp; renovation services in Toronto &amp; GTA.</p>
        <a href="mailto:amaximumconstructioncorp@gmail.com" class="footer-email">amaximumconstructioncorp@gmail.com</a>
      </div>
      <div class="footer-col">
        <h4>Services</h4>
        <ul>
          <li><a href="/deck-builder/">Deck Building</a></li>
          <li><a href="/fence-contractor-in-toronto/">Fence Installation</a></li>
          <li><a href="/bathroom-renovation/">Bathroom Renovation</a></li>
          <li><a href="/basement-renovation-service-in-toronto/">Basement Renovation</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
          <li><a href="/general-contractor-in-toronto/">General Contractor</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Service Areas</h4>
        <ul>
          <li><a href="/deck-builder-toronto/">Toronto</a></li>
          <li><a href="/deck-contractor-markham/">Markham</a></li>
          <li><a href="/deck-builder-in-richmond-hill/">Richmond Hill</a></li>
          <li><a href="/deck-builder-newmarket/">Newmarket</a></li>
          <li><a href="/deck-builder-gta/">GTA</a></li>
          <li><a href="/locations/">All Locations &rarr;</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/portfolio/">Portfolio</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/#faq">FAQ</a></li>
          <li><a href="/#contact">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bar">
      <span>&copy; 2026 aMaximum Construction. Licensed &amp; Insured.</span>
      <span>Toronto &amp; GTA</span>
    </div>
  </div>
</footer>"""

# Regexes
RE_STYLE_BLOCK = re.compile(r'[ \t]*<style[^>]*>[\s\S]*?</style>\s*\n?', re.DOTALL)
RE_CSS_LINK    = re.compile(r'[ \t]*<link\s+rel="stylesheet"\s+href="[^"]*styles\.css"[^>]*>\s*\n?')
RE_ELFSIGHT_ANY_SCRIPT = re.compile(
  r'[ \t]*<script\s+src="https://(?:static\.elfsight\.com/platform/platform\.js|elfsightcdn\.com/platform\.js)"\s+async></script>\s*\n?',
  re.IGNORECASE,
)
RE_ELFSIGHT_WIDGET_BLOCK = re.compile(
  r'[ \t]*<!--\s*Elfsight Google Reviews \| Untitled Google Reviews\s*-->\s*\n?'
  r'[ \t]*<script\s+src="https://elfsightcdn\.com/platform\.js"\s+async></script>\s*\n?'
  r'[ \t]*<div\s+class="elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"[^>]*></div>\s*\n?',
  re.IGNORECASE,
)
RE_ELFSIGHT_LEGACY_BADGE = re.compile(
  r'[ \t]*<div\s+class="elfsight-review-badge"[^>]*>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_ELFSIGHT_LEGACY_APP = re.compile(
  r'[ \t]*<div\s+class="elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875"[^>]*></div>\s*\n?',
  re.IGNORECASE,
)
RE_TOPBAR      = re.compile(r'<div class="topbar-wrap shell">[\s\S]*?</header>\s*\n?[ \t]*</div>', re.DOTALL)
RE_HEADER_BANNER = re.compile(r'[ \t]*<header[^>]*role="banner"[^>]*>[\s\S]*?</header>', re.DOTALL)
RE_FOOTER      = re.compile(r'<footer[\s\S]*?</footer>', re.DOTALL)
RE_MULTI_BLANK = re.compile(r'\n{3,}')

def has_base_css(style_block):
    """Return True if this <style> block contains base/duplicated CSS."""
    return ('--bg:' in style_block or '--bg :' in style_block or
            ':root' in style_block or '--primary:' in style_block)

def process(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    rel = filepath.replace(ROOT, '').replace('\\', '/')
    is_main_index = (rel == '/index.html')
    in_blog = '/blog/' in rel

    # 1. Remove inline <style> blocks that contain base CSS
    def strip_style(m):
        block = m.group(0)
        if has_base_css(block):
            return '\n'
        return block
    html = RE_STYLE_BLOCK.sub(strip_style, html)

    # 2. Detect if the page contains a form
    has_form = re.search(r'<form[^>]*>', html, re.IGNORECASE) is not None

    # 3. Remove existing (possibly wrong-path) CSS link
    html = RE_CSS_LINK.sub('', html)

    # 4. Insert correct CSS link (always)
    if CSS_LINK not in html:
      html = html.replace('</title>', '</title>\n  ' + CSS_LINK, 1)

    # Always strip Elfsight scripts; we'll re-add only on pages without forms
    html = RE_ELFSIGHT_ANY_SCRIPT.sub('', html)

    # 4. Fix /amax-construction-site/ paths
    html = html.replace('/amax-construction-site/', '/')

    # 5. Replace nav HTML
    if RE_TOPBAR.search(html):
        html = RE_TOPBAR.sub(STANDARD_NAV, html, count=1)
    elif RE_HEADER_BANNER.search(html):
        html = RE_HEADER_BANNER.sub(STANDARD_NAV, html, count=1)

    # 6. Replace footer (always update to get correct service links)
    if RE_FOOTER.search(html):
        html = RE_FOOTER.sub(STANDARD_FOOTER, html, count=1)

    # 6b. Elfsight Google Reviews widget: everywhere EXCEPT pages with forms
    # Remove any legacy/new blocks first
    html = RE_ELFSIGHT_WIDGET_BLOCK.sub('', html)
    html = RE_ELFSIGHT_LEGACY_BADGE.sub('', html)
    html = RE_ELFSIGHT_LEGACY_APP.sub('', html)

    should_show_widget = not has_form
    if should_show_widget:
      if '<footer class="site-footer">' in html:
        html = html.replace('<footer class="site-footer">', ELFSIGHT_WIDGET_BLOCK + '\n\n<footer class="site-footer">', 1)
      elif '</body>' in html:
        html = html.replace('</body>', ELFSIGHT_WIDGET_BLOCK + '\n</body>', 1)

    # 6c. Google Places autocomplete only on pages with forms
    if has_form:
      html = re.sub(r'<script[^>]+maps\.googleapis\.com/maps/api/js[^>]*></script>', '', html)
      needs_inline = 'initAddressAutocomplete' not in html
      needs_script = 'google-places-script' not in html
      if needs_inline and needs_script:
        html = html.replace('</body>', AUTOCOMPLETE_INLINE + '\n  ' + PLACES_SCRIPT + '\n</body>', 1)
      elif needs_inline:
        html = html.replace('</body>', AUTOCOMPLETE_INLINE + '\n</body>', 1)
      elif needs_script:
        html = html.replace('</body>', PLACES_SCRIPT + '\n</body>', 1)

    # 7. Rename hero class (not on main index.html)
    if not is_main_index:
        new_hero = 'blog-hero' if in_blog else 'page-hero'
        html = html.replace('class="hero"', f'class="{new_hero}"')
        html = html.replace("class='hero'", f"class='{new_hero}'")

    # 8. Clean up extra blank lines
    html = RE_MULTI_BLANK.sub('\n\n', html)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False

updated = []
for dirpath, dirnames, filenames in os.walk(ROOT):
  dirnames[:] = [d for d in dirnames if d not in {'.git', 'img'}]
  for fn in filenames:
    if fn.endswith('.html') and fn not in SKIP_FILES:
      fp = os.path.join(dirpath, fn)
      if process(fp):
        updated.append(fp.replace(ROOT, '').replace('\\', '/'))

print(f'Updated {len(updated)} files:')
for u in sorted(updated):
    print(' ', u)
