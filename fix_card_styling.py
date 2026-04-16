"""
Convert all inline-styled sections to the card-based design system.

Handles 5 patterns:
1. "Our Other Services" inline <ul> → .island .location-grid .location-card
2. "[Service] Near You" inline <ul> → .island .location-grid .location-card  
3. "Related Blog Posts" inline <ul> → .island .related-articles .cards .card
4. "Related Articles" inline <ul> → .island .related-articles .cards .card
5. "Related Service" inline <ul> → .island .related-articles .cards .card
Also removes duplicate inline sections when a proper .island version exists.
"""

import re
import os
import glob
from html import unescape

ROOT = os.path.dirname(os.path.abspath(__file__))

# Service icons for "Our Other Services" cards
SERVICE_ICONS = {
    "Deck Building": "🏗️",
    "Fence Installation": "🚧",
    "Bathroom Renovation": "🛁",
    "Basement Renovation": "🏠",
    "Handyman": "🛠️",
    "Plumbing": "🚰",
    "Electrical": "⚡",
    "Painting": "🎨",
    "General Contractor": "🔨",
    "Carpentry": "🪵",
    "Canopy & Awnings": "⛱️",
    "Landscaping": "🌳",
    "Interlocking & Paving": "🪨",
    "Demolition": "🏗️",
    "Excavation": "⛏️",
    "Home Renovation": "🏠",
    "Christmas Lights": "🎄",
    "Deck Railings": "🛡️",
}

stats = {"other_services": 0, "near_you": 0, "related_blogs": 0, 
         "related_articles": 0, "related_service": 0, "duplicates": 0, "errors": 0}


def convert_other_services(html):
    """Convert 'Our Other Services' inline <ul> to island with location-card grid."""
    pattern = re.compile(
        r'<section[^>]*class="shell"[^>]*style="[^"]*padding:\s*32px[^"]*"[^>]*>\s*'
        r'<h2[^>]*>Our Other Services</h2>\s*'
        r'<ul[^>]*>(.*?)</ul>\s*'
        r'</section>',
        re.DOTALL
    )
    
    def replacer(m):
        ul_content = m.group(1)
        links = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', ul_content)
        if not links:
            return m.group(0)
        
        cards_html = []
        for href, text in links:
            icon = SERVICE_ICONS.get(text, "🔧")
            cards_html.append(
                f'    <a href="{href}" class="service-card">'
                f'<span class="service-icon">{icon}</span>'
                f'<h3>{text}</h3></a>'
            )
        
        return (
            '<section class="island reveal service-locations" aria-label="Our other services">\n'
            '  <span class="shine" aria-hidden="true"></span>\n'
            '  <div class="section-head">\n'
            '    <h2>Our Other Services</h2>\n'
            '    <p>Explore the full range of construction and renovation services we offer across Toronto &amp; GTA.</p>\n'
            '  </div>\n'
            '  <div class="location-grid">\n'
            + '\n'.join(cards_html) + '\n'
            '  </div>\n'
            '</section>'
        )
    
    new_html = pattern.sub(replacer, html)
    changed = new_html != html
    return new_html, changed


def convert_near_you(html):
    """Convert '[Service] Near You' inline <ul> to island with location-card grid."""
    pattern = re.compile(
        r'<section[^>]*(?:id="service-areas")?[^>]*class="shell"[^>]*style="[^"]*padding:\s*32px[^"]*"[^>]*>\s*'
        r'<h2[^>]*>([^<]*(?:Near You|Near you)[^<]*)</h2>\s*'
        r'<ul[^>]*>(.*?)</ul>\s*'
        r'</section>',
        re.DOTALL
    )
    
    def replacer(m):
        heading = m.group(1).strip()
        ul_content = m.group(2)
        links = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', ul_content)
        if not links:
            return m.group(0)
        
        cards_html = []
        for href, text in links:
            cards_html.append(f'    <a href="{href}" class="location-card">{text}</a>')
        
        return (
            f'<section class="island reveal service-locations" id="service-areas" aria-label="{heading}">\n'
            '  <span class="shine" aria-hidden="true"></span>\n'
            '  <div class="section-head">\n'
            f'    <h2>{heading}</h2>\n'
            '    <p>Select your area to learn more about our services near you.</p>\n'
            '  </div>\n'
            '  <div class="location-grid">\n'
            + '\n'.join(cards_html) + '\n'
            '  </div>\n'
            '</section>'
        )
    
    new_html = pattern.sub(replacer, html)
    changed = new_html != html
    return new_html, changed


