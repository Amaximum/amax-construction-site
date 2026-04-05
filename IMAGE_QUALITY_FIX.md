# Image Quality Guidelines & Fix Instructions

## Current Issues

20 images on the website have low quality (appear blurry):

### HIGH PRIORITY (affects 73+ pages):

| Image | Sharpness | Status |
|-------|-----------|--------|
| basement-1.jpg | 361 | LOW - needs replacement |
| basement-2.jpg | 499 | LOW - needs replacement |
| basement-3.jpg | 361 | LOW - needs replacement |
| basement-4.jpg | 426 | LOW - needs replacement |
| plumbing-1.jpg | 246 | LOW - replaced on plumbing hub |
| plumbing-2.jpg | 365 | LOW - replaced on plumbing hub |
| plumbing-3.jpg | 450 | LOW - replaced on plumbing hub |
| plumbing-4.jpg | 382 | LOW - replaced on plumbing hub |

### MEDIUM PRIORITY:

| Image | Sharpness | Status |
|-------|-----------|--------|
| handyman-2.jpg | 267 | LOW |
| contractor-4.jpg | 319 | LOW |
| carpentry-3.jpg | 413 | LOW |
| electrical-3.jpg | 360 | LOW |
| painting-2.jpg | 323 | LOW |

## How To Fix

### Option 1: Replace Source Images (RECOMMENDED)

1. Find high-quality photos (1600x1067px or larger)
2. Save them with the SAME filename (e.g., `basement-1.jpg`)
3. Put them in `img/services/` folder
4. Run: `python optimize_images.py` to ensure proper size/quality

This automatically fixes ALL pages using that image!

### Option 2: Use Existing Quality Images

For basement pages, you could use bathroom images temporarily:
- bathroom-2.jpg (sharpness: 664) 
- bathroom-3.jpg (sharpness: 586)
- bathroom-4.jpg (sharpness: 533)

But this changes the subject matter (bathrooms instead of basements).

## Quality Standards

All new images should meet these requirements:

| Property | Requirement |
|----------|-------------|
| Resolution | Minimum 1200x800px |
| File size | 100-200KB (JPEG) |
| Sharpness score | > 500 |
| Format | JPEG (RGB color mode) |
| Aspect ratio | 3:2 or 16:9 |

## Verification

Run these scripts to check image quality:

```bash
# Check all image quality
python check_image_quality.py

# Find blurry images
python find_blurry_images.py

# Check carousel quality
python check_carousel_quality.py
```

## Sources for Quality Images

- Unsplash.com (free, high quality)
- Pexels.com (free)
- Your own project photos (BEST option!)

## Sharpness Scale

| Score | Quality |
|-------|---------|
| < 300 | Very blurry (AI-generated or heavily compressed) |
| 300-500 | Soft/blurry |
| 500-1000 | Acceptable |
| 1000-2000 | Good |
| > 2000 | Excellent |
