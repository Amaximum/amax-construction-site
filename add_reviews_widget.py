"""
add_reviews_widget.py
Adds the Elfsight Google Reviews corner badge to all HTML pages that don't have it.
Skips template/staging files.
"""
import os, re

ROOT = r'c:\Users\maxim\Desktop\amax-Construction-site'
SKIP_FILES = {'index-seo-2026.html', 'service-template.html'}

WIDGET_ID = 'elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875'
ELFSIGHT_SCRIPT = '<script src="https://static.elfsight.com/platform/platform.js" async></script>'

BADGE_HTML = '''<div class="elfsight-review-badge" id="reviews-badge" style="position:fixed;right:14px;bottom:14px;z-index:9999;max-width:164px;pointer-events:auto;">
  <div class="elfsight-app-3935cedc-67a1-44d8-b85e-f841374ae875" data-elfsight-app-lazy></div>
</div>'''

added = []
skipped_has_widget = []
skipped_file = []
errors = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # Skip hidden dirs
    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
    for fname in filenames:
        if not fname.endswith('.html'):
            continue
        if fname in SKIP_FILES:
            skipped_file.append(os.path.join(dirpath, fname))
            continue

        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Skip if already has widget
            if WIDGET_ID in content:
                skipped_has_widget.append(fpath)
                continue

            modified = content

            # Ensure Elfsight platform.js is in <head>
            if ELFSIGHT_SCRIPT not in modified:
                modified = modified.replace(
                    '<link rel="stylesheet" href="/css/styles.css">',
                    f'{ELFSIGHT_SCRIPT}\n<link rel="stylesheet" href="/css/styles.css">'
                )

            # Insert badge just before </footer> if footer exists, else before </body>
            if '</footer>' in modified:
                modified = modified.replace('</footer>', BADGE_HTML + '\n</footer>', 1)
            elif '</body>' in modified:
                modified = modified.replace('</body>', BADGE_HTML + '\n</body>', 1)
            else:
                errors.append(f'No </footer> or </body> found: {fpath}')
                continue

            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(modified)

            added.append(fpath)

        except Exception as e:
            errors.append(f'{fpath}: {e}')

# Report
print(f'\nWidget added to {len(added)} pages')
print(f'Already had widget: {len(skipped_has_widget)} pages')
print(f'Skipped (template): {len(skipped_file)} files')
if errors:
    print(f'\nErrors ({len(errors)}):')
    for e in errors:
        print(f'   {e}')
else:
    print('Errors: 0')

print('\nDone.')
