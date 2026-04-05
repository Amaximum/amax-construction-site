#!/usr/bin/env python3
"""
Download high-quality images from Unsplash to replace low-quality stock images.
This script downloads free-to-use images and replaces blurry ones.
"""

import urllib.request
import os
from pathlib import Path
from PIL import Image
import numpy as np
import time

# Unsplash Source API - free images (no API key needed)
# Format: https://source.unsplash.com/600x400/?keyword

REPLACEMENTS = {
    # basement images - search for basement renovation, finished basement
    'basement-1.jpg': 'basement+renovation',
    'basement-2.jpg': 'finished+basement',
    'basement-3.jpg': 'basement+remodel',
    'basement-4.jpg': 'basement+living+room',
    
    # plumbing images
    'plumbing-1.jpg': 'plumber+working',
    'plumbing-2.jpg': 'plumbing+repair',
    'plumbing-3.jpg': 'kitchen+sink+plumbing',
    'plumbing-4.jpg': 'bathroom+plumbing',
    
    # handyman
    'handyman-2.jpg': 'handyman+tools',
    
    # carpentry
    'carpentry-3.jpg': 'carpentry+woodwork',
    
    # contractor
    'contractor-4.jpg': 'construction+contractor',
    
    # electrical
    'electrical-3.jpg': 'electrician+work',
    
    # painting
    'painting-2.jpg': 'house+painting',
}

def download_image(keyword, output_path, size="1600x1067"):
    """Download image from Unsplash."""
    url = f"https://source.unsplash.com/{size}/?{keyword}"
    
    try:
        print(f"  Downloading: {keyword}...")
        
        # Create request with headers
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            
        # Save temporarily
        temp_path = output_path.with_suffix('.tmp')
        with open(temp_path, 'wb') as f:
            f.write(data)
        
        # Verify it's a valid image and optimize
        img = Image.open(temp_path)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize to standard size
        img.thumbnail((1600, 1067), Image.Resampling.LANCZOS)
        
        # Save with good quality
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        os.remove(temp_path)
        
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

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

def main():
    print("=" * 60)
    print("IMAGE QUALITY IMPROVEMENT TOOL")
    print("=" * 60)
    print()
    print("This will download high-quality images from Unsplash")
    print("to replace low-quality stock images.")
    print()
    
    img_dir = Path("img/services")
    backup_dir = Path("img/services/backup")
    backup_dir.mkdir(exist_ok=True)
    
    success = 0
    failed = 0
    
    for filename, keyword in REPLACEMENTS.items():
        filepath = img_dir / filename
        
        if not filepath.exists():
            print(f"[SKIP] {filename} - file not found")
            continue
        
        # Check current quality
        old_sharpness = calculate_sharpness(filepath)
        print(f"\n{filename} (current sharpness: {old_sharpness:.0f})")
        
        # Backup original
        backup_path = backup_dir / filename
        if not backup_path.exists():
            import shutil
            shutil.copy2(filepath, backup_path)
            print(f"  Backed up to {backup_path}")
        
        # Download new image
        if download_image(keyword, filepath):
            new_sharpness = calculate_sharpness(filepath)
            
            if new_sharpness > old_sharpness:
                print(f"  [OK] Improved: {old_sharpness:.0f} -> {new_sharpness:.0f}")
                success += 1
            else:
                print(f"  [?] New image sharpness: {new_sharpness:.0f}")
                # Still count as success if downloaded
                success += 1
        else:
            failed += 1
        
        # Rate limiting
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"DONE: {success} images updated, {failed} failed")
    print("=" * 60)
    print()
    print("Backups saved in: img/services/backup/")
    print("Run check_image_quality.py to verify improvements.")

if __name__ == "__main__":
    main()
