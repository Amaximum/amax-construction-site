from pathlib import Path
from PIL import Image

root = Path(r"c:\Users\maxim\Desktop\amax-Construction-site")
src = root / "services" / "aMaximum-Construction1-1 (2).png"
out = root / "img" / "logo.png"

img = Image.open(src).convert("RGBA")
px = img.load()
width, height = img.size

for y in range(height):
    for x in range(width):
        r, g, b, a = px[x, y]
        is_light = r > 220 and g > 220 and b > 220
        is_low_saturation = abs(r - g) < 14 and abs(g - b) < 14 and abs(r - b) < 14
        if is_light and is_low_saturation:
            px[x, y] = (r, g, b, 0)

bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

# small padding so crown top doesn't touch bounds
pad = 16
canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
canvas.paste(img, (pad, pad), img)

canvas.save(out)
print(f"Saved {out} size={canvas.size}")
