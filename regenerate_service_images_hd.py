from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def _center_crop_to_ratio(img: Image.Image, ratio: float) -> Image.Image:
    w, h = img.size
    if w <= 0 or h <= 0:
        return img

    current = w / h
    if abs(current - ratio) < 1e-6:
        return img

    if current > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def make_jpeg(src: Path, dst: Path, width: int, height: int, quality: int) -> None:
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    img = _center_crop_to_ratio(img, width / height)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate high-quality web JPEGs for a service from original photos."
    )
    ap.add_argument("--src", required=True, help="Folder with original photos (jpg/jpeg/png)")
    ap.add_argument(
        "--out-dir", default="img/services", help="Output directory for web images"
    )
    ap.add_argument(
        "--service",
        required=True,
        help="Service key prefix used in filenames (e.g. fence -> fence-1.jpg)",
    )
    ap.add_argument(
        "--outputs",
        default="",
        help=(
            "Comma-separated output filenames relative to --out-dir. "
            "If omitted, defaults to '<service>-1.jpg..-4.jpg' and '<service>-user-1.jpg'. "
            "Example: --outputs deck-1.jpg,deck-2.jpg,deck-3.jpg,deck-4.jpg,deck-user-1.jpg"
        ),
    )
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1067)
    ap.add_argument("--quality", type=int, default=84)

    args = ap.parse_args()

    src_dir = Path(args.src)
    out_dir = Path(args.out_dir)
    service = args.service.strip().lower()
    width = int(args.width)
    height = int(args.height)
    quality = int(args.quality)

    if not src_dir.exists() or not src_dir.is_dir():
        raise SystemExit(f"Source folder not found: {src_dir}")

    originals = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        originals.extend(src_dir.glob(ext))
    originals = sorted([p for p in originals if p.is_file()])
    if not originals:
        raise SystemExit(f"No images found in: {src_dir}")

    outputs = [o.strip() for o in str(args.outputs or "").split(",") if o.strip()]
    if outputs:
        targets = [out_dir / o for o in outputs]
    else:
        # Default: service-1..4 and service-user-1
        targets = [
            out_dir / f"{service}-1.jpg",
            out_dir / f"{service}-2.jpg",
            out_dir / f"{service}-3.jpg",
            out_dir / f"{service}-4.jpg",
            out_dir / f"{service}-user-1.jpg",
        ]

    # Use as many unique originals as available; repeat if fewer.
    picks = []
    for i in range(len(targets)):
        picks.append(originals[i % len(originals)])

    for src, dst in zip(picks, targets, strict=True):
        make_jpeg(src, dst, width=width, height=height, quality=quality)
        print(f"OK: {src} -> {dst} ({width}x{height}, q={quality})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
