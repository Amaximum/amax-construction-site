#!/usr/bin/env python3
"""
Refactor content cards v2 — Split single-container content into multiple
island cards with service-specific booking CTAs between them.

Input pattern (typical untouched page):
  <div class="container">
    <div class="content">
      <h2>Section 1</h2>
      ...paragraphs/lists...
      <h2>Section 2</h2>
      ...
    </div>
    <div class="cta-section">
      <h2>Ready to ...</h2>
      <a class="btn" href="/book-X.html">BOOK NOW</a>
    </div>
  </div>

Output:
  <section class="island reveal" style="margin-top:18px;">
    <span class="shine"></span>
    <div class="section-head"><h2>Section 1</h2></div>
    <div style="padding:0 24px;">...paragraphs...</div>
  </section>
  <CTA button>
  <section class="island reveal">Section 2 card</section>
  <CTA button>
  ...
  (original cta-section preserved at the end as final BOOK NOW)
"""

import re
from pathlib import Path

BASE = Path(r'c:\Projects\SEO_Tool\amax-construction-site')

SERVICE_FORMS = [
    ('basement-renovation',         '/book-basement.html'),
    ('basement',                    '/book-basement.html'),
    ('bathroom-renovation',         '/book-bathroom.html'),
    ('bathroom',                    '/book-bathroom.html'),
    ('demolition',                  '/book-demolition.html'),
    ('deck-railing',                '/book-railing.html'),
    ('deck-builder',                '/book-deck.html'),
    ('deck-contractor',             '/book-deck.html'),
    ('deck',                        '/book-deck.html'),
    ('fence',                       '/book-fence.html'),
    ('carpenter',                   '/book-carpentry.html'),
    ('carpentry',                   '/book-carpentry.html'),
    ('handyman',                    '/book-handy.html'),
    ('electrical',                  '/book-electrical.html'),
    ('plumbing',                    '/book-plumbing.html'),
    ('painting',                    '/book-painting.html'),
    ('excavation',                  '/book-excavation.html'),
    ('landscaping',                 '/book-landscaping.html'),
    ('canopy',                      '/book-canopy.html'),
    ('interlock',                   '/book-interlock.html'),
    ('christmas',                   '/book-christmas.html'),
    ('general-contractor',          '/book-contractor.html'),
    ('contractor',                  '/book-contractor.html'),
    ('home-renovation',             '/book-renovation.html'),
    ('renovation',                  '/book-renovation.html'),
]

CTA_TEXTS = [
    'Get Your Free Estimate Today!',
    'Schedule Your Free Site Assessment!',
    'Get a Free Quote Now!',
    'Book Your Consultation Today!',
    'Contact Our Team Today!',
]

# Skip these — already restructured / special structure / non-service pages
SKIP_FOLDERS = {
    'demolition-service-in-king-city',      # already done
    'demolition-service-in-toronto',        # already done
    'book-now', 'blog', 'client-testimonials',
    'general-contractor-services-2',
}


def detect_form(folder_name):
    n = folder_name.lower()
    for key, form in SERVICE_FORMS:
        if key in n:
            return form
    return '/book-contractor.html'


def build_card(heading_html, body_html, idx):
    margin = ' style="margin-top:18px;"' if idx == 0 else ''
    label = re.sub(r'<[^>]+>', '', heading_html).strip()[:80]
    label = re.sub(r'\s+', ' ', label) or f'Section {idx+1}'
    return (
        f'\n<section class="island reveal"{margin} aria-label="{label}">\n'
        f'  <span class="shine" aria-hidden="true"></span>\n'
        f'  <div class="section-head">\n'
        f'    <h2>{heading_html}</h2>\n'
        f'  </div>\n'
        f'  <div style="padding:0 24px 16px;">\n'
        f'{body_html.rstrip()}\n'
        f'  </div>\n'
        f'</section>'
    )


def build_cta(form_url, text):
    return (
        f'\n<div style="text-align:center;margin:24px 0;">\n'
        f'  <a class="btn btn-primary" href="{form_url}" style="display:inline-block;">{text}</a>\n'
        f'</div>'
    )


# Match the .container > .content block (greedy until matching </div> closing .content)
# We use a non-greedy approach against a sentinel: the closing </div> immediately
# followed by whitespace and then <div class="cta-section"> OR </div> closing
# .container.
CONTAINER_RE = re.compile(
    r'(<div\s+class="container">\s*<div\s+class="content">)(.*?)(</div>\s*(?=<div\s+class="cta-section">|</div>))',
    re.DOTALL | re.IGNORECASE,
)


