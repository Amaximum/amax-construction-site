"""
update_all_pages.py
Standardizes nav (topbar) and footer across all HTML pages.
Also removes duplicate inline <style> blocks and links to external CSS.
"""
import os, re

ROOT = r'c:\Users\maxim\Desktop\amax-Construction-site'
SKIP_FILES = {'index-seo-2026.html', 'service-template.html', 'update_all_pages.py'}

BOOKING_PAGE_REL = '/book-now/index.html'

CSS_LINK = '<link rel="stylesheet" href="/css/styles.css">'
# Use `defer` (not `async`) so the loader executes after HTML is parsed,
# ensuring the widget divs are present when Elfsight scans the DOM.
ELFSIGHT_SCRIPT = '<script src="https://static.elfsight.com/platform/platform.js" defer></script>'

# Cache-bust so browsers reliably fetch latest JS changes.
SITE_JS_VERSION = '20260314-1'
SITE_JS = f'<script src="/js/site.js?v={SITE_JS_VERSION}" defer></script>'

# Elfsight widgets
ELFSIGHT_REVIEWS_APP_CLASS = 'elfsight-app-b029cad3-6f49-425c-9793-f556870797bb'
ELFSIGHT_RATING_APP_CLASS = 'elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875'

ELFSIGHT_RATING_FLOAT_WRAPPER = f"""<div id=\"rating-widget\" style=\"position:fixed;right:14px;bottom:14px;z-index:9999;max-width:220px;pointer-events:auto;\">\
  <div class=\"{ELFSIGHT_RATING_APP_CLASS}\"></div>
</div>"""

