#!/usr/bin/env python3
"""
Universal FAQ consolidator v2.
- Handles BOTH <details class="faq-item"> and <dl><dt><dd> FAQ formats
- Processes every folder containing index.html
- Removes ALL existing FAQ sections (anywhere on page)
- Inserts a single consolidated FAQ card just before <footer>
"""

import re
from pathlib import Path
import html

BASE = Path(r'c:\Projects\SEO_Tool\amax-construction-site')

# Folders we never want to touch
SKIP_DIRS = {
    '.git', '.venv', 'node_modules', '__pycache__', 'img', 'assets',
    'css', 'js', 'fonts', 'icons', 'images', 'video', 'videos',
}

# ---------- extraction ----------

def extract_details_faqs(text):
    """Return list of (question, answer) tuples from <details class="faq-item">."""
    out = []
    for m in re.finditer(
        r'<details[^>]*class="[^"]*faq-item[^"]*"[^>]*>(.*?)</details>',
        text, flags=re.DOTALL | re.IGNORECASE):
        inner = m.group(1)
        qm = re.search(r'<summary[^>]*>(.*?)</summary>', inner, re.DOTALL | re.IGNORECASE)
        if not qm:
            continue
        q = qm.group(1).strip()
        a = inner[qm.end():].strip()
        # strip wrapping <p> if just one paragraph
        out.append((q, a))
    return out

def extract_dl_faqs(text):
    """Return list of (question, answer) from a <dl> block that looks like FAQ.

    A 'FAQ dl' is one that has at least 2 <dt>/<dd> pairs AND is preceded by
    an h2/h3 containing 'Frequently Asked Questions' or 'FAQ'.
    """
    out = []
    # Find <dl>...</dl> blocks
    for dl_match in re.finditer(r'<dl[^>]*>(.*?)</dl>', text, re.DOTALL | re.IGNORECASE):
        dl_inner = dl_match.group(1)
        # Look 300 chars before for FAQ heading
        before = text[max(0, dl_match.start()-400):dl_match.start()]
        if not re.search(r'<h[1-6][^>]*>[^<]*(?:Frequently Asked Questions|FAQ)\b',
                         before, re.IGNORECASE):
            continue
        pairs = re.findall(
            r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>',
            dl_inner, re.DOTALL | re.IGNORECASE)
        for q, a in pairs:
            # strip leading <strong> wrappers in question
            q_clean = re.sub(r'^\s*<strong[^>]*>(.*?)</strong>\s*$', r'\1',
                             q.strip(), flags=re.DOTALL | re.IGNORECASE)
            out.append((q_clean.strip(), a.strip()))
    return out

# ---------- removal ----------

def remove_existing_faq_sections(text):
    """Remove FAQ blocks in any of these forms:
      A) <section ... id="faq" ...>...</section>
      B) <section ... aria-label="...frequently asked questions..." ...>...</section>
      C) An <h2>Frequently Asked Questions</h2> followed by <dl>...</dl> (and
         possibly intervening whitespace). We only remove the heading + dl.
    """
    # A & B
    text = re.sub(
        r'<section[^>]*id="faq"[^>]*>.*?</section>\s*',
        '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(
        r'<section[^>]*aria-label="[^"]*[Ff]requently\s+[Aa]sked\s+[Qq]uestions[^"]*"[^>]*>.*?</section>\s*',
        '', text, flags=re.DOTALL | re.IGNORECASE)

    # C: heading + dl (only if dl contains dt/dd)
    def _dl_replacer(m):
        return ''
    text = re.sub(
        r'<h[1-6][^>]*>\s*(?:Frequently Asked Questions|FAQ)[^<]*</h[1-6]>\s*<dl[^>]*>.*?</dl>\s*',
        _dl_replacer, text, flags=re.DOTALL | re.IGNORECASE)

    # Also remove stray <details class="faq-item"> blocks not in a section
    text = re.sub(
        r'<details[^>]*class="[^"]*faq-item[^"]*"[^>]*>.*?</details>\s*',
        '', text, flags=re.DOTALL | re.IGNORECASE)

    return text

# ---------- building ----------

def dedup(pairs):
    seen = set()
    out = []
    for q, a in pairs:
        key = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', q)).strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append((q, a))
    return out

def build_consolidated_card(pairs):
    items = []
    for q, a in pairs:
        # Ensure answer is wrapped in <p> if it's just text
        a_stripped = a.strip()
        if not re.match(r'^\s*<(p|ul|ol|div|blockquote|table)\b', a_stripped, re.IGNORECASE):
            a_html = f'<p>{a_stripped}</p>'
        else:
            a_html = a_stripped
        items.append(
            f'    <details class="faq-item">\n'
            f'      <summary>{q.strip()}</summary>\n'
            f'      {a_html}\n'
            f'    </details>'
        )
    body = '\n'.join(items)
    return (
        '\n<section class="island reveal" id="faq" style="margin-top:18px;" '
        'aria-label="Frequently asked questions">\n'
        '  <span class="shine" aria-hidden="true"></span>\n'
        '  <div class="section-head">\n'
        '    <h2>Frequently Asked Questions</h2>\n'
        '  </div>\n'
        '  <div class="faq-list" style="padding:0 24px 16px;">\n'
        f'{body}\n'
        '  </div>\n'
        '</section>\n'
    )

# ---------- per-file pipeline ----------

def process_file(path):
    try:
        original = path.read_text(encoding='utf-8')
    except Exception as e:
        return ('read-error', str(e))

    details_pairs = extract_details_faqs(original)
    dl_pairs = extract_dl_faqs(original)
    all_pairs = dedup(details_pairs + dl_pairs)

    if not all_pairs:
        return ('no-faq', 0)

    # Remove existing FAQ blocks
    cleaned = remove_existing_faq_sections(original)

    # Build new card
    new_card = build_consolidated_card(all_pairs)

    # Insert just before <footer ...> (first occurrence)
    footer_re = re.compile(r'<footer\b', re.IGNORECASE)
    fm = footer_re.search(cleaned)
    if fm:
        new_html = cleaned[:fm.start()] + new_card + '\n' + cleaned[fm.start():]
    else:
        # Fallback: before </body>
        bm = re.search(r'</body>', cleaned, re.IGNORECASE)
        if not bm:
            return ('no-footer', 0)
        new_html = cleaned[:bm.start()] + new_card + '\n' + cleaned[bm.start():]

    if new_html == original:
        return ('unchanged', len(all_pairs))

    path.write_bytes(new_html.encode('utf-8'))
    return ('updated', len(all_pairs))

# ---------- driver ----------

def main():
    targets = []
    for child in BASE.iterdir():
        if not child.is_dir() or child.name in SKIP_DIRS or child.name.startswith('.'):
            continue
        idx = child / 'index.html'
        if idx.is_file():
            targets.append(idx)

    print(f'Scanning {len(targets)} index.html pages...\n')
    counts = {'updated': 0, 'no-faq': 0, 'unchanged': 0, 'read-error': 0, 'no-footer': 0}
    updated_files = []
    for p in targets:
        status, info = process_file(p)
        counts[status] = counts.get(status, 0) + 1
        if status == 'updated':
            updated_files.append((p.parent.name, info))
        elif status in ('read-error', 'no-footer'):
            print(f'  ! {p.parent.name}: {status} ({info})')

    print(f'\nSummary:')
    for k, v in counts.items():
        print(f'  {k:12} {v}')
    print(f'\nUpdated {len(updated_files)} files:')
    for name, n in updated_files[:80]:
        print(f'  - {name}  ({n} FAQs)')

if __name__ == '__main__':
    main()
