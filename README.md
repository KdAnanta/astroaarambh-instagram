# Astro Aarambh Instagram

Nightly Instagram Stories and Posts for **@astroaarambhstore**, built by Claude.

Every night at 12:00 AM IST a scheduled Claude task:
1. Reads the **Top picks** on https://astroaarambh.store/ (names, prices, MRP, ratings)
2. Picks 5 products for Stories and 1 for a feed Post, least recently used first
3. Renders them with the approved designs (`tools/render.py`), saved in `out/<date>/`
4. Publishes them to Instagram through Windsor.ai, with a caption and hashtags on the Post

## Ready-made post designs (feed posts)
Upload finished post images to `posts/`. Each needs a line in `data/post_images.json`
(product name, link, price); the nightly run looks at any new image, matches it to its product
and adds that line itself. One is posted every night, exactly as uploaded, rotating so none
repeats until all have been posted.

## Ready-made Stories (`stories/`)
Upload finished Story images to `stories/` (best size 1080 x 1920, PNG/JPG/WEBP). Each night up to
5 of them are posted exactly as uploaded, in file-name order (start names with 01, 02, 03... to
control the order). Each one is posted once. If fewer than 5 are waiting, the rest of the night's
Stories are made from the Top Picks as before.

## Adding a product photo (Stories)
Upload the original photo to `photos/`, named with the product name as it appears on the website
(e.g. `Pyrite Peacock Frame for Prosperity and Protection.webp`). Photos are never edited.

## Files
- `photos/` original product photos
- `posts/` ready-made feed post designs
- `stories/` ready-made Story designs
- `data/products.json` design text per product (headline, ribbon, benefit icons, hashtags)
- `data/history.json` what was posted on which night (keeps products from repeating)
- `data/latest.json` tonight's images and product details
