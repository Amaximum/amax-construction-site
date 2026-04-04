#!/usr/bin/env python3
"""
Fix shortened footers on service hubs
"""

import os

# Full footer template (Services and Locations columns)
FULL_FOOTER_COLS = '''      <div class="footer-col">
        <h4>Services</h4>
        <ul>
          <li><a href="/deck-builder/">Deck Building</a></li>
          <li><a href="/deck-railings-toronto/">Deck Railings</a></li>
          <li><a href="/fence-contractor-in-toronto/">Fence Installation</a></li>
          <li><a href="/bathroom-renovation/">Bathroom Renovation</a></li>
          <li><a href="/basement-renovation-service-in-toronto/">Basement Renovation</a></li>
          <li><a href="/handyman-plumbing-services/">Plumbing</a></li>
          <li><a href="/electrical-handyman-services/">Electrical</a></li>
          <li><a href="/handyman-painting-services/">Painting</a></li>
          <li><a href="/canopy/">Canopy &amp; Awnings</a></li>
          <li><a href="/landscaping-services-toronto/">Landscaping</a></li>
          <li><a href="/handyman-service-in-toronto/">Handyman</a></li>
          <li><a href="/general-contractor-in-toronto/">General Contractor</a></li>
          <li><a href="/interlocking-paver-services/">Interlocking &amp; Paving</a></li>
          <li><a href="/carpenter-services/">Carpentry</a></li>
          <li><a href="/demolition-services/">Demolition</a></li>
          <li><a href="/excavation-services/">Excavation</a></li>
          <li><a href="/home-renovation/">Home Renovation</a></li>
          <li><a href="/christmas-lights-installation-toronto-gta/">Christmas Lights</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Locations</h4>
        <ul>
          <li><a href="/locations/toronto/">Toronto</a></li>
          <li><a href="/locations/markham/">Markham</a></li>
          <li><a href="/locations/richmond-hill/">Richmond Hill</a></li>
          <li><a href="/locations/vaughan/">Vaughan</a></li>
          <li><a href="/locations/newmarket/">Newmarket</a></li>
          <li><a href="/locations/">All Locations &rarr;</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Company</h4>'''

# Old short footer (only Company)
SHORT_FOOTER = '''      <div class="footer-col">
        <h4>Company</h4>'''

# Files to fix
files_to_fix = [
    'basement-renovation/index.html',
    'fence-installation/index.html',
    'general-contractor/index.html',
    'handyman-services/index.html',
    'landscaping-services/index.html'
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Not found: {filepath}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if SHORT_FOOTER in content and '/home-renovation/' not in content:
        content = content.replace(SHORT_FOOTER, FULL_FOOTER_COLS)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
    else:
        print(f"Already OK or different pattern: {filepath}")
