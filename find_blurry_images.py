#!/usr/bin/env python3
"""
Find all low-quality images across the website.
Compares sharpness values to identify stock photos that need replacement.
"""

from pathlib import Path
from PIL import Image
import numpy as np

def calculate_sharpness(img_path):
    """Calculate image sharpness using Laplacian variance."""
    try:
        img = Image.open(img_path).convert('L')
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        arr = np.array(img, dtype=np.float64)
        
        h, w = arr.shape
        variance = 0
        count = 0
        for i in range(1, h-1):
            for j in range(1, w-1):
                lap = (arr[i-1,j] + arr[i+1,j] + arr[i,j-1] + arr[i,j+1] - 4*arr[i,j])
                variance += lap * lap
                count += 1
        
        return variance / count if count > 0 else 0
    except:
        return -1

def main():
    img_dir = Path("img/services")
    
    # Threshold: images below 500 sharpness are likely AI/stock and look blurry
    QUALITY_THRESHOLD = 500
    
    results = []
    for img_path in sorted(img_dir.glob("*.jpg")):
        sharpness = calculate_sharpness(img_path)
        size_kb = img_path.stat().st_size // 1024
        
        try:
            img = Image.open(img_path)
            dims = f"{img.width}x{img.height}"
        except:
            dims = "?"
        
        results.append({
            'path': img_path,
            'name': img_path.name,
            'dims': dims,
            'size_kb': size_kb,
            'sharpness': sharpness,
            'needs_replacement': sharpness < QUALITY_THRESHOLD
        })
    
    # Find low quality images
    low_quality = [r for r in results if r['needs_replacement']]
    
    print("=" * 70)
    print("LOW QUALITY IMAGES THAT NEED REPLACEMENT")
    print(f"Threshold: sharpness < {QUALITY_THRESHOLD}")
    print("=" * 70)
    print()
    
    if low_quality:
        # Group by service
        services = {}
        for r in low_quality:
            # Extract service name (e.g., "plumbing" from "plumbing-1.jpg")
            parts = r['name'].replace('.jpg', '').rsplit('-', 1)
            service = parts[0] if len(parts) > 1 else parts[0]
            # Remove numbers and "user" suffix
            service = service.rstrip('-0123456789').replace('-user', '')
            
            if service not in services:
                services[service] = []
            services[service].append(r)
        
        for service, images in sorted(services.items()):
            print(f"\n{service.upper()}:")
            for r in images:
                print(f"  {r['name']:<30} sharpness: {r['sharpness']:>6.0f}  {r['dims']}")
        
        print()
        print("=" * 70)
        print(f"TOTAL: {len(low_quality)} images need replacement")
        print("=" * 70)
        
        # Generate replacement suggestions
        print()
        print("SUGGESTED ACTIONS:")
        for service in sorted(services.keys()):
            user_imgs = list(img_dir.glob(f"{service}-user-*.jpg"))
            if user_imgs:
                print(f"  {service}: Replace with {service}-user-*.jpg files")
            else:
                print(f"  {service}: Need to source new quality images")
    else:
        print("All images are high quality!")
    
    # Also show distribution
    print()
    print("=" * 70)
    print("SHARPNESS DISTRIBUTION")
    print("=" * 70)
    
    ranges = [
        (0, 300, "Very Low (AI/stock)"),
        (300, 500, "Low"),
        (500, 1000, "Medium"),
        (1000, 2000, "Good"),
        (2000, float('inf'), "Excellent")
    ]
    
    for low, high, label in ranges:
        count = len([r for r in results if low <= r['sharpness'] < high])
        bar = "#" * count
        print(f"  {label:<20}: {count:>3} images {bar}")

if __name__ == "__main__":
    main()
