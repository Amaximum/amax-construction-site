"""Fix encoding bugs in all booking forms."""
from pathlib import Path

root = Path('.')
fixes = [
    ('weâ€™ll', "we'll"),
    ('Weâ€™ll', "We'll"),
    ('weâ€™re', "we're"),
    ('Weâ€™re', "We're"),
    ('â€™', "'"),
    ('â€œ', '"'),
    ('â€\x9d', '"'),
    ('â€"', '—'),
    ('â€"', '–'),
    ('Â ', ' '),
]

forms = sorted(root.glob('book-*.html'))
for f in forms:
    content = f.read_text(encoding='utf-8', errors='replace')
    original = content
    for bad, good in fixes:
        content = content.replace(bad, good)
    if content != original:
        f.write_text(content, encoding='utf-8')
        print(f'  FIXED: {f.name}')
    else:
        print(f'  OK: {f.name}')
