# Light & Love Books

Soft, multilingual static author site for Amazon KDP titles by **Light & Love (MW)**.

## Features

- Bookstore-feel homepage: hero, featured shelf, benefit cards, promo about
- Catalog of all titles from `data/books.json` with local cover images
- Category filters (client-side)
- Book detail modal with blurb, category, format, Amazon UK / US links
- Languages: English, 繁體中文, 简体中文, 日本語, 한국어
- Vanilla HTML / CSS / JS — no build step
- Soft paper/cream aesthetic; no fake reviews or star ratings

## Local preview

```bash
cd light-and-love-books
python3 -m http.server 8080
# open http://127.0.0.1:8080/
```

Opening `index.html` as a file may block `fetch` for JSON in some browsers; prefer a local server.

## Publish

- Netlify / Cloudflare Pages / GitHub Pages: publish this folder as the site root.
- Update absolute Open Graph URLs once you have a live domain.

## Data

- `data/books.json` — scraped metadata, categories, blurbs
- `data/categories.json` — category ids + counts
- `assets/covers/{ASIN}.jpg` — cover images
- `CATALOG.md` — ASIN / title / category summary
- `js/i18n.js` — UI strings and translated category labels / author bio

## Add a book later

1. Add cover to `assets/covers/{ASIN}.jpg`
2. Append an object to `data/books.json` (and bump `categories.json` counts)
3. Optionally add a short `blurb` in each language
