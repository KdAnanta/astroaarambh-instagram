# Astro Aarambh Instagram

Nightly Instagram Stories and Posts for **@astroaarambhstore**, built by Claude.

Every night at 12:00 AM IST a scheduled Claude task:
1. Reads the **Top picks** on https://astroaarambh.store/ (names, prices, MRP, ratings)
2. Picks 5 products for Stories and 1 for a feed Post, least recently used first
3. Renders them with the approved designs (`tools/render.py`), saved in `out/<date>/`
4. Publishes them to Instagram through Windsor.ai, with a caption and hashtags on the Post

## Adding a product photo
Upload the original photo to `photos/`, named with the product name as it appears on the website
(e.g. `Pyrite Peacock Frame for Prosperity and Protection.webp`). Photos are never edited.

## Files
- `photos/` original product photos
- `data/products.json` design text per product (headline, ribbon, benefit icons, hashtags)
- `data/history.json` what was posted on which night (keeps products from repeating)
- `data/latest.json` tonight's images and product details
