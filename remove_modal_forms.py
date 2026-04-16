#!/usr/bin/env python3
"""
Remove modal form remnants from pages that have them.
These are orphaned form fields, </form>, </div> closers, and <script> blocks
referencing bookingModal/bookingForm that no longer exist as visible HTML elements.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).parent


def find_pages_with_modal():
    """Find all index.html files containing bookingModal references (not book-*.html)."""
    pages = []
    for root, dirs, files in os.walk(ROOT):
        for f in files:
            if f == "index.html":
                path = Path(root) / f
                rel = path.relative_to(ROOT).as_posix()
                if rel.startswith("book-"):
                    continue
                html = path.read_text(encoding="utf-8")
                if "bookingModal" in html:
                    pages.append(path)
    return pages


def clean_modal_form(html):
    """Remove modal form leftovers from HTML content."""
    
    # Pattern 1: Remove orphaned form fields block
    # These are <div class="form-group"> blocks up through </form></div></div>
    # that appear after the CTA div and before the <script>
    
    # Remove form field divs (form-group, form-row) that are orphaned
    html = re.sub(
        r'<div class="form-group">.*?</div>\s*\n?',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove form-row blocks  
    html = re.sub(
        r'<div class="form-row">.*?</div>\s*\n?</div>\s*\n?',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove button rows for modal (Cancel + Send)
    html = re.sub(
        r'<div style="display:flex;gap:12px;margin-top:20px">\s*<button type="button".*?Cancel</button>\s*<button type="submit".*?Send</button>\s*</div>\s*\n?',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove orphaned </form> 
    # Remove the comment + CTA replacement that was added previously
    html = re.sub(
        r'<!-- .*?удалена.*?-->\s*\n?',
        '',
        html,
    )
    
    # Remove orphaned </form></div></div> before <script>
    html = re.sub(
        r'</form>\s*\n</div>\s*\n</div>\s*\n(?=<script>)',
        '',
        html,
    )
    
    return html


def clean_modal_script(html):
    """Remove the <script> block containing bookingModal code."""
    
    # The script contains modal logic + reveal observer
    # We want to keep the reveal observer but remove the modal code
    
    # Pattern: <script> block that starts with modal code
    pattern = r'<script>\s*\n?const m=document\.getElementById\([\'"]bookingModal[\'"]\).*?</script>'
    
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return html
    
    script_content = match.group(0)
    
    # Extract the reveal observer code (we want to keep it)
    reveal_match = re.search(r'(// Reveal on scroll.*?)(?=</script>)', script_content, re.DOTALL)
    
    if reveal_match:
        reveal_code = reveal_match.group(1).strip()
        replacement = f'<script>\n{reveal_code}\n</script>'
    else:
        # Also check for Mobile menu + Reveal on scroll
        reveal_match2 = re.search(r'(// Mobile menu.*?)(?=</script>)', script_content, re.DOTALL)
        if reveal_match2:
            reveal_code = reveal_match2.group(1).strip()
            replacement = f'<script>\n{reveal_code}\n</script>'
        else:
            replacement = ''
    
    html = html[:match.start()] + replacement + html[match.end():]
    return html


def process_file(path):
    """Process a single file: remove modal form + script."""
    html = path.read_text(encoding="utf-8")
    original = html
    
    html = clean_modal_form(html)
    html = clean_modal_script(html)
    
    # Clean up excess blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    pages = find_pages_with_modal()
    print(f"Found {len(pages)} pages with modal form remnants")
    print("=" * 60)
    
    updated = 0
    for path in sorted(pages):
        rel = path.relative_to(ROOT).as_posix()
        result = process_file(path)
        if result:
            print(f"  OK {rel}")
            updated += 1
        else:
            print(f"  -- {rel} (no changes needed)")
    
    print(f"\nUpdated: {updated}/{len(pages)}")


if __name__ == "__main__":
    main()
