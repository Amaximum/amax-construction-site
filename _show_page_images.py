import os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
targets = []
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in {'.git','node_modules','.venv','__pycache__'}]
    for f in fn:
        if not f.lower().endswith('.html'):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT).replace('\\','/')
        raw = open(p, encoding='utf-8', errors='replace').read()
        if 'noindex' in raw.lower():
            continue
        if re.search(r'property=["\']og:image["\']', raw, re.I) and re.search(r'name=["\']twitter:image["\']', raw, re.I):
            continue
        if rel == 'services/service-template.html':
            continue
        # collect images referenced in the body (img/services or any /img/)
        imgs = re.findall(r'(?:src|href)=["\']([^"\']*?/img/[^"\']+\.(?:jpg|jpeg|png|webp))["\']', raw, re.I)
        # normalize, keep order unique
        seen = []
        for i in imgs:
            if i not in seen:
                seen.append(i)
        print(f'### {rel}')
        for i in seen[:8]:
            print('   ', i)
        if not seen:
            print('    (no /img/ refs found)')
        print()
