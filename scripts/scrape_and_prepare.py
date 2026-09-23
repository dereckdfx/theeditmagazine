#!/usr/bin/env python3
"""Scrape tatler.com homepage + hubs for The Edit Magazine / Tatler English."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup

BASE = "https://www.tatler.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 40
ROOT = Path("/home/box/the-edit-tatler")
DATA = ROOT / "data"
RAW = DATA / "raw"
HISTORY = DATA / "history"
TODAY = datetime.now().strftime("%Y-%m-%d")
SCRAPED_AT = datetime.now().astimezone().isoformat(timespec="seconds")
FOLDER = f"the-edit-tatler/{TODAY}"
CLOUD = "dhx58lnzb"

HUBS = {
    "home": BASE + "/",
    "fashion": BASE + "/fashion",
    "beauty": BASE + "/topic/beauty",
    "royals": BASE + "/topic/royals",
    "bystander": BASE + "/bystander",
    "travel": BASE + "/topic/travel",
    "style": BASE + "/topic/style",
}

# Map hub -> site section slug used in HTML
SECTION_MAP = {
    "home": "home",
    "fashion": "fashion",
    "beauty": "beauty",
    "royals": "royals",
    "bystander": "society",
    "travel": "travel",
    "style": "fashion",
}

ARTICLE_RE = re.compile(r"^/(article|gallery)/[^?#]+", re.I)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9"})


def fetch(url: str, slug: str | None = None) -> BeautifulSoup:
    r = SESSION.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    RAW.mkdir(parents=True, exist_ok=True)
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", urlparse(url).path.strip("/")) or "home"
    (RAW / f"{slug}.html").write_bytes(r.content)
    return BeautifulSoup(r.content, "html.parser")


def normalize_image(url: str | None) -> str:
    if not url:
        return ""
    url = url.strip()
    if url.startswith("//"):
        url = "https:" + url
    if "," in url and "http" in url.split(",")[0]:
        parts = [p.strip().split(" ")[0] for p in url.split(",") if "http" in p]
        if parts:
            best, best_w = parts[0], 0
            for p in parts:
                m = re.search(r"w_(\d+)", p)
                w = int(m.group(1)) if m else 0
                if w >= best_w:
                    best_w, best = w, p
            url = best
    # Prefer w_1280
    url = re.sub(r"/(\d+:\d+)/w_\d+", r"/\1/w_1280", url)
    url = re.sub(r"/(\d+:\d+)/pass/", r"/\1/w_1280,c_limit/", url)
    if "/photos/" in url and "w_" not in url:
        url = re.sub(r"/(\d+:\d+)/", r"/\1/w_1280,c_limit/", url, count=1)
    return url


def pick_img(el) -> str:
    img = el.find("img") if el else None
    if not img:
        return ""
    candidates = []
    for attr in ("srcset", "data-srcset", "src", "data-src"):
        v = img.get(attr)
        if not v:
            continue
        if "srcset" in attr:
            candidates.extend(p.strip().split(" ")[0] for p in v.split(",") if p.strip())
        else:
            candidates.append(v)
    best, score = "", -1
    for c in candidates:
        c = c.strip()
        if not (c.startswith("http") or c.startswith("//")):
            continue
        s = 0
        if "media.tatler.com" in c or "assets" in c:
            s += 1000
        m = re.search(r"w_(\d+)", c)
        if m:
            s += int(m.group(1))
        if s > score:
            score, best = s, c
    return normalize_image(best)


def public_id_from_url(url: str) -> str:
    path = urlparse(url).path
    m = re.search(r"/photos/([a-f0-9]+)/", path)
    photo_id = m.group(1) if m else hashlib.sha1(url.encode()).hexdigest()[:12]
    name = unquote(unquote(path.split("/")[-1]))
    name = re.sub(r"\.(jpg|jpeg|png|webp|gif).*$", "", name, flags=re.I)
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name).strip("_")[:36]
    if not name or name.isdigit() or len(name) < 3:
        name = "img"
    return f"{FOLDER}/{photo_id}_{name}"


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    # article/foo-bar or gallery/foo
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[-1][:80]
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def extract_items(soup: BeautifulSoup, section: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Prefer summary-item cards (Condé Nast verso)
    cards = soup.select(".summary-item, [class*='SummaryItemWrapper']")
    if not cards:
        cards = []
        for a in soup.find_all("a", href=ARTICLE_RE):
            parent = a.find_parent(["article", "div", "li"])
            if parent and parent not in cards:
                cards.append(parent)

    for el in cards:
        a = el.find("a", href=ARTICLE_RE)
        if not a:
            continue
        href = urljoin(BASE, a.get("href", "")).split("?")[0].split("#")[0]
        if href in seen:
            continue
        # title
        hed = el.select_one(
            "[data-testid='SummaryItemHed'], [class*='SummaryItemHed'], "
            ".summary-item__hed, h2, h3, h1"
        )
        title = " ".join((hed.get_text(" ", strip=True) if hed else a.get_text(" ", strip=True)).split())
        # strip rubric prefix sometimes glued
        rubric_el = el.select_one(
            "[class*='SummaryItemRubric'], [class*='Rubric'], .summary-item__rubric"
        )
        category = " ".join(rubric_el.get_text(" ", strip=True).split()) if rubric_el else ""
        if category and title.lower().startswith(category.lower()):
            title = title[len(category) :].strip(" -–—|")
        title = re.sub(r"\s+By\s+.+$", "", title).strip()
        if len(title) < 12:
            continue
        img = pick_img(el)
        if not img:
            # try og later; skip for listing
            continue
        byline = ""
        byl = el.select_one("[class*='Byline'], [class*='byline'], [class*='SummaryItemByline']")
        if byl:
            byline = re.sub(r"^By\s+", "", " ".join(byl.get_text(" ", strip=True).split()), flags=re.I)

        seen.add(href)
        items.append(
            {
                "id": slug_from_url(href),
                "title": title,
                "url": href,
                "image": img,
                "category": category or section.replace("_", " ").title(),
                "section": SECTION_MAP.get(section, section),
                "hub": section,
                "author": byline or "Tatler Editors",
                "date": TODAY.replace("-", "."),
                "public_id": public_id_from_url(img),
                "slug": slug_from_url(href),
            }
        )
    return items


def enrich_article(article: dict) -> dict:
    """Fetch article page for dek + body paragraphs + better image."""
    try:
        soup = fetch(article["url"], slug=f"art-{article['slug'][:50]}")
    except Exception as e:
        article["excerpt"] = ""
        article["body"] = []
        article["fetch_error"] = str(e)
        return article

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        article["image"] = normalize_image(og["content"])
        article["public_id"] = public_id_from_url(article["image"])

    desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", property="og:description"
    )
    article["excerpt"] = (desc.get("content") if desc else "") or ""

    # author
    for sel in (
        '[rel="author"]',
        "[class*='BylineName']",
        "[class*='byline__name']",
        'a[href*="/author/"]',
        "[class*='Byline']",
    ):
        n = soup.select_one(sel)
        if n:
            t = " ".join(n.get_text(" ", strip=True).split())
            t = re.sub(r"^By\s+", "", t, flags=re.I)
            t = re.sub(r"\d{1,2}\s+\w+\s+\d{4}.*$", "", t).strip()
            if 2 < len(t) < 80:
                article["author"] = t
                break

    # body paragraphs
    paras: list[str] = []
    selectors = [
        "article .body__inner-container p",
        "[class*='ArticleBody'] p",
        "[class*='article__body'] p",
        "article p",
        ".content p",
    ]
    for sel in selectors:
        nodes = soup.select(sel)
        if len(nodes) >= 3:
            for p in nodes:
                t = " ".join(p.get_text(" ", strip=True).split())
                if len(t) < 40:
                    continue
                # skip newsletter CTAs etc
                low = t.lower()
                if any(x in low for x in ("subscribe", "newsletter", "sign up", "cookie", "privacy policy")):
                    continue
                paras.append(t)
            if paras:
                break
    article["body"] = paras[:12]
    if not article.get("excerpt") and paras:
        article["excerpt"] = paras[0][:240]
    time.sleep(0.25)
    return article


def assign_slots(home: list[dict], cats: dict[str, list]) -> dict:
    used: set[str] = set()
    pool = home[:]

    def take(n=1):
        out = []
        for a in pool:
            if a["url"] in used:
                continue
            used.add(a["url"])
            out.append(a)
            if len(out) >= n:
                break
        return out[0] if n == 1 and out else out

    hero = take(1)
    top = take(8)
    most_read = take(5)
    shop = take(4)

    def from_cat(key, n):
        out = []
        for a in cats.get(key, []):
            out.append(a)
            if len(out) >= n:
                break
        return out

    return {
        "hero": hero,
        "top_stories": top if isinstance(top, list) else [top],
        "most_read": most_read if isinstance(most_read, list) else [most_read],
        "shop_the_look": shop if isinstance(shop, list) else [shop],
        "fashion": from_cat("fashion", 8) or from_cat("style", 8),
        "beauty": from_cat("beauty", 8),
        "royals": from_cat("royals", 8),
        "society": from_cat("bystander", 8),
        "travel": from_cat("travel", 8),
        "latest": home[:16],
    }


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    HISTORY.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    # Rotate previous
    latest_path = DATA / "latest.json"
    prev_path = DATA / "previous.json"
    if latest_path.exists():
        shutil.copy(latest_path, prev_path)

    categories: dict[str, list] = {}
    home_items: list[dict] = []

    for key, url in HUBS.items():
        print(f"Fetching {key}: {url}")
        try:
            soup = fetch(url, slug=key)
            items = extract_items(soup, key)
            print(f"  -> {len(items)} items")
            if key == "home":
                home_items = items
            else:
                categories[key] = items
            time.sleep(0.35)
        except Exception as e:
            print(f"  ERROR {key}: {e}")
            if key != "home":
                categories[key] = []

    # Merge unique
    all_articles: list[dict] = []
    seen = set()
    for bucket in [home_items] + list(categories.values()):
        for a in bucket:
            if a["url"] in seen:
                continue
            seen.add(a["url"])
            all_articles.append(a)

    slots = assign_slots(home_items, categories)

    # Enrich featured articles (hero + top + most_read + first of each cat)
    to_enrich: list[dict] = []
    enrich_seen = set()

    def queue(a):
        if not a or a["url"] in enrich_seen:
            return
        enrich_seen.add(a["url"])
        to_enrich.append(a)

    if slots.get("hero"):
        queue(slots["hero"])
    for a in slots.get("top_stories", [])[:6]:
        queue(a)
    for a in slots.get("most_read", [])[:3]:
        queue(a)
    for key in ("fashion", "beauty", "royals", "society", "travel"):
        for a in (slots.get(key) or [])[:2]:
            queue(a)

    print(f"Enriching {len(to_enrich)} articles with body text...")
    enriched_by_url = {}
    for i, a in enumerate(to_enrich, 1):
        print(f"  [{i}/{len(to_enrich)}] {a['slug'][:50]}")
        enriched_by_url[a["url"]] = enrich_article(dict(a))

    def apply_enrich(obj):
        if isinstance(obj, dict) and "url" in obj and obj["url"] in enriched_by_url:
            return enriched_by_url[obj["url"]]
        return obj

    # Patch slots
    if slots.get("hero") and isinstance(slots["hero"], dict):
        slots["hero"] = apply_enrich(slots["hero"])
    for key in ("top_stories", "most_read", "shop_the_look", "fashion", "beauty", "royals", "society", "travel", "latest"):
        if key in slots and isinstance(slots[key], list):
            slots[key] = [apply_enrich(a) for a in slots[key]]

    # Update all_articles with enrichments
    for i, a in enumerate(all_articles):
        if a["url"] in enriched_by_url:
            all_articles[i] = enriched_by_url[a["url"]]

    # Images to upload
    upload_map: dict[str, dict] = {}

    def add_img(article):
        if not article or not article.get("image"):
            return
        pid = article["public_id"]
        upload_map[pid] = {
            "public_id": pid,
            "file": article["image"],
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "slug": article.get("slug", ""),
        }

    def walk(obj):
        if isinstance(obj, dict) and "image" in obj and "url" in obj:
            add_img(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(slots)
    for a in all_articles[:40]:
        add_img(a)

    images_to_upload = list(upload_map.values())

    payload = {
        "scraped_at": SCRAPED_AT,
        "source": BASE,
        "cloudinary_folder": FOLDER,
        "cloudinary_cloud": CLOUD,
        "slots": slots,
        "categories": {k: v[:12] for k, v in categories.items()},
        "home_all": home_items[:40],
        "articles": all_articles,
        "enriched": list(enriched_by_url.values()),
        "images_to_upload": images_to_upload,
        "images_uploaded": 0,
        "counts": {
            "home": len(home_items),
            "categories": {k: len(v) for k, v in categories.items()},
            "unique": len(all_articles),
            "enriched": len(enriched_by_url),
            "images": len(images_to_upload),
        },
    }

    latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (HISTORY / f"{stamp}.json").write_text(latest_path.read_text(encoding="utf-8"), encoding="utf-8")
    (DATA / "upload_list.json").write_text(
        json.dumps(images_to_upload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Wrote {latest_path}: {len(all_articles)} unique, "
        f"{len(enriched_by_url)} enriched, {len(images_to_upload)} images"
    )


if __name__ == "__main__":
    main()
