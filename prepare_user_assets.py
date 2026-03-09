from pathlib import Path
from PIL import Image

ROOT = Path(r"c:\Users\maxim\Desktop\amax-Construction-site")
SRC = ROOT / "services"
DST = ROOT / "img" / "services"
DST.mkdir(parents=True, exist_ok=True)

TARGET_W, TARGET_H = 600, 400
QUALITY = 86

mapping = {
    "Plastic Decking.jpg": "deck-user-1.jpg",
    "Composite.JPG": "deck-user-2.jpg",
    "A-Maximum (1).jpg": "deck-user-3.jpg",
    "A (2).jpg": "deck-user-4.jpg",
    "Photo from Max.jpg": "canopy-user-1.jpg",
    "Horizontal fence (8).JPG": "fence-user-1.jpg",
    "interlocking (6) (4).jpg": "interlocking-user-1.jpg",
    "interlocking (9) (1).jpg": "interlocking-user-2.jpg",
}

def process_image(src_path: Path, out_path: Path):
    img = Image.open(src_path)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    target_ratio = TARGET_W / TARGET_H
    current_ratio = img.width / img.height

    if current_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))

    img = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    img.save(out_path, "JPEG", quality=QUALITY, optimize=True)


for src_name, dst_name in mapping.items():
    source = SRC / src_name
    target = DST / dst_name
    process_image(source, target)
    print(f"OK: {src_name} -> {target.name}")

# copy exact provided logo without modification
logo_src = SRC / "aMaximum-Construction1-1 (2).png"
logo_dst = ROOT / "img" / "logo.png"
Image.open(logo_src).save(logo_dst)
print("OK: exact logo copied to img/logo.png")
