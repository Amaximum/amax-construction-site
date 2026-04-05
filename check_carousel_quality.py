#!/usr/bin/env python3
"""
Fix all carousels on the website to use only high-quality images.
Replaces low-quality stock images with high-quality alternatives.
"""

import os
import re
from pathlib import Path
from PIL import Image
import numpy as np

# Quality threshold - images below this are considered low quality
QUALITY_THRESHOLD = 500

def calculate_sharpness(img_path):
    """Calculate image sharpness using Laplacian variance."""
    try:
        img = Image.open(img_path).convert('L')
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        arr = np.array(img, dtype=np.float64)
        
        h, w = arr.shape
        variance = 0
        for i in range(1, h-1):
            for j in range(1, w-1):
                lap = (arr[i-1,j] + arr[i+1,j] + arr[i,j-1] + arr[i,j+1] - 4*arr[i,j])
                variance += lap * lap
        
        return variance / ((h-2)*(w-2))
    except:
        return -1

def get_image_quality_map():
    """Build a map of all images and their quality."""
    img_dir = Path("img/services")
    quality_map = {}
    
    for img_path in img_dir.glob("*.jpg"):
        sharpness = calculate_sharpness(img_path)
        quality_map[img_path.name] = {
            'path': img_path,
            'sharpness': sharpness,
            'is_good': sharpness >= QUALITY_THRESHOLD
        }
    
    return quality_map

def get_good_images_by_service(quality_map):
    """Get list of good quality images grouped by service."""
    services = {}
    
    for name, info in quality_map.items():
        if not info['is_good']:
            continue
        
        # Extract service name
        base = name.replace('.jpg', '')
        # Remove -user suffix and numbers
        parts = re.split(r'-(?:user-?)?\d+$', base)
        service = parts[0] if parts else base
        
        if service not in services:
            services[service] = []
        services[service].append(name)
    
    return services

def find_replacement(bad_image, quality_map, good_by_service):
    """Find a good quality replacement for a bad image."""
    base = bad_image.replace('.jpg', '')
    parts = re.split(r'-(?:user-?)?\d+$', base)
    service = parts[0] if parts else base
    
    # First try to find good images from same service
    if service in good_by_service:
        return good_by_service[service][0]
    
    # Try related services
    related = {
        'plumbing': ['bathroom'],
        'bathroom': ['plumbing'],
        'basement': ['renovation'],
        'renovation': ['basement', 'bathroom'],
    }
    
    for related_service in related.get(service, []):
        if related_service in good_by_service:
            return good_by_service[related_service][0]
    
    return None

def scan_html_files():
    """Find all HTML files with carousels and their images."""
    results = []
    
    for html_path in Path('.').rglob('index.html'):
        if '__pycache__' in str(html_path):
            continue
            
        try:
            content = html_path.read_text(encoding='utf-8')
        except:
            continue
        
        # Find all img tags in carousels
        carousel_match = re.search(r'class="carousel".*?</div>\s*</div>', content, re.DOTALL)
        if not carousel_match:
            continue
        
        carousel_html = carousel_match.group(0)
        
        # Find all images
        img_matches = re.findall(r'<img\s+src="[^"]*(/img/services/([^"]+))"', carousel_html)
        
        if img_matches:
            results.append({
                'path': html_path,
                'images': [m[1] for m in img_matches]
            })
    
    return results

def main():
    print("=" * 70)
    print("CAROUSEL IMAGE QUALITY CHECKER")
    print("=" * 70)
    print()
    
    # Build quality map
    print("Analyzing image quality...")
    quality_map = get_image_quality_map()
    good_by_service = get_good_images_by_service(quality_map)
    
    print(f"Total images: {len(quality_map)}")
    print(f"Good quality: {sum(1 for v in quality_map.values() if v['is_good'])}")
    print(f"Low quality: {sum(1 for v in quality_map.values() if not v['is_good'])}")
    print()
    
    # Scan HTML files
    print("Scanning HTML files for carousels...")
    pages = scan_html_files()
    print(f"Found {len(pages)} pages with carousels")
    print()
    
    # Find pages with low quality images
    pages_with_issues = []
    for page in pages:
        bad_images = []
        for img in page['images']:
            if img in quality_map and not quality_map[img]['is_good']:
                bad_images.append(img)
        
        if bad_images:
            pages_with_issues.append({
                'path': page['path'],
                'bad_images': bad_images
            })
    
    print(f"Pages with low-quality carousel images: {len(pages_with_issues)}")
    print()
    
    for page in pages_with_issues[:20]:  # Show first 20
        print(f"\n{page['path']}:")
        for img in page['bad_images']:
            sharpness = quality_map[img]['sharpness']
            replacement = find_replacement(img, quality_map, good_by_service)
            repl_text = f" -> {replacement}" if replacement else " (no replacement found)"
            print(f"  LOW: {img} ({sharpness:.0f}){repl_text}")
    
    if len(pages_with_issues) > 20:
        print(f"\n... and {len(pages_with_issues) - 20} more pages")
    
    print()
    print("=" * 70)
    print("GOOD IMAGES BY SERVICE (use these as replacements):")
    print("=" * 70)
    for service, images in sorted(good_by_service.items()):
        print(f"  {service}: {', '.join(images[:3])}")

if __name__ == "__main__":
    main()
