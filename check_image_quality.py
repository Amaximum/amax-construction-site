#!/usr/bin/env python3
"""
Analyze image quality across the entire website.
Detects blurry/low-quality images using Laplacian variance method.
"""

import os
from pathlib import Path
from PIL import Image
import numpy as np

def calculate_sharpness(img_path):
    """
    Calculate image sharpness using Laplacian variance.
    Higher value = sharper image, Lower value = blurry.
    Threshold: < 100 is likely blurry, > 300 is sharp.
    """
    try:
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        # Resize for consistent analysis
        img = img.resize((400, 300), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        arr = np.array(img, dtype=np.float64)
        
        # Laplacian kernel
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        
        # Apply convolution manually (simple version)
        h, w = arr.shape
        variance = 0
        count = 0
        for i in range(1, h-1):
            for j in range(1, w-1):
                lap = (arr[i-1,j] + arr[i+1,j] + arr[i,j-1] + arr[i,j+1] - 4*arr[i,j])
                variance += lap * lap
                count += 1
        
        return variance / count if count > 0 else 0
    except Exception as e:
        return -1

def get_compression_ratio(img_path):
    """
    Check file size vs pixel count.
    Lower ratio = more compressed = potentially lower quality.
    """
    try:
        img = Image.open(img_path)
        pixels = img.width * img.height
        file_size = img_path.stat().st_size
        # Bytes per pixel
        return (file_size / pixels) * 100
    except:
        return 0

def analyze_all_images():
    """Analyze all images in img/services folder."""
    img_dir = Path("img/services")
    
    results = []
    
    for img_path in sorted(img_dir.glob("*.jpg")):
        sharpness = calculate_sharpness(img_path)
        compression = get_compression_ratio(img_path)
        size_kb = img_path.stat().st_size // 1024
        
        try:
            img = Image.open(img_path)
            dims = f"{img.width}x{img.height}"
        except:
            dims = "?"
        
        # Determine quality
        if sharpness < 50:
            quality = "BLURRY"
        elif sharpness < 100:
            quality = "SOFT"
        elif sharpness < 200:
            quality = "OK"
        else:
            quality = "SHARP"
        
        results.append({
            'name': img_path.name,
            'dims': dims,
            'size_kb': size_kb,
            'sharpness': sharpness,
            'compression': compression,
            'quality': quality
        })
    
    return results

def main():
    print("=" * 80)
    print("IMAGE QUALITY ANALYSIS - ALL SERVICE IMAGES")
    print("=" * 80)
    print()
    
    results = analyze_all_images()
    
    # Group by quality
    blurry = [r for r in results if r['quality'] == 'BLURRY']
    soft = [r for r in results if r['quality'] == 'SOFT']
    ok = [r for r in results if r['quality'] == 'OK']
    sharp = [r for r in results if r['quality'] == 'SHARP']
    
    print(f"{'Image':<35} {'Dims':<12} {'Size':<8} {'Sharpness':<12} {'Quality'}")
    print("-" * 80)
    
    for r in results:
        quality_icon = {
            'BLURRY': '[!!!]',
            'SOFT': '[!]  ',
            'OK': '[OK] ',
            'SHARP': '[+++]'
        }.get(r['quality'], '     ')
        
        print(f"{r['name']:<35} {r['dims']:<12} {r['size_kb']:>5}KB  {r['sharpness']:>8.0f}    {quality_icon} {r['quality']}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total images: {len(results)}")
    print(f"SHARP (>200):  {len(sharp)} images")
    print(f"OK (100-200):  {len(ok)} images")
    print(f"SOFT (50-100): {len(soft)} images")  
    print(f"BLURRY (<50):  {len(blurry)} images")
    
    if blurry:
        print()
        print("!!! BLURRY IMAGES NEED REPLACEMENT:")
        for r in blurry:
            print(f"   - {r['name']}")
    
    if soft:
        print()
        print("! SOFT IMAGES (consider replacing):")
        for r in soft:
            print(f"   - {r['name']}")

if __name__ == "__main__":
    main()
