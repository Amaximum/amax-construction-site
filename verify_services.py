#!/usr/bin/env python3
"""
Full verification: all services from sitemap are on main page and in footers
"""

import os
import re
from xml.etree import ElementTree as ET

# Parse sitemap
tree = ET.parse('sitemap.xml')
root = tree.getroot()
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

sitemap_urls = []
for url in root.findall('sm:url/sm:loc', ns):
    path = url.text.replace('https://amaximumconstruction.com/', '').strip('/')
    if path:
        sitemap_urls.append(path)

print(f"Total URLs in sitemap: {len(sitemap_urls)}")

# Service hubs (canonical paths)
SERVICE_HUBS = {
    "Deck Building": ["deck-builder"],
    "Deck Railings": ["deck-railings-toronto", "deck-railings"],
    "Fence Installation": ["fence-installation", "fence-contractor-in-toronto"],
    "Bathroom Renovation": ["bathroom-renovation"],
    "Basement Renovation": ["basement-renovation", "basement-renovation-service-in-toronto"],
    "Handyman Services": ["handyman-services", "handyman-service-in-toronto"],
    "General Contractor": ["general-contractor", "general-contractor-in-toronto"],
    "Carpentry": ["carpenter-services"],
    "Demolition": ["demolition-services"],
    "Interlocking & Paving": ["interlocking-paver-services"],
    "Christmas Lights": ["christmas-lights-installation-toronto-gta"],
    "Home Renovation": ["home-renovation"],
    "Landscaping": ["landscaping-services-toronto"],
    "Plumbing": ["handyman-plumbing-services"],
    "Electrical": ["electrical-handyman-services"],
    "Painting": ["handyman-painting-services"],
    "Canopy & Awnings": ["canopy"],
    "Excavation": ["excavation-services"]
}

# Read main page
with open('index.html', 'r', encoding='utf-8') as f:
    main_page = f.read()

print("\n" + "="*60)
print("SERVICES ON MAIN PAGE (index.html)")
print("="*60)

all_ok = True
for service_name, paths in SERVICE_HUBS.items():
    found = False
    found_path = None
    for path in paths:
        if f'href="/{path}/' in main_page or f'href="/{path}"' in main_page:
            found = True
            found_path = path
            break
    
    if found:
        print(f"[OK] {service_name} -> /{found_path}/")
    else:
        print(f"[MISSING] {service_name} - NOT FOUND!")
        all_ok = False

# Check footer structure on main page
print("\n" + "="*60)
print("FOOTER STRUCTURE CHECK")
print("="*60)

footer_services = re.findall(r'<h4>Services</h4>.*?</ul>', main_page, re.DOTALL)
if footer_services:
    print(f"Footer Services section: FOUND")
    for service_name, paths in SERVICE_HUBS.items():
        found = any(path in footer_services[0] for path in paths)
        status = "[OK]" if found else "[MISS]"
        print(f"  {status} {service_name}")
else:
    print("Footer Services section: NOT FOUND!")

# Check locations section
footer_locations = re.findall(r'<h4>Locations</h4>.*?</ul>', main_page, re.DOTALL)
if footer_locations:
    print(f"\nFooter Locations section: FOUND")
else:
    print(f"\nFooter Locations section: NOT FOUND!")

# Verify all service hubs exist as folders
print("\n" + "="*60)
print("SERVICE HUB FOLDERS EXISTENCE")
print("="*60)

for service_name, paths in SERVICE_HUBS.items():
    for path in paths:
        if os.path.isdir(path) and os.path.exists(f"{path}/index.html"):
            print(f"[OK] {path}/")
            break
    else:
        print(f"[MISSING] {service_name} - no folder found for {paths}")

# Check sitemap contains all service hubs
print("\n" + "="*60)
print("SERVICE HUBS IN SITEMAP")
print("="*60)

for service_name, paths in SERVICE_HUBS.items():
    found = any(path in sitemap_urls for path in paths)
    if found:
        print(f"[OK] {service_name}")
    else:
        print(f"[MISSING] {service_name} - not in sitemap!")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total services: {len(SERVICE_HUBS)}")
print(f"Total sitemap URLs: {len(sitemap_urls)}")