ELFSIGHT_REVIEWS_EMBED_BLOCK = f"""<section id=\"reviews-embed\" class=\"shell\">\n  <div class=\"{ELFSIGHT_REVIEWS_APP_CLASS}\"></div>\n</section>"""
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
      <a class="btn btn-primary btn-sm nav-quote" href="/book-now/">BOOK NOW</a>
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
          <li><a href="/deck-railings-toronto/">Deck Railings</a></li>
          <li><a href="/fence-contractor-in-toronto/">Fence Installation</a></li>
          <li><a href="/bathroom-renovation/">Bathroom Renovation</a></li>
          <li><a href="/basement-renovation-service-in-toronto/">Basement Renovation</a></li>
          <li><a href="/handyman-plumbing-services/">Plumbing</a></li>
          <li><a href="/electrical-handyman-services/">Electrical</a></li>
          <li><a href="/handyman-painting-services/">Painting</a></li>
          <li><a href="/canopy/">Canopy &amp; Awnings</a></li>
          <li><a href="/landscaping-services-toronto/">Landscaping</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
          <li><a href="/general-contractor-in-toronto/">General Contractor</a></li>
          <li><a href="/interlocking-paver-services/">Interlocking</a></li>
          <li><a href="/carpenter-services/">Carpentry</a></li>
          <li><a href="/demolition-services/">Demolition</a></li>
          <li><a href="/excavation-services/">Excavation</a></li>
          <li><a href="/christmas-lights-installation-toronto-gta/">Christmas Lights</a></li>
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
  r'[ \t]*<script\s+src="https://(?:static\.elfsight\.com/platform/platform\.js|elfsightcdn\.com/platform\.js)"[^>]*></script>\s*\n?',
  re.IGNORECASE,
)
RE_ELFSIGHT_WIDGET_BLOCK = re.compile(
  r'[ \t]*<!--\s*Elfsight Google Reviews \| Untitled Google Reviews\s*-->\s*\n?'
  r'(?:[ \t]*<script\s+src="https://elfsightcdn\.com/platform\.js"\s+async></script>\s*\n?)?'
  r'[ \t]*<div\s+class="elfsight-app-b029cad3-6f49-425c-9793-f556870797bb"[^>]*></div>\s*\n?',
  re.IGNORECASE,
)
RE_ELFSIGHT_FLOAT_WRAPPER = re.compile(
  r'[ \t]*<div\s+id="reviews-widget"[^>]*>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_ELFSIGHT_RATING_FLOAT_WRAPPER = re.compile(
  r'[ \t]*<div\s+id="rating-widget"[^>]*>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_ELFSIGHT_REVIEWS_EMBED_BLOCK = re.compile(
  r'[ \t]*<section\s+id="reviews-embed"[^>]*>[\s\S]*?</section>\s*\n?',
  re.DOTALL | re.IGNORECASE,
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

RE_BOOKING_MODAL_COMMENT = re.compile(r'[ \t]*<!--\s*Booking Form Modal\s*-->\s*\n?', re.IGNORECASE)
RE_BOOKING_MODAL = re.compile(
  r'[ \t]*<div[^>]*\bid="bookingModal"[^>]*>[\s\S]*?<form[^>]*\bid="bookingForm"[\s\S]*?</form>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_BOOKING_MODAL_GENERIC_COMMENT = re.compile(r'[ \t]*<!--\s*Booking Modal\s*-->\s*\n?', re.IGNORECASE)
RE_BOOKING_MODAL_FRAGMENT_BY_COMMENT = re.compile(
  r'[ \t]*<!--\s*Booking Modal\s*-->[\s\S]*?</form>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_BOOKING_MODAL_FRAGMENT_AFTER_MAIN = re.compile(
  r'(</main>\s*)[\s\S]*?<div\s+class="form-group">[\s\S]*?\bid="clientAddress"[\s\S]*?</form>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_BOOKING_FORM_ORPHAN_FRAGMENT = re.compile(
  r'\n[ \t]*<div\s+class="form-group">[\s\S]*?\bid="clientAddress"[\s\S]*?</form>[\s\S]*?</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_BOOKING_MODAL_SCRIPT_TAIL = re.compile(
  r'\n[ \t]*//\s*Booking Modal Functionality[\s\S]*?\n[ \t]*</script>',
  re.DOTALL | re.IGNORECASE,
)
RE_BOOKING_MODAL_SCRIPT_BLOCK_TO_MOBILE_MENU = re.compile(
  r"\n[ \t]*const\s+modal\s*=\s*document\.getElementById\(['\"]bookingModal['\"]\);[\s\S]*?(?=\n[ \t]*//\s*Mobile menu)",
  re.DOTALL | re.IGNORECASE,
)

# Cleanup for partial booking-modal deletions that left a “tail” of fields
# (Email/Address/Date/Time/etc) plus stray </form></div></div>.
RE_BOOKING_MODAL_ORPHAN_TAIL = re.compile(
  r'\n[ \t]*<div\s+class="form-group">\s*<label>\s*Email\s*\*\s*</label>[\s\S]*?\bid="bookDate"[\s\S]*?</form>\s*</div>\s*</div>\s*\n?',
  re.DOTALL | re.IGNORECASE,
)
RE_GOOGLE_PLACES_SCRIPT = re.compile(
  r'[ \t]*<script[^>]+maps\.googleapis\.com/maps/api/js[^>]*></script>\s*\n?',
  re.IGNORECASE,
)
RE_AUTOCOMPLETE_INLINE = re.compile(
  r'[ \t]*<script>\s*function\s+initAddressAutocomplete\(\)\s*\{[\s\S]*?</script>\s*\n?',
  re.IGNORECASE,
)

RE_SITE_JS = re.compile(r'[ \t]*<script\s+src="/js/site\.js(?:\?[^\"]*)?"[^>]*></script>\s*\n?', re.IGNORECASE)

RE_SCRIPT_BLOCK = re.compile(r'(<script\b[^>]*>)([\s\S]*?)(</script>)', re.IGNORECASE)


def _strip_mobile_menu_js_from_script(script_text: str) -> str:
  """Remove legacy inline mobile-menu JS snippet from a <script> block.

  Some pages have an inline snippet that binds #menuBtn to toggle .open on #siteNav.
  If we also include /js/site.js, duplicate listeners can cause double-toggles.
  We strip only the menu snippet, leaving the rest of the script intact.
  """
  lower = script_text.lower()
  if "getelementbyid('menubtn')" not in lower and 'getelementbyid("menubtn")' not in lower:
    return script_text
  if "getelementbyid('sitenav')" not in lower and 'getelementbyid("sitenav")' not in lower:
    return script_text

  # Find the first occurrence of the menuBtn binding.
  anchors = [lower.find("getelementbyid('menubtn')"), lower.find('getelementbyid("menubtn")')]
  anchors = [a for a in anchors if a != -1]
  if not anchors:
    return script_text
  anchor = min(anchors)

  # Start at the beginning of the line containing the anchor.
  start = script_text.rfind('\n', 0, anchor)
  start = 0 if start == -1 else start + 1

  # Attempt to remove the surrounding if(...) { ... } block.
  # We look for an "if" before the anchor, then match braces.
  if_pos = lower.rfind('if', 0, anchor)
  if if_pos != -1:
    brace_open = script_text.find('{', if_pos)
    if brace_open != -1:
      depth = 0
      i = brace_open
      while i < len(script_text):
        ch = script_text[i]
        if ch == '{':
          depth += 1
        elif ch == '}':
          depth -= 1
          if depth == 0:
            end = i + 1
            # consume trailing semicolon/whitespace/newlines
            while end < len(script_text) and script_text[end] in ' \t;\r\n':
              end += 1
            return script_text[:start] + script_text[end:]
        i += 1

  # Fallback: remove a small window from start through the next blank line.
  end = script_text.find('\n\n', start)
  if end == -1:
    end = len(script_text)
  return script_text[:start] + script_text[end:]


def _button_to_booking_link(match: re.Match) -> str:
  attrs = match.group('attrs')
  attrs = re.sub(r'\s*\btype\s*=\s*"[^"]*"', '', attrs, flags=re.IGNORECASE)
  # Remove id attributes that were used for modal wiring.
  attrs = re.sub(r'\s*\bid\s*=\s*"(?:bookingBtn|cancelBtn|modalClose|modalOverlay)"', '', attrs, flags=re.IGNORECASE)
  if re.search(r'\bhref\s*=', attrs, re.IGNORECASE):
    return f'<a{attrs}>BOOK NOW</a>'
  return f'<a{attrs} href="/book-now/">BOOK NOW</a>'


def _remove_div_by_id(html: str, element_id: str) -> str:
  """Remove <div id="element_id">...</div> including nested divs.

  Regex is fragile for nested HTML; this uses a depth counter on <div> tags.
  """
  start_re = re.compile(
    r'<div\b[^>]*\bid\s*=\s*["\']' + re.escape(element_id) + r'["\'][^>]*>',
    re.IGNORECASE,
  )

  while True:
    m = start_re.search(html)
    if not m:
      return html

    start = m.start()
    i = m.end()
    lower = html.lower()
    depth = 1

    while depth > 0:
      next_open = lower.find('<div', i)
      next_close = lower.find('</div', i)

      if next_close == -1:
        # Malformed HTML; remove only the start tag.
        html = html[:start] + html[m.end():]
        break

      if next_open != -1 and next_open < next_close:
        depth += 1
        i = next_open + 4
        continue

      depth -= 1
      close_end = lower.find('>', next_close)
      if close_end == -1:
        html = html[:start] + html[next_close:]
        break
      i = close_end + 1

    else:
      html = html[:start] + html[i:]

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
    is_booking_page = (rel == BOOKING_PAGE_REL)

    # 1. Remove inline <style> blocks that contain base CSS
    def strip_style(m):
        block = m.group(0)
        if has_base_css(block):
            return '\n'
        return block
    html = RE_STYLE_BLOCK.sub(strip_style, html)

    # 2. Booking CTA normalization (site-wide)
    html = re.sub(
      r'<button(?P<attrs>[^>]*\bclass\s*=\s*"[^"]*\bbtn-booking\b[^"]*"[^>]*)>\s*[\s\S]*?</button>',
      _button_to_booking_link,
      html,
      flags=re.IGNORECASE,
    )
    html = re.sub(
      r'<button(?P<attrs>[^>]*\bid\s*=\s*"bookingBtn"[^>]*)>\s*[\s\S]*?</button>',
      _button_to_booking_link,
      html,
      flags=re.IGNORECASE,
    )
    html = re.sub(
      r'href="/#contact"([^>]*>)\s*Get Free Quote\s*<',
      r'href="/book-now/"\1BOOK NOW<',
      html,
      flags=re.IGNORECASE,
    )

    # 3. Remove existing (possibly wrong-path) CSS link
    html = RE_CSS_LINK.sub('', html)

    # 4. Insert correct CSS link (always)
    if CSS_LINK not in html:
      html = html.replace('</title>', '</title>\n  ' + CSS_LINK, 1)

    # 4a. Insert global site JS (always)
    html = RE_SITE_JS.sub('', html)
    if SITE_JS not in html:
      html = html.replace('</title>', '</title>\n  ' + SITE_JS, 1)

    # Always strip Elfsight scripts; we'll re-add only on pages without forms
    html = RE_ELFSIGHT_ANY_SCRIPT.sub('', html)

    # Strip legacy inline mobile-menu snippets to avoid double-toggle once /js/site.js is present.
    def strip_menu_in_script(m: re.Match) -> str:
      open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
      return open_tag + _strip_mobile_menu_js_from_script(body) + close_tag
    html = RE_SCRIPT_BLOCK.sub(strip_menu_in_script, html)

    # Strip booking modal UI from non-booking pages (form lives on /book-now/)
    if not is_booking_page:
      # Prefer robust removal first.
      html = _remove_div_by_id(html, 'bookingModal')

      html = RE_BOOKING_MODAL_COMMENT.sub('', html)
      html = RE_BOOKING_MODAL_GENERIC_COMMENT.sub('', html)
      html = RE_BOOKING_MODAL.sub('', html)
      html = RE_BOOKING_MODAL_FRAGMENT_BY_COMMENT.sub('', html)
      html = RE_BOOKING_MODAL_FRAGMENT_AFTER_MAIN.sub(r'\1', html)
      html = RE_BOOKING_FORM_ORPHAN_FRAGMENT.sub('\n', html)
      html = RE_BOOKING_MODAL_ORPHAN_TAIL.sub('\n', html)

      # Remove booking-modal JS that becomes unsafe once modal markup is gone.
      html = RE_BOOKING_MODAL_SCRIPT_TAIL.sub('\n  </script>', html)
      html = RE_BOOKING_MODAL_SCRIPT_BLOCK_TO_MOBILE_MENU.sub('\n', html)

    # 4. Fix /amax-construction-site/ paths
    html = html.replace('/amax-construction-site/', '/')

    # 4b. Fix malformed <body> tag (missing closing '>')
    html = re.sub(r'(<body\b[^>\n]*)(\s*)\n', r'\1>\n', html)

    # 5. Replace nav HTML
    if RE_TOPBAR.search(html):
        html = RE_TOPBAR.sub(STANDARD_NAV, html, count=1)
    elif RE_HEADER_BANNER.search(html):
        html = RE_HEADER_BANNER.sub(STANDARD_NAV, html, count=1)

    # 6. Replace footer (always update to get correct service links)
    if RE_FOOTER.search(html):
        html = RE_FOOTER.sub(STANDARD_FOOTER, html, count=1)

    # 6b. Elfsight widgets
    # Remove any legacy/new blocks first
    html = RE_ELFSIGHT_WIDGET_BLOCK.sub('', html)
    html = RE_ELFSIGHT_FLOAT_WRAPPER.sub('', html)
    html = RE_ELFSIGHT_RATING_FLOAT_WRAPPER.sub('', html)
    html = RE_ELFSIGHT_REVIEWS_EMBED_BLOCK.sub('', html)
    html = RE_ELFSIGHT_LEGACY_BADGE.sub('', html)
    html = RE_ELFSIGHT_LEGACY_APP.sub('', html)

    # Always show rating widget on every page
    if ELFSIGHT_SCRIPT not in html:
        html = html.replace('</title>', '</title>\n  ' + ELFSIGHT_SCRIPT, 1)
    if '</body>' in html:
        html = html.replace('</body>', '\n' + ELFSIGHT_RATING_FLOAT_WRAPPER + '\n</body>', 1)

    # Show reviews embed on every page EXCEPT the booking page, placed before FAQ when possible.
    if not is_booking_page:
        faq_match = re.search(r'\n([ \t]*<section[^>]*\bid="faq"[^>]*>)', html, re.IGNORECASE)
        if faq_match:
            html = html[:faq_match.start(1)] + ELFSIGHT_REVIEWS_EMBED_BLOCK + '\n' + html[faq_match.start(1):]
        else:
            footer_match = re.search(r'\n([ \t]*<footer\b)', html, re.IGNORECASE)
            if footer_match:
                html = html[:footer_match.start(1)] + ELFSIGHT_REVIEWS_EMBED_BLOCK + '\n' + html[footer_match.start(1):]

    # 6c. Google Places autocomplete only on /book-now/
    html = RE_GOOGLE_PLACES_SCRIPT.sub('', html)
    html = RE_AUTOCOMPLETE_INLINE.sub('', html)
    if is_booking_page:
        html = html.replace('</body>', AUTOCOMPLETE_INLINE + '\n  ' + PLACES_SCRIPT + '\n</body>', 1)

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
