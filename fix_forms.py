"""
fix_forms.py — Replace mailto: modal form handlers with Formsubmit.co AJAX.
Run: python fix_forms.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

CANDIDATES = [
    'deck-builder/index.html',
    'deck-builder-toronto/index.html',
    'deck-builder-gta/index.html',
    'deck-builder-newmarket/index.html',
    'deck-builder-schomberg/index.html',
    'deck-builder-in-richmond-hill/index.html',
    'deck-contractor-woodbridge/index.html',
    'deck-contractor-scarborough/index.html',
    'deck-contractor-north-york/index.html',
    'deck-contractor-markham/index.html',
    'deck-contractor-king-city/index.html',
    'deck-contractor-burlington/index.html',
    'deck-contractor-bradford/index.html',
    'deck-railing-installer-east-york/index.html',
    'deck-railing-builder-richmond-hill/index.html',
    'services/handyman-plumbing.html',
    'services/service-template.html',
    'index-seo-2026.html',
]

NEW_HANDLER = (
    "f.onsubmit=async function(e){"
    "e.preventDefault();"
    "var btn=f.querySelector('button[type=\"submit\"]');"
    "if(btn){btn.disabled=true;btn.textContent='Sending…';}"
    "try{"
    "var fd=new FormData(f);"
    "fd.append('_subject','New Booking Request — aMaximum Construction');"
    "fd.append('_template','table');"
    "fd.append('_captcha','false');"
    "var r=await fetch('https://formsubmit.co/ajax/amaximumconstructioncorp@gmail.com',"
    "{method:'POST',headers:{Accept:'application/json'},body:fd});"
    "var j=await r.json();"
    "if(j&&(j.success===true||j.success==='true')){"
    "f.reset();"
    "close();"
    "alert('Your request has been sent! We will contact you within 24 hours.');}"
    "else{"
    "alert('Could not send. Please try again or email us at amaximumconstructioncorp@gmail.com.');}"
    "}"
    "catch(err){"
    "alert('Could not send. Please check your connection and try again.');}"
    "finally{"
    "if(btn){btn.disabled=false;btn.textContent='Send';}}"
    "}"
)

updated = []
skipped = []

for page in CANDIDATES:
    filepath = os.path.join(BASE, page.replace('/', os.sep))
    if not os.path.exists(filepath):
        skipped.append((page, 'file not found'))
        continue

    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # Find the mailto: form submit handler
    start = content.find('f.onsubmit=e=>{')
    if start == -1:
        skipped.append((page, 'no f.onsubmit=e=>{ found'))
        continue

    mailto_check = content.find('window.location.href=`mailto:', start)
    if mailto_check == -1:
        skipped.append((page, 'f.onsubmit found but no mailto: href'))
        continue

    # The handler is minified on one line — find end of line
    newline_pos = content.find('\n', start)
    if newline_pos == -1:
        newline_pos = len(content)

    line_content = content[start:newline_pos]

    # End of handler = last }; on the same line
    handler_end_in_line = line_content.rfind('};')
    if handler_end_in_line == -1:
        skipped.append((page, 'could not find handler end };'))
        continue

    handler_end = start + handler_end_in_line + 2
    new_content = content[:start] + NEW_HANDLER + content[handler_end:]

    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write(new_content)

    updated.append(page)

print('=' * 55)
print('UPDATED:')
for p in updated:
    print(f'  OK  {p}')

print()
print('SKIPPED:')
for p, reason in skipped:
    print(f'  --  {p}  ({reason})')

print()
print(f'Total updated: {len(updated)}  |  Skipped: {len(skipped)}')
print('=' * 55)
print()
print('NEXT STEP:')
print('  Check Gmail (amaximumconstructioncorp@gmail.com) for a')
print('  confirmation email from formsubmit.co and click the')
print('  activation link — only needed ONCE to activate the service.')
