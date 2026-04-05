#!/usr/bin/env python3
"""
Image audit for service pages
"""

import os
import re
from pathlib import Path

# Read main page to check what images are expected
with open('index.html', 'r', encoding='utf-8') as f:
    main_page = f.read()

# Extract all image references from main page services section
service_images = re.findall(r'<img src="(img/services/[^"]+)"', main_page)

print("="*60)
print("IMAGE AUDIT FOR SERVICES")
print("="*60)

# Group by service
services = {}
for img_path in service_images:
    # Extract service name from path
    filename = os.path.basename(img_path)
    # Get service prefix (e.g., "deck-user-1.jpg" -> "deck")
    parts = filename.replace('.jpg', '').replace('.svg', '').replace('.png', '').split('-')
    
    if 'user' in parts:
        service = parts[0]  # e.g., "deck" from "deck-user-1"
    elif parts[-1].isdigit():
        service = '-'.join(parts[:-1])  # e.g., "deck-railings" from "deck-railings-1"
    else:
        service = '-'.join(parts)
    
    if service not in services:
        services[service] = []
    services[service].append(img_path)

# Check each service
missing_images = []
large_images = []

for service, images in sorted(services.items()):
    print(f"\n{service.upper()}")
    print("-" * 40)
    
    for img_path in images:
        exists = os.path.exists(img_path)
        
        if exists:
            size_kb = os.path.getsize(img_path) / 1024
            status = "[OK]" if size_kb < 200 else "[LARGE]"
            print(f"  {status} {os.path.basename(img_path)} ({size_kb:.0f} KB)")
            
            if size_kb > 200:
                large_images.append((img_path, size_kb))
        else:
            print(f"  [MISSING] {os.path.basename(img_path)}")
            missing_images.append(img_path)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if missing_images:
    print(f"\n❌ MISSING IMAGES ({len(missing_images)}):")
    for img in missing_images:
        print(f"   - {img}")
else:
    print("\n✅ All images exist")

if large_images:
    print(f"\n⚠️ LARGE IMAGES > 200KB ({len(large_images)}):")
    for img, size in sorted(large_images, key=lambda x: -x[1]):
        print(f"   - {img} ({size:.0f} KB)")
else:
    print("\n✅ All images are optimized")

# Recommended sizes
print("\n" + "="*60)
print("RECOMMENDED IMAGE SPECS")
print("="*60)
print("Desktop: 600x400px (3:2 aspect ratio)")
print("Max file size: 100-150 KB (JPEG quality 80%)")
print("Format: WebP preferred, JPEG fallback")
print("Lazy loading: Yes (already implemented)")
