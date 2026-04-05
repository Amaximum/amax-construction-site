#!/usr/bin/env python3
"""Optimize large images in img/services/ folder."""

from PIL import Image
import os
from pathlib import Path

# Target images that need optimization (>200KB)
LARGE_IMAGES = [
    "fence-user-1.jpg",
    "canopy-user-1.jpg", 
    "interlocking-user-1.jpg",
    "basement-1.jpg",
    "basement-2.jpg",
    "basement-3.jpg",
    "basement-4.jpg",
    "deck-user-1.jpg",
    "renovation-1.jpg",
    "renovation-3.jpg",
]

IMG_DIR = Path("img/services")
MAX_WIDTH = 600
MAX_HEIGHT = 400
QUALITY = 80

def optimize_image(filename):
    """Optimize a single image."""
    filepath = IMG_DIR / filename
    if not filepath.exists():
        print(f"  [SKIP] {filename} not found")
        return
    
    original_size = filepath.stat().st_size // 1024
    
    try:
        img = Image.open(filepath)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize if larger than target
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
        
        # Save with optimization
        img.save(filepath, 'JPEG', quality=QUALITY, optimize=True)
        
        new_size = filepath.stat().st_size // 1024
        savings = original_size - new_size
        
        print(f"  [OK] {filename}: {original_size}KB -> {new_size}KB (saved {savings}KB)")
    except Exception as e:
        print(f"  [ERROR] {filename}: {e}")

def main():
    print("=" * 60)
    print("OPTIMIZING LARGE IMAGES")
    print("=" * 60)
    print(f"Target: {MAX_WIDTH}x{MAX_HEIGHT}px, JPEG quality {QUALITY}%\n")
    
    total_saved = 0
    for filename in LARGE_IMAGES:
        filepath = IMG_DIR / filename
        if filepath.exists():
            original_size = filepath.stat().st_size // 1024
            optimize_image(filename)
            new_size = filepath.stat().st_size // 1024
            total_saved += (original_size - new_size)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL SAVED: {total_saved} KB")
    print("=" * 60)

if __name__ == "__main__":
    main()
