# The Edit / Tatler scrape pipeline

Mirrors the Devon (Vogue.mx / Korea / USA) pattern for **Tatler.com → The Edit Magazine**.

## Layout
- `scrape_and_prepare.py` — scrape homepage + hubs, enrich articles, write `data/latest.json`
- `build_site.py` — regenerate Edit + Tatler HTML into `dereckdfx/theeditmagazine`
- `data/latest.json` / `data/previous.json` — change detection
- `data/history/` — timestamped snapshots
- `data/raw/` — raw HTML dumps
- Cloudinary folder: `the-edit-tatler/YYYY-MM-DD` on cloud `dhx58lnzb`

## Hubs scraped
home, fashion, beauty, royals, bystander, travel, style

## Daily run (cron — parent wires schedule)
```bash
/home/box/vogue-mx/venv/bin/python3 /home/box/the-edit-tatler/scrape_and_prepare.py
# upload new images via Cloudinary MCP upload-asset (or sign-upload + curl)
/home/box/vogue-mx/venv/bin/python3 /home/box/the-edit-tatler/build_site.py
cd /workspace/theditrevista && git add -A && git commit -m "Daily Tatler sync" && git push origin main
```

## Site features
- GUARDAR ARTÍCULO / SAVE ARTICLE → `localStorage.editSavedArticles`
- Privacy consent → `localStorage.privacyAccepted`
- On-site article pages under `articles/` and `tatler/articles/`
