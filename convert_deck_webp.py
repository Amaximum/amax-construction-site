"""Convert deck-1..deck-4 and deck-user-1..deck-user-4 to WebP for the
Richmond Hill deck builder hero carousel. Keeps original JPGs for fallback."""
from PIL import Image
from pathlib import Path

src_dir = Path("img/services")
files = [
    "deck-1.jpg", "deck-2.jpg", "deck-3.jpg", "deck-4.jpg",
    "deck-user-1.jpg", "deck-user-2.jpg", "deck-user-3.jpg", "deck-user-4.jpg",
]
MAX_WIDTH = 1600  # cap to a reasonable hero width
QUALITY = 78

for name in files:
    src = src_dir / name
    if not src.exists():
        print(f"SKIP missing: {src}")
        continue
    dst = src.with_suffix(".webp")
    img = Image.open(src).convert("RGB")
    if img.width > MAX_WIDTH:
        new_h = int(img.height * (MAX_WIDTH / img.width))
        img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)
    img.save(dst, "WEBP", quality=QUALITY, method=6)
    src_kb = src.stat().st_size / 1024
    dst_kb = dst.stat().st_size / 1024
    print(f"{name}: {src_kb:.0f} KB -> {dst.name}: {dst_kb:.0f} KB ({img.width}x{img.height})")
