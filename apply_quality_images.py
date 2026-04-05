#!/usr/bin/env python3
"""
Apply quality image fixes across the website.
This script replaces low-quality images with high-quality alternatives.

Usage:
1. Put new quality images in img/services/new/ folder
2. Run this script
3. It will backup old images and apply new ones
"""

import shutil
from pathlib import Path
from PIL import Image
import numpy as np

def calculate_sharpness(img_path):
    """Calculate image sharpness."""
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

def optimize_and_save(src_path, dst_path, max_width=1600, max_height=1067, quality=85):
    """Optimize image and save to destination."""
    img = Image.open(src_path)
    
    # Convert to RGB
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if needed
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Save optimized
    img.save(dst_path, 'JPEG', quality=quality, optimize=True)
    
    return dst_path.stat().st_size // 1024

def main():
    img_dir = Path("img/services")
    new_dir = img_dir / "new"
    backup_dir = img_dir / "backup"
    
    # Create directories
    backup_dir.mkdir(exist_ok=True)
    
    if not new_dir.exists():
        print("=" * 60)
        print("IMAGE QUALITY FIX TOOL")
        print("=" * 60)
        print()
        print("To use this tool:")
        print("1. Create folder: img/services/new/")
        print("2. Put your quality images there (same names as originals)")
        print("3. Run this script again")
        print()
        print("Example: Put a quality 'basement-1.jpg' in img/services/new/")
        print("         It will replace the blurry one in img/services/")
        print()
        
        # Create the folder
        new_dir.mkdir(exist_ok=True)
        print(f"Created folder: {new_dir}")
        return
    
    # Find new images
    new_images = list(new_dir.glob("*.jpg")) + list(new_dir.glob("*.jpeg")) + list(new_dir.glob("*.png"))
    
    if not new_images:
        print("No new images found in img/services/new/")
        print("Add your quality images there and run again.")
        return
    
    print("=" * 60)
    print("APPLYING QUALITY IMAGES")
    print("=" * 60)
    print()
    
    for new_img in new_images:
        target_name = new_img.stem + ".jpg"
        target_path = img_dir / target_name
        backup_path = backup_dir / target_name
        
        # Check new image quality
        new_sharpness = calculate_sharpness(new_img)
        
        print(f"{new_img.name}:")
        print(f"  New image sharpness: {new_sharpness:.0f}")
        
        if new_sharpness < 500:
            print(f"  [WARN] New image quality is low! Sharpness should be > 500")
            response = input("  Apply anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("  Skipped.")
                continue
        
        # Backup original if exists
        if target_path.exists():
            old_sharpness = calculate_sharpness(target_path)
            print(f"  Old image sharpness: {old_sharpness:.0f}")
            
            if not backup_path.exists():
                shutil.copy2(target_path, backup_path)
                print(f"  Backed up to: {backup_path}")
        
        # Optimize and apply
        size_kb = optimize_and_save(new_img, target_path)
        print(f"  Applied! Size: {size_kb}KB")
        
        # Verify
        final_sharpness = calculate_sharpness(target_path)
        print(f"  Final sharpness: {final_sharpness:.0f}")
        
        if old_sharpness and final_sharpness > old_sharpness:
            improvement = ((final_sharpness - old_sharpness) / old_sharpness) * 100
            print(f"  Improvement: +{improvement:.0f}%")
        
        print()
    
    print("=" * 60)
    print("DONE!")
    print()
    print("Old images backed up to: img/services/backup/")
    print("Run 'python check_image_quality.py' to verify.")
    print("=" * 60)

if __name__ == "__main__":
    main()
