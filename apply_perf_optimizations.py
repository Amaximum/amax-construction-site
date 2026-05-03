"""Apply Elfsight defer + preconnect optimization to all HTML pages.

Replaces blocking <script src="https://static.elfsight.com/platform/platform.js" defer>
with an inline loader that defers Elfsight to first user interaction or
viewport intersection. Adds preconnect+dns-prefetch hints.

Idempotent: safe to re-run.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent

OLD_SCRIPT = '<script src="https://static.elfsight.com/platform/platform.js" defer></script>'

NEW_BLOCK = '''<link rel="preconnect" href="https://static.elfsight.com" crossorigin>
<link rel="dns-prefetch" href="https://static.elfsight.com">
<script>
// Lazy-load Elfsight platform.js to reduce TBT/LCP. Loads on first user
// interaction, when a widget enters viewport, or after 5s idle fallback.
(function(){
  var loaded = false;
  function load(){
    if (loaded) return; loaded = true;
    var s = document.createElement('script');
    s.src = 'https://static.elfsight.com/platform/platform.js';
    s.defer = true;
    document.head.appendChild(s);
    cleanup();
  }
  function cleanup(){
    ['scroll','touchstart','mousemove','keydown','click'].forEach(function(e){
      window.removeEventListener(e, load, {passive:true});
    });
  }
  ['scroll','touchstart','mousemove','keydown','click'].forEach(function(e){
    window.addEventListener(e, load, {passive:true, once:true});
  });
  if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', function(){
      var targets = document.querySelectorAll('[class*="elfsight-app-"]');
      if (!targets.length) return;
      var io = new IntersectionObserver(function(entries){
        entries.forEach(function(en){ if (en.isIntersecting){ load(); io.disconnect(); } });
      }, {rootMargin: '300px'});
      targets.forEach(function(t){ io.observe(t); });
    });
  }
  setTimeout(load, 5000);
})();
</script>'''

MARKER = 'static.elfsight.com" crossorigin'

changed = 0
skipped_already = 0
skipped_no_script = 0

for html in ROOT.rglob('*.html'):
    if 'node_modules' in html.parts or '.git' in html.parts:
        continue
    text = html.read_text(encoding='utf-8', errors='ignore')
    if OLD_SCRIPT not in text:
        if MARKER in text:
            skipped_already += 1
        else:
            skipped_no_script += 1
        continue
    if MARKER in text:
        # Already has loader; just remove the leftover blocking script
        new_text = text.replace(OLD_SCRIPT + '\n', '').replace(OLD_SCRIPT, '')
    else:
        new_text = text.replace(OLD_SCRIPT, NEW_BLOCK, 1)
        # Remove any additional duplicate copies of the old script
        new_text = new_text.replace(OLD_SCRIPT + '\n', '').replace(OLD_SCRIPT, '')
    if new_text != text:
        html.write_text(new_text, encoding='utf-8')
        changed += 1

print(f"Changed:  {changed}")
print(f"Already optimized (skipped): {skipped_already}")
print(f"No Elfsight script (skipped): {skipped_no_script}")
