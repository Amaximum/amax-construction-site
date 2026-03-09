#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import os

source_dir = Path("services/Plumbing")
output_dir = Path("img/services")
output_dir.mkdir(parents=True, exist_ok=True)

# Image files to process
image_files = [
    "images.jpg",
    "images (1).jpg", 
    "images (2).jpg",
    "professional-kitchen-plumbing-installation.jpg",
    "what-type-of-work-can-a-handyman-do-legally_1000x.jpg",
    "Plumbing_Help.webp"
]

processed = 0
errors = 0

for idx, filename in enumerate(image_files, 1):
    input_path = source_dir / filename
    
    if not input_path.exists():
        print(f"❌ NOT FOUND: {filename}")
        continue
        
    try:
        # Open image
        img = Image.open(input_path)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = bg
        
        # Calculate smart crop to maintain 3:2 ratio
        w, h = img.size
        ratio = 3/2
        
        if w/h > ratio:
            # Too wide - crop width
            new_w = int(h * ratio)
            x = (w - new_w) // 2
            img = img.crop((x, 0, x + new_w, h))
        else:
            # Too tall - crop height
            new_h = int(w / ratio)
            y = (h - new_h) // 2
            img = img.crop((0, y, w, y + new_h))
        
        # Resize to 600x400
        img = img.resize((600, 400), Image.Resampling.LANCZOS)
        
        # Save as optimized JPEG
        output_name = f"plumbing-user-{idx}.jpg"
        output_path = output_dir / output_name
        img.save(output_path, "JPEG", quality=85, optimize=True)
        
        file_size_kb = output_path.stat().st_size / 1024
        print(f"✅ {idx}. {output_name} ({file_size_kb:.1f} KB)")
        processed += 1
        
    except Exception as e:
        print(f"❌ ERROR processing {filename}: {e}")
        errors += 1

print(f"\n✅ Processed: {processed} images")
if errors:
    print(f"❌ Errors: {errors}")
