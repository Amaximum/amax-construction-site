#!/usr/bin/env python3
"""
Consolidate FAQ sections across all pages.
- Merge duplicate FAQ sections into ONE
- Place single FAQ card at the very end before footer
- Remove FAQ sections from other parts of the page
"""

import re
from pathlib import Path
import sys

def extract_faq_items(html_content):
    """Extract all FAQ items (details/summary pairs) from page."""
    # Pattern for <details> FAQ items
    details_pattern = r'<details[^>]*class="faq-item"[^>]*>.*?</details>'
    matches = re.findall(details_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    return matches

def remove_old_faq_sections(html_content):
    """Remove all existing FAQ section cards."""
    # Pattern to find FAQ island sections
    faq_section_pattern = r'<section[^>]*id="faq"[^>]*>.*?</section>'
    html_content = re.sub(faq_section_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove FAQ sections without ID
    faq_island_pattern = r'<section[^>]*class="[^"]*island[^"]*"[^>]*aria-label="[^"]*[Ff]requently[^"]*"[^>]*>.*?</section>'
    html_content = re.sub(faq_island_pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    return html_content

def create_unified_faq_card(faq_items):
    """Create a single unified FAQ card at the end."""
    if not faq_items:
        return ""
    
    # Remove duplicates by converting to set of strings
    unique_items = list(set(faq_items))
    
    faq_html = '''<section class="island reveal" id="faq" aria-label="Frequently asked questions">
  <span class="shine" aria-hidden="true"></span>
  <div class="section-head">
    <h2>Frequently Asked Questions</h2>
    <p>Common questions about our services.</p>
  </div>
  <div class="faq-list">
'''
    
    for item in unique_items:
        faq_html += item + "\n"
    
    faq_html += '''  </div>
</section>
'''
    
    return faq_html

def process_faq_on_page(html_content):
    """Process FAQ on a single page."""
    # Extract all FAQ items
    faq_items = extract_faq_items(html_content)
    
    if not faq_items:
        # No FAQ items found, nothing to do
        return html_content
    
    # Remove all old FAQ sections
    html_content = remove_old_faq_sections(html_content)
    
    # Create unified FAQ card
    unified_faq = create_unified_faq_card(faq_items)
    
    # Insert before footer (find <footer or </div> before footer)
    footer_pattern = r'(<footer|<div id="rating-widget")'
    match = re.search(footer_pattern, html_content, re.IGNORECASE)
    
    if match:
        insert_pos = match.start()
        html_content = html_content[:insert_pos] + unified_faq + "\n" + html_content[insert_pos:]
    
    return html_content

def process_file(filepath):
    """Process a single HTML file."""
    print(f"Processing: {filepath.name}")
    
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process FAQ
        new_content = process_faq_on_page(content)
        
        # Write back
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ FAQ consolidated")
            return True
        else:
            print(f"  ⊘ No changes needed")
            return False
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main function - process all HTML service pages."""
    base_path = Path(r'c:\Projects\SEO_Tool\amax-construction-site')
    
    # Find all service pages with index.html
    service_patterns = [
        'demolition-service-*/index.html',
        'basement-renovation-service-*/index.html',
        'carpenter-services-*/index.html',
        'fence-contractor-*/index.html',
        'handyman-service-*/index.html',
    ]
    
    print("Consolidating FAQ sections across all pages...\n")
    
    processed_count = 0
    total_count = 0
    
    for pattern in service_patterns:
        for filepath in base_path.glob(pattern):
            total_count += 1
            if process_file(filepath):
                processed_count += 1
    
    print(f"\n✓ Complete! Processed {processed_count}/{total_count} files.")

if __name__ == '__main__':
    main()
