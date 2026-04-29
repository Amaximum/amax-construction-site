from pathlib import Path

issues_all = {}
for f in sorted(Path('.').glob('book-*.html')):
    content = f.read_text(encoding='utf-8')
    issues = []
    if 'formsubmit.co/amaximumconstructioncorp@gmail.com' not in content:
        issues.append('WRONG_ACTION')
    if 'thank-you-page' not in content:
        issues.append('NO_REDIRECT')
    for fid in ['clientName','clientPhone','clientEmail','clientAddress','consultDate','timeSlot','serviceType']:
        if fid not in content:
            issues.append('MISSING_FIELD:' + fid)
    if '_honey' not in content:
        issues.append('NO_HONEYPOT')
    if 'submitButton.disabled = true' not in content:
        issues.append('NO_DOUBLE_SUBMIT_PREVENTION')
    if 'AIzaSy' in content:
        issues.append('GOOGLE_API_KEY_EXPOSED')
    if 'setAttribute' not in content:
        issues.append('NO_MIN_DATE')
    if not issues:
        issues = ['ALL_OK']
    issues_all[f.name] = issues

for fname, issues in issues_all.items():
    sep = ' | '
    print(fname + ': ' + sep.join(issues))
