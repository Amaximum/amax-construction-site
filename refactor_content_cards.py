#!/usr/bin/env python3
"""
Refactor service pages: Break large content into separate island cards with booking CTAs between them.
This script processes HTML files and restructures their content sections.
"""

import re
from pathlib import Path
import sys

# Service to booking form mapping
SERVICE_BOOKING_FORMS = {
    'demolition': '/book-demolition.html',
    'basement': '/book-basement.html',
    'bathroom': '/book-bathroom.html',
    'deck': '/book-deck.html',
    'fence': '/book-fence.html',
    'carpenter': '/book-carpentry.html',
    'carpentry': '/book-carpentry.html',
    'handyman': '/book-handy.html',
    'electrical': '/book-electrical.html',
    'plumbing': '/book-plumbing.html',
    'painting': '/book-painting.html',
    'excavation': '/book-excavation.html',
    'landscaping': '/book-landscaping.html',
    'canopy': '/book-canopy.html',
    'interlock': '/book-interlock.html',
    'christmas': '/book-christmas.html',
    'general': '/book-contractor.html',
    'contractor': '/book-contractor.html',
}

# Sample CTA button texts
CTA_BUTTONS = [
    "Get Your Free Estimate Today!",
    "Schedule Your Free Site Assessment Today!",
    "Get a Free Quote Now!",
    "Contact Our Team Today!",
    "Book Your Consultation Now!",
]

def get_booking_form(filename):
    """Determine booking form URL from filename."""
    filename_lower = filename.lower()
    
    for service, form_url in SERVICE_BOOKING_FORMS.items():
        if service in filename_lower:
            return form_url
    
    # Default to general contractor form
    return '/book-contractor.html'

def extract_service_name(filepath):
    """Extract service name from file path for better CTA text."""
    path_parts = str(filepath).lower().split('\\')
    
    # Try to find service name from directory
    for part in path_parts:
        if any(service in part for service in SERVICE_BOOKING_FORMS.keys()):
            return part
    
    return None

def split_content_into_sections(content_div_html):
    """
    Split content div into sections based on h2 headings.
    Returns list of tuples: (heading, content_html)
    """
    # Find all h2 tags and their following content
    h2_pattern = r'<h2>(.*?)</h2>'
    h2_matches = list(re.finditer(h2_pattern, content_div_html, re.IGNORECASE))
    
    if not h2_matches:
        return []
    
    sections = []
    for i, match in enumerate(h2_matches):
        heading = match.group(1)
        start = match.start()
        
        # Find the end of this section (next h2 or end of div)
        if i + 1 < len(h2_matches):
            end = h2_matches[i + 1].start()
        else:
            end = len(content_div_html)
        
        section_html = content_div_html[start:end].rstrip()
        sections.append((heading, section_html))
    
    return sections

def create_island_card(section_html, index):
    """Convert section HTML into an island card."""
    card_html = f'''<!-- Section Card #{index} -->
<section class="island reveal" aria-label="Service section {index}">
  <span class="shine" aria-hidden="true"></span>
  <div style="padding:0 24px;">
    {section_html}
  </div>
</section>'''
    return card_html

def create_cta_button(booking_form, button_text):
    """Create CTA button HTML."""
    button_html = f'''<!-- Booking CTA -->
<div style="text-align:center;margin:24px 0;">
  <a class="btn btn-primary" href="{booking_form}" style="display:inline-block;">{button_text}</a>
</div>'''
    return button_html

def process_content_container(html_content, booking_form):
    """
    Process the main content container and convert to card structure.
    """
    # Find the main content div (usually <div class="container"><div class="content">...</div>)
    container_pattern = r'<div class="container">\s*<div class="content">(.*?)</div>\s*<div class="cta-section">'
    match = re.search(container_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    if not match:
        # Try alternative pattern
        container_pattern = r'<div class="container">(.*?)<section.*?id="why-choose-us"'
        match = re.search(container_pattern, html_content, re.DOTALL | re.IGNORECASE)
        if not match:
            return html_content
    
    content_html = match.group(1).strip()
    
    # Split into sections
    sections = split_content_into_sections(content_html)
    
    if not sections or len(sections) < 2:
        return html_content
    
    # Build new card structure
    new_content = ""
    for i, (heading, section_html) in enumerate(sections):
        # Create island card
        new_content += create_island_card(section_html, i + 1)
        
        # Add CTA button between cards (not after last one)
        if i < len(sections) - 1:
            cta_text = CTA_BUTTONS[i % len(CTA_BUTTONS)]
            new_content += "\n" + create_cta_button(booking_form, cta_text) + "\n"
    
    # Replace the old container with new structure
    old_container = match.group(0)
    
    # Find where the old container ends (before the "Why Choose" section)
    new_html = html_content.replace(
        old_container,
        new_content + "\n"
    )
    
    return new_html

def process_file(filepath):
    """Process a single HTML file."""
    print(f"Processing: {filepath}")
    
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get booking form URL
        booking_form = get_booking_form(filepath.name)
        
        # Process content
        new_content = process_content_container(content, booking_form)
        
        # Write back
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ Updated successfully")
            return True
        else:
            print(f"  ⊘ No changes needed")
            return False
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main function."""
    base_path = Path(r'c:\Projects\SEO_Tool\amax-construction-site')
    
    # Priority list of files to process
    priority_files = [
        # Main service pages
        'demolition-service-in-toronto/index.html',
        'demolition-service-in-aurora/index.html',
        'demolition-service-in-markham/index.html',
        'basement-renovation-service-in-toronto/index.html',
        'basement-renovation-service-in-aurora/index.html',
    ]
    
    print("Starting refactor of service pages...\n")
    
    updated_count = 0
    for file_path in priority_files:
        full_path = base_path / file_path
        if full_path.exists():
            if process_file(full_path):
                updated_count += 1
        else:
            print(f"File not found: {full_path}")
    
    print(f"\n✓ Refactoring complete! Updated {updated_count} files.")

if __name__ == '__main__':
    main()
