import os, re, sys

root = r'c:\Users\maxim\Desktop\amax-Construction-site'
all_links = set()

for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'img', 'css', '.venv']]
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            text = open(fpath, encoding='utf-8', errors='ignore').read()
            for m in re.finditer(r'href="(/[^"#?]+)"', text):
                link = m.group(1)
                if not link.startswith('//') and 'mailto' not in link:
                    all_links.add(link)
        except:
            pass

missing = []
for link in sorted(all_links):
    if link.endswith('/'):
        check = os.path.join(root, link.lstrip('/').replace('/', os.sep), 'index.html')
    else:
        check = os.path.join(root, link.lstrip('/').replace('/', os.sep))
    if not os.path.exists(check):
        missing.append(link)

print(f'Total unique paths: {len(all_links)}')
print(f'Missing ({len(missing)}):')
for m in missing:
    print(' ', m)