def convert_related_list(html):
    """Convert 'Related Blog Posts', 'Related Articles', 'Related Service' inline <ul> 
    to .island .related-articles .cards .card — but only if no proper styled version exists nearby."""
    
    pattern = re.compile(
        r'<section[^>]*(?:id="(?:related-blogs|service-links)")?[^>]*class="shell"[^>]*style="[^"]*padding:\s*32px[^"]*"[^>]*>\s*'
        r'<h2[^>]*>(Related Blog Posts|Related Articles|Related Service)</h2>\s*'
        r'<ul[^>]*>(.*?)</ul>\s*'
        r'</section>',
        re.DOTALL
    )
    
    def replacer(m):
        heading = m.group(1).strip()
        ul_content = m.group(2)
        links = re.findall(r'<li><a href="([^"]+)">([^<]+)</a></li>', ul_content)
        if not links:
            return m.group(0)
        
        # Determine the section subtitle
        if heading == "Related Blog Posts":
            subtitle = "Read our latest guides and tips related to this service."
            section_id = "related-blogs"
        elif heading == "Related Service":
            subtitle = "Explore related services we offer across Toronto &amp; GTA."
            section_id = "service-links"
        else:
            subtitle = "Helpful articles and resources for your project."
            section_id = "related-articles"
        
        cards_html = []
        for href, text in links:
            safe_text = text.replace("&", "&amp;")
            cards_html.append(
                f'    <a href="{href}" class="card">\n'
                f'      <h3>{safe_text}</h3>\n'
                f'    </a>'
            )
        
        return (
            f'<section class="island reveal related-articles" id="{section_id}" aria-label="{heading}">\n'
            '  <span class="shine" aria-hidden="true"></span>\n'
            '  <div class="section-head">\n'
            f'    <h2>{heading}</h2>\n'
            f'    <p>{subtitle}</p>\n'
            '  </div>\n'
            '  <div class="cards">\n'
            + '\n'.join(cards_html) + '\n'
            '  </div>\n'
            '</section>'
        )
    
    new_html = pattern.sub(replacer, html)
    changed = new_html != html
    return new_html, changed


def remove_duplicate_inline_blogs(html):
    """If page has BOTH an inline 'Related Blog Posts' <ul> AND a proper 
    .island.related-articles section, remove the inline duplicate."""
    has_island = bool(re.search(r'class="island[^"]*related-articles"', html))
    if not has_island:
        return html, False
    
    # Check for inline version  
    inline_pattern = re.compile(
        r'<section[^>]*id="related-blogs"[^>]*class="shell"[^>]*style="[^"]*"[^>]*>\s*'
        r'<h2[^>]*>Related Blog Posts</h2>\s*'
        r'<ul[^>]*>.*?</ul>\s*'
        r'</section>\s*',
        re.DOTALL
    )
    
    new_html = inline_pattern.sub('', html)
    changed = new_html != html
    return new_html, changed


def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        stats["errors"] += 1
        return
    
    original = html
    
    # Step 1: Remove duplicate inline blogs if proper island exists
    html, dup_changed = remove_duplicate_inline_blogs(html)
    if dup_changed:
        stats["duplicates"] += 1
    
    # Step 2: Convert "Our Other Services"
    html, os_changed = convert_other_services(html)
    if os_changed:
        stats["other_services"] += 1
    
    # Step 3: Convert "[Service] Near You"
    html, ny_changed = convert_near_you(html)
    if ny_changed:
        stats["near_you"] += 1
    
    # Step 4: Convert all remaining inline related lists
    html, rl_changed = convert_related_list(html)
    if rl_changed:
        # Count which types were found
        if "Related Blog Posts" in original and rl_changed:
            stats["related_blogs"] += 1
        if re.search(r'style="[^"]*">Related Articles<', original):
            stats["related_articles"] += 1
        if "Related Service" in original and rl_changed:
            stats["related_service"] += 1
    
    if html != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        relpath = os.path.relpath(filepath, ROOT)
        changes = []
        if dup_changed: changes.append("rm-dup")
        if os_changed: changes.append("services")
        if ny_changed: changes.append("near-you")
        if rl_changed: changes.append("related")
        print(f"  FIXED [{', '.join(changes)}]: {relpath}")


def main():
    html_files = glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
    print(f"Scanning {len(html_files)} HTML files...\n")
    
    for filepath in sorted(html_files):
        process_file(filepath)
    
    print(f"\n{'='*60}")
    print(f"  'Our Other Services' converted:  {stats['other_services']}")
    print(f"  '[Service] Near You' converted:  {stats['near_you']}")
    print(f"  'Related Blog Posts' converted:  {stats['related_blogs']}")
    print(f"  'Related Articles' converted:    {stats['related_articles']}")
    print(f"  'Related Service' converted:     {stats['related_service']}")
    print(f"  Duplicate sections removed:      {stats['duplicates']}")
    print(f"  Errors:                          {stats['errors']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
