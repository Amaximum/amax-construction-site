"""
update_all_pages.py
Standardizes nav (topbar) and footer across all HTML pages.
Also removes duplicate inline <style> blocks and links to external CSS.
"""
import os, re

ROOT = r'c:\Users\maxim\Desktop\amax-Construction-site'
SKIP_FILES = {'index-seo-2026.html', 'service-template.html', 'update_all_pages.py'}

CSS_LINK = '<link rel="stylesheet" href="/css/styles.css">'

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
RE_ELFSIGHT_SCRIPT = re.compile(r'[ \t]*<script\s+src="https://static\.elfsight\.com/platform/platform\.js"\s+async></script>\s*\n?')
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

    # 2. Remove existing (possibly wrong-path) CSS link
    html = RE_CSS_LINK.sub('', html)

    # 3. Insert correct CSS link after </title>
    if CSS_LINK not in html:
        html = html.replace('</title>', '</title>\n  ' + CSS_LINK, 1)
    html = RE_ELFSIGHT_SCRIPT.sub('', html)

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

    # 6b. Remove Elfsight reviews section + floating badge everywhere
    html = re.sub(r'<section class="shell"[^>]*>\s*<div class="elfsight-app-b029cad3[^<]*</div>\s*</section>', '', html)
    html = re.sub(r'<div class="elfsight-app-3935cedc[^"]*"[^>]*></div>', '', html)

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
    dirnames[:] = [d for d in dirnames if d not in {'.git', 'services', 'img'}]
    for fn in filenames:
        if fn.endswith('.html') and fn not in SKIP_FILES:
            fp = os.path.join(dirpath, fn)
            if process(fp):
                updated.append(fp.replace(ROOT, '').replace('\\', '/'))

print(f'Updated {len(updated)} files:')
for u in sorted(updated):
    print(' ', u)