def split_by_h2(html_block):
    """Split a chunk of HTML into [(heading_inner_html, body_html), ...] using <h2>.

    Anything before the first <h2> becomes a leading body assigned to the FIRST
    section as preface (or, if there is no <h2> at all, returns []).
    """
    h2_re = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL | re.IGNORECASE)
    matches = list(h2_re.finditer(html_block))
    if not matches:
        return []
    sections = []
    leading = html_block[:matches[0].start()].strip()
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i+1].start() if i+1 < len(matches) else len(html_block)
        body = html_block[body_start:body_end].strip()
        if i == 0 and leading:
            body = leading + '\n' + body
        sections.append((heading, body))
    return sections


def process_html(html_text, folder_name):
    m = CONTAINER_RE.search(html_text)
    if not m:
        return html_text, 'no-container'

    inner = m.group(2)
    sections = split_by_h2(inner)
    if len(sections) < 2:
        return html_text, 'too-few-sections'

    form_url = detect_form(folder_name)

    parts = []
    for i, (heading, body) in enumerate(sections):
        parts.append(build_card(heading, body, i))
        if i < len(sections) - 1:
            parts.append(build_cta(form_url, CTA_TEXTS[i % len(CTA_TEXTS)]))

    new_block = '\n'.join(parts) + '\n'

    # Replace the entire <div class="container"><div class="content">...</div>
    # with our new structure. We must also strip the original opening
    # <div class="container"><div class="content"> wrapper AND the trailing
    # </div> that closes .content, plus the closing </div> that closes
    # .container — BUT preserve the .cta-section if present.

    # Locate full container span: from start of m.group(0)'s wrapper to the
    # closing </div> of .container.
    container_start = m.start(1)  # start of <div class="container"><div class="content">
    # Find .content closing position
    content_close_end = m.end(3)  # position just after </div> closing .content

    # Now examine what follows content_close_end: either <div class="cta-section">...</div></div>
    # or just </div> closing .container.
    tail = html_text[content_close_end:]
    cta_section_re = re.compile(r'\s*<div\s+class="cta-section">.*?</div>\s*</div>', re.DOTALL | re.IGNORECASE)
    cta_m = cta_section_re.match(tail)
    if cta_m:
        # Keep the .cta-section but unwrap from .container
        cta_block_only = re.search(
            r'<div\s+class="cta-section">.*?</div>',
            cta_m.group(0), re.DOTALL | re.IGNORECASE).group(0)
        end_of_container = content_close_end + cta_m.end()
        replacement = new_block + '\n' + cta_block_only + '\n'
    else:
        # Just closing </div> of container
        end_close_re = re.compile(r'\s*</div>', re.IGNORECASE)
        ec = end_close_re.match(tail)
        if not ec:
            return html_text, 'unmatched-container-close'
        end_of_container = content_close_end + ec.end()
        replacement = new_block

    new_html = html_text[:container_start] + replacement + html_text[end_of_container:]
    return new_html, 'updated'


def main():
    targets = []
    for child in sorted(BASE.iterdir()):
        if not child.is_dir() or child.name.startswith('.') or child.name in SKIP_FOLDERS:
            continue
        idx = child / 'index.html'
        if idx.is_file():
            targets.append(idx)

    print(f'Scanning {len(targets)} pages...\n')
    counts = {}
    updated = []
    errors = []

    for p in targets:
        try:
            original = p.read_text(encoding='utf-8')
        except Exception as e:
            errors.append((p.parent.name, f'read: {e}'))
            counts['read-error'] = counts.get('read-error', 0) + 1
            continue

        new_html, status = process_html(original, p.parent.name)
        counts[status] = counts.get(status, 0) + 1
        if status == 'updated' and new_html != original:
            p.write_bytes(new_html.encode('utf-8'))
            updated.append(p.parent.name)

    print('\nSummary:')
    for k, v in sorted(counts.items()):
        print(f'  {k:25} {v}')
    print(f'\nUpdated {len(updated)} files.')
    if errors:
        print(f'\nErrors ({len(errors)}):')
        for name, msg in errors[:20]:
            print(f'  - {name}: {msg}')


if __name__ == '__main__':
    main()
