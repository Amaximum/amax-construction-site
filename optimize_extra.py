#!/usr/bin/env python3
"""Optimize remaining large images."""

from PIL import Image
import os
from pathlib import Path

EXTRA_IMAGES = [
    "fence-1.jpg",
    "fence-2.jpg", 
    "fence-3.jpg",
    "fence-4.jpg",
    "canopy-1.jpg",
    "canopy-2.jpg",
    "canopy-3.jpg",
    "canopy-4.jpg",
]

IMG_DIR = Path("img/services")
MAX_WIDTH = 600
MAX_HEIGHT = 400
QUALITY = 80

def optimize_image(filename):
    filepath = IMG_DIR / filename
    if not filepath.exists():
        print(f"  [SKIP] {filename} not found")
        return
    
    original_size = filepath.stat().st_size // 1024
    
    try:
        img = Image.open(filepath)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        img.save(filepath, 'JPEG', quality=QUALITY, optimize=True)
        
        new_size = filepath.stat().st_size // 1024
        savings = original_size - new_size
        print(f"  [OK] {filename}: {original_size}KB -> {new_size}KB (saved {savings}KB)")
        return savings
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")
        return 0

def main():
    print("Optimizing additional images...")
    total = 0
    for f in EXTRA_IMAGES:
        saved = optimize_image(f)
        if saved:
            total += saved
    print(f"\nTotal saved: {total} KB")

if __name__ == "__main__":
    main()
