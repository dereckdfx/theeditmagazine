#!/usr/bin/env python3
"""Build The Edit Magazine + Tatler English pages from scraped Tatler data."""
from __future__ import annotations

import html as H
import json
import re
from pathlib import Path

ROOT = Path("/home/box/the-edit-tatler")
REPO = Path("/workspace/theditrevista")
DATA = json.loads((ROOT / "data/latest.json").read_text(encoding="utf-8"))
CLOUD = DATA.get("cloudinary_cloud") or "dhx58lnzb"
FOLDER = DATA.get("cloudinary_folder") or "the-edit-tatler/2026-09-22"

SLOTS = DATA["slots"]
CATS = DATA.get("categories") or {}
ARTICLES = {a["slug"]: a for a in DATA.get("articles") or [] if a.get("slug")}
# Prefer enriched versions
for a in DATA.get("enriched") or []:
    ARTICLES[a["slug"]] = a


def esc(s: str) -> str:
    return H.escape(s or "", quote=True)


def cld(article: dict | None) -> str:
    if not article:
        return ""
    pid = article.get("public_id") or ""
    if pid:
        return f"https://res.cloudinary.com/{CLOUD}/image/upload/{pid}"
    return article.get("image") or ""


def brand_en(text: str) -> str:
    t = text or ""
    t = re.sub(r"(?i)\btatler\b", "Tatler", t)
    return t


def brand_es(text: str) -> str:
    """Light Spanish-facing brand: keep story titles, swap site name if present."""
    t = text or ""
    t = re.sub(r"(?i)\btatler\b", "Edit", t)
    return t


def save_btn(article: dict, *, lang: str = "es", href: str = "", extra: str = "") -> str:
    slug = article.get("slug") or ""
    title = article.get("title") or ""
    img = cld(article)
    url = href or (
        f"articles/{slug}.html" if lang == "es" else f"articles/{slug}.html"
    )
    tip = "GUARDAR ARTÍCULO" if lang.startswith("es") else "SAVE ARTICLE"
    return f'''<button type="button" class="save-btn relative group/save inline-flex items-center justify-center w-9 h-9 text-black hover:opacity-70 {extra}"
      data-save-article data-lang="{esc(lang)}" data-id="{esc(slug)}" data-title="{esc(title)}"
      data-url="{esc(url)}" data-image="{esc(img)}" data-category="{esc(article.get('category') or '')}"
      aria-label="{tip}" aria-pressed="false">
      <span data-save-icon><i class="fa-regular fa-bookmark"></i></span>
      <span data-save-tip class="pointer-events-none absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black text-white text-[9px] tracking-[0.15em] uppercase px-2 py-1 opacity-0 group-hover/save:opacity-100 transition">{tip}</span>
    </button>'''


PRIVACY_ES = '''
<div id="privacy-overlay" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/50">
  <div class="bg-white max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative">
    <div class="p-8 sm:p-12">
      <div class="mb-6 border-b border-black pb-4">
        <p class="font-serif text-3xl tracking-[0.25em] uppercase">The Edit</p>
      </div>
      <h2 class="text-2xl font-bold mb-6 font-jost">Tu invitación insider</h2>
      <div class="space-y-5 text-gray-800 text-sm leading-relaxed mb-8 font-serif">
        <p>Todo conocedor sabe que lo hecho a medida siempre es mejor. Edit utiliza tecnología para adaptar nuestras historias a tus intereses — de la alta sociedad a la moda y la realeza — y permite que socios publicitarios de lujo muestren anuncios alineados a tu estilo.</p>
        <p>Nosotros y nuestros <a href="#" class="underline font-medium">229</a> socios usamos cookies y métodos similares para reconocer visitantes y recordar preferencias. Algunas son esenciales; otras mejoran la experiencia. <a href="#" class="underline font-medium">Política de Privacidad</a></p>
        <p>Puedes retirar tu consentimiento o gestionar preferencias en cualquier momento con «Tus opciones de privacidad» en el pie de página. Tus preferencias aplican solo en este sitio.</p>
      </div>
      <div class="flex flex-col sm:flex-row justify-center items-center gap-3 mb-6">
        <button type="button" data-privacy-accept class="bg-black text-white px-8 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto">ACEPTO</button>
        <button type="button" data-privacy-accept class="bg-black text-white px-8 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto">RECHAZAR</button>
        <button type="button" data-privacy-accept class="bg-black text-white px-6 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto whitespace-nowrap">TUS OPCIONES DE PRIVACIDAD</button>
      </div>
      <div class="text-center"><a href="#" class="text-blue-700 underline text-sm font-serif">Política de Privacidad</a></div>
    </div>
  </div>
</div>
'''

PRIVACY_EN = '''
<div id="privacy-overlay" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/50">
  <div class="bg-white max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative">
    <div class="p-8 sm:p-12">
      <div class="mb-6 border-b border-black pb-4">
        <p class="font-tatler text-4xl tracking-[0.12em] uppercase">Tatler</p>
      </div>
      <h2 class="text-2xl font-bold mb-6 font-jost">Your insider invite</h2>
      <div class="space-y-5 text-gray-800 text-sm leading-relaxed mb-8 font-serif">
        <p>Every insider knows that bespoke is always better. Tatler uses technology to tailor stories to your interests — from royal whispers to high-society news — and allows trusted luxury advertising partners to show ads aligned to your style.</p>
        <p>We, and our <a href="#" class="underline font-medium">229</a> partners, use cookies and similar methods to recognise visitors and remember preferences. Some are essential; others improve the experience. <a href="#" class="underline font-medium">Privacy Policy</a></p>
        <p>You may withdraw consent or manage preferences anytime via Your Privacy Choices in the footer. Preferences apply only on this website.</p>
      </div>
      <div class="flex flex-col sm:flex-row justify-center items-center gap-3 mb-6">
        <button type="button" data-privacy-accept class="bg-black text-white px-8 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto">I AGREE</button>
        <button type="button" data-privacy-accept class="bg-black text-white px-8 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto">REJECT</button>
        <button type="button" data-privacy-accept class="bg-black text-white px-6 py-3 text-xs font-bold tracking-widest hover:bg-gray-800 transition w-full sm:w-auto whitespace-nowrap">YOUR PRIVACY CHOICES</button>
      </div>
      <div class="text-center"><a href="#" class="text-blue-700 underline text-sm font-serif">Privacy Policy</a></div>
    </div>
  </div>
</div>
'''


def edit_head(title: str, *, extra: str = "") -> str:
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{esc(title)}</title>
  <link rel="icon" type="image/png" href="https://res.cloudinary.com/dhx58lnzb/image/upload/v1785444730/faviconeditlogo_d9zdxq.png"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Jost:wght@300;400;500;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
    body {{ font-family: 'Jost', sans-serif; background:#fff; color:#0a0a0a; }}
    .font-serif {{ font-family: 'Playfair Display', 'Libre Baskerville', Georgia, serif; }}
    .font-jost {{ font-family: 'Jost', sans-serif; }}
    .save-btn.is-saved {{ color:#b91c1c; }}
  </style>
  {extra}
</head>
'''


def tatler_head(title: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{esc(title)}</title>
  <link rel="icon" type="image/png" href="https://res.cloudinary.com/dhx58lnzb/image/upload/v1785444730/faviconeditlogo_d9zdxq.png"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Jost:wght@300;400;500;600&family=Playfair+Display:wght@400;700&display=swap');
    body {{ font-family: 'Jost', sans-serif; background:#fff; color:#0a0a0a; }}
    .font-tatler {{ font-family: 'Cormorant Garamond', 'Playfair Display', Georgia, serif; font-weight: 600; }}
    .font-jost {{ font-family: 'Jost', sans-serif; }}
    .font-serif {{ font-family: 'Playfair Display', Georgia, serif; }}
    .save-btn.is-saved {{ color:#b91c1c; }}
  </style>
</head>
'''


def edit_header(active: str = "home", *, prefix: str = "") -> str:
    def nav(href, label, key):
        cls = "border-b border-black" if active == key else "hover:text-gray-500"
        return f'<li><a href="{prefix}{href}" class="{cls} transition">{label}</a></li>'

    return f'''
<header id="main-header" class="sticky top-0 bg-white w-full z-40 border-b border-neutral-200">
  <div class="w-full border-b border-gray-100 bg-gray-50">
    <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-2 flex flex-wrap items-center gap-x-5 gap-y-2 text-[10px] md:text-[11px] font-jost tracking-[0.18em] uppercase text-black">
      <span class="text-gray-500 font-medium">Más de Edit / Ediciones</span>
      <a href="{prefix}index.html" class="px-1 py-1 border-b-2 border-black font-semibold">Edit México / Latam</a>
      <a href="{prefix}tatler/index.html" class="px-1 py-1 hover:border-b border-transparent hover:border-black">Tatler English</a>
      <a href="{prefix}guardados.html" class="px-1 py-1 hover:border-b border-transparent hover:border-black">Guardados</a>
    </div>
  </div>
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-5 flex items-center justify-between">
    <button type="button" class="w-6 flex flex-col gap-[5px]" aria-label="Menú">
      <span class="block h-[1px] w-full bg-black"></span>
      <span class="block h-[1px] w-full bg-black"></span>
      <span class="block h-[1px] w-full bg-black"></span>
    </button>
    <a href="{prefix}index.html" class="text-center">
      <span class="block font-serif text-4xl md:text-5xl tracking-[0.28em] uppercase leading-none">The Edit</span>
      <span class="block font-jost text-[9px] tracking-[0.35em] uppercase mt-2 text-neutral-500">México y Latinoamérica</span>
    </a>
    <a href="{prefix}suscripcion.html" class="font-jost text-[11px] tracking-[0.2em] uppercase hover:opacity-60">Suscripción</a>
  </div>
  <nav class="border-t border-neutral-200">
    <ul class="max-w-screen-2xl mx-auto px-6 md:px-12 py-3 flex justify-center flex-wrap gap-x-7 gap-y-2 font-jost text-[11px] md:text-[12px] tracking-[0.18em] uppercase">
      {nav('moda.html','Moda','moda')}
      {nav('belleza.html','Belleza','belleza')}
      {nav('estilo-de-vida.html','Estilo de vida','estilo')}
      {nav('hollywood.html','Hollywood','hollywood')}
      {nav('tatler/index.html','Tatler','tatler')}
      {nav('guardados.html','Guardados','guardados')}
    </ul>
  </nav>
</header>
'''


def edit_footer(prefix: str = "") -> str:
    return f'''
<footer id="main-footer" class="bg-black text-white mt-auto">
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-14">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-10 mb-10">
      <div>
        <p class="font-serif text-3xl tracking-[0.25em] uppercase mb-4">The Edit</p>
        <p class="text-sm text-neutral-400">Moda, cultura y sociedad para México y Latinoamérica.</p>
      </div>
      <div>
        <h3 class="font-jost text-xs tracking-[0.25em] uppercase mb-4">Secciones</h3>
        <ul class="space-y-2 text-sm text-neutral-300">
          <li><a href="{prefix}moda.html" class="hover:text-white">Moda</a></li>
          <li><a href="{prefix}belleza.html" class="hover:text-white">Belleza</a></li>
          <li><a href="{prefix}tatler/index.html" class="hover:text-white">Tatler English</a></li>
          <li><a href="{prefix}guardados.html" class="hover:text-white">Guardados</a></li>
        </ul>
      </div>
      <div>
        <h3 class="font-jost text-xs tracking-[0.25em] uppercase mb-4">Legal</h3>
        <ul class="space-y-2 text-sm text-neutral-300">
          <li><a href="#" class="hover:text-white" data-privacy-accept>Tus opciones de privacidad</a></li>
          <li><a href="https://github.com/dereckdfx/theeditmagazine" class="hover:text-white" target="_blank" rel="noopener">GitHub</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-neutral-800 pt-6 text-xs text-neutral-500 flex flex-col md:flex-row justify-between gap-2">
      <p>© Edit — México y Latinoamérica</p>
      <p><a href="https://theditrevista.vercel.app" class="hover:text-white">theditrevista.vercel.app</a></p>
    </div>
  </div>
</footer>
<script src="{prefix}js/edit-app.js"></script>
'''


def tatler_header(active: str = "home", *, prefix: str = "") -> str:
    def nav(href, label, key):
        cls = "border-b border-black" if active == key else "hover:opacity-60"
        return f'<li><a href="{prefix}{href}" class="{cls} transition">{label}</a></li>'

    return f'''
<header class="sticky top-0 z-40 bg-white border-b border-black">
  <div class="w-full border-b border-neutral-200 bg-neutral-50">
    <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-2 flex flex-wrap items-center gap-x-5 gap-y-2 text-[10px] md:text-[11px] font-jost tracking-[0.18em] uppercase">
      <span class="text-neutral-500">More from Edit / Editions</span>
      <a href="{prefix}../index.html" class="hover:border-b border-transparent hover:border-black">Edit México / Latam</a>
      <a href="{prefix}index.html" class="border-b-2 border-black font-semibold">Tatler English</a>
      <a href="{prefix}../guardados.html" class="hover:border-b border-transparent hover:border-black">Saved</a>
    </div>
  </div>
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-5 flex items-center justify-between">
    <a href="{prefix}../index.html" class="font-jost text-[10px] tracking-[0.2em] uppercase text-neutral-500 hover:text-black">← Edit</a>
    <a href="{prefix}index.html" class="text-center">
      <span class="block font-tatler text-4xl md:text-5xl tracking-[0.08em] uppercase leading-none">Tatler</span>
      <span class="block font-jost text-[9px] tracking-[0.35em] uppercase mt-1 text-neutral-500">English Edition · via Edit</span>
    </a>
    <a href="{prefix}../subscribe.html" class="font-jost text-[10px] tracking-[0.2em] uppercase hover:opacity-60">Subscribe</a>
  </div>
  <nav class="border-t border-neutral-200">
    <ul class="max-w-screen-2xl mx-auto px-6 md:px-12 py-3 flex justify-center flex-wrap gap-x-8 gap-y-2 font-jost text-[11px] tracking-[0.2em] uppercase">
      {nav('fashion.html','Bystander' if False else 'Fashion','fashion')}
      {nav('beauty.html','Beauty','beauty')}
      {nav('royals.html','Royals','royals')}
      {nav('society.html','Society','society')}
      {nav('travel.html','Travel','travel')}
      {nav('lifestyle.html','Lifestyle','lifestyle')}
      {nav('culture.html','Culture','culture')}
    </ul>
  </nav>
</header>
'''


def tatler_footer(prefix: str = "") -> str:
    return f'''
<footer class="bg-black text-white mt-auto">
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 py-14">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-10 mb-10">
      <div>
        <p class="font-tatler text-3xl tracking-[0.1em] uppercase mb-4">Tatler</p>
        <p class="text-sm text-neutral-400">English society & luxury editorial within The Edit Magazine.</p>
      </div>
      <div>
        <h3 class="font-jost text-xs tracking-[0.25em] uppercase mb-4">Sections</h3>
        <ul class="space-y-2 text-sm text-neutral-300">
          <li><a href="{prefix}fashion.html" class="hover:text-white">Fashion</a></li>
          <li><a href="{prefix}royals.html" class="hover:text-white">Royals</a></li>
          <li><a href="{prefix}society.html" class="hover:text-white">Society</a></li>
          <li><a href="{prefix}travel.html" class="hover:text-white">Travel</a></li>
        </ul>
      </div>
      <div>
        <h3 class="font-jost text-xs tracking-[0.25em] uppercase mb-4">Editions</h3>
        <ul class="space-y-2 text-sm text-neutral-300">
          <li><a href="{prefix}../index.html" class="hover:text-white">Edit México / Latam</a></li>
          <li><a href="#" class="hover:text-white" data-privacy-accept>Your Privacy Choices</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-neutral-800 pt-6 text-xs text-neutral-500 flex flex-col md:flex-row justify-between gap-2">
      <p>Stories sourced from Tatler.com · updated daily</p>
      <p><a href="https://theditrevista.vercel.app/tatler/" class="hover:text-white">theditrevista.vercel.app/tatler/</a></p>
    </div>
  </div>
</footer>
<script src="{prefix}../js/edit-app.js"></script>
'''


def article_href(slug: str, *, where: str) -> str:
    """where: edit-home | edit-art | tatler-home | tatler-art | tatler-sec"""
    if where == "edit-home":
        return f"articles/{slug}.html"
    if where == "edit-art":
        return f"{slug}.html"
    if where == "tatler-home":
        return f"articles/{slug}.html"
    if where == "tatler-sec":
        return f"articles/{slug}.html"
    if where == "tatler-art":
        return f"{slug}.html"
    return f"articles/{slug}.html"


def card_html(a: dict, *, lang: str, href: str, large: bool = False) -> str:
    title = brand_es(a["title"]) if lang.startswith("es") else brand_en(a["title"])
    img = cld(a)
    cat = a.get("category") or ""
    img_cls = "aspect-[3/4]" if not large else "aspect-[16/10] md:aspect-[3/4]"
    return f'''
<a href="{esc(href)}" class="group block relative">
  <div class="{img_cls} overflow-hidden bg-neutral-100 mb-4">
    <img src="{esc(img)}" alt="" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy"/>
  </div>
  <div class="flex items-start justify-between gap-2">
    <div>
      <p class="font-jost text-[10px] tracking-[0.25em] uppercase text-neutral-500 mb-2">{esc(cat)}</p>
      <h3 class="font-serif text-xl md:text-2xl leading-snug group-hover:underline decoration-1 underline-offset-4">{esc(title)}</h3>
    </div>
    {save_btn(a, lang=lang, href=href)}
  </div>
</a>'''


def build_edit_index() -> str:
    hero = SLOTS.get("hero") or {}
    top = SLOTS.get("top_stories") or []
    most = SLOTS.get("most_read") or []
    shop = SLOTS.get("shop_the_look") or []
    latest = SLOTS.get("latest") or top

    hero_href = article_href(hero.get("slug", ""), where="edit-home")
    hero_img = cld(hero)
    hero_title = brand_es(hero.get("title", ""))

    most_html = ""
    for i, a in enumerate(most[:5], 1):
        href = article_href(a["slug"], where="edit-home")
        most_html += f'''
        <li class="flex gap-3 py-3 border-b border-neutral-200">
          <span class="font-serif text-2xl text-neutral-300 w-8">{i:02d}</span>
          <div class="flex-1">
            <a href="{esc(href)}" class="font-serif text-base leading-snug hover:underline">{esc(brand_es(a['title']))}</a>
            <p class="text-[10px] tracking-widest uppercase text-neutral-500 mt-1">{esc(a.get('category') or '')}</p>
          </div>
          {save_btn(a, lang='es', href=href, extra='flex-shrink-0')}
        </li>'''

    grid = "".join(
        card_html(a, lang="es", href=article_href(a["slug"], where="edit-home"))
        for a in (top + latest)[1:10]
        if a.get("slug") and a.get("slug") != hero.get("slug")
    )

    shop_html = "".join(
        card_html(a, lang="es", href=article_href(a["slug"], where="edit-home"))
        for a in shop[:4]
        if a.get("slug")
    )

    cover_img = cld(hero) or cld((top[0] if top else {}))

    return (
        edit_head("The Edit — México y Latinoamérica")
        + '<body class="flex flex-col min-h-screen bg-white text-black overflow-hidden">\n'
        + PRIVACY_ES
        + edit_header("home")
        + f'''
<main id="main-content" class="flex-grow">
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 pt-8 pb-20">

    <!-- Subscribe strip (no B4) -->
    <section class="w-full flex justify-center mb-10">
      <a href="suscripcion.html" class="max-w-[1200px] w-full flex items-center gap-6 py-3 group">
        <div class="w-[85px] h-[115px] flex-shrink-0 overflow-hidden border border-neutral-300 shadow-sm bg-neutral-100">
          <img src="{esc(cover_img)}" alt="Portada Edit" class="w-full h-full object-cover group-hover:scale-105 transition duration-500"/>
        </div>
        <p class="text-[18px] md:text-[20px] font-jost font-light tracking-wide">
          La portada de #EditAgosto ya está aquí: ¡Suscríbete y recíbela antes que todos!
        </p>
      </a>
    </section>

    <!-- Hero + Lo más leído -->
    <section class="grid lg:grid-cols-12 gap-10 mb-16">
      <article class="lg:col-span-8 relative">
        <a href="{esc(hero_href)}" class="block group">
          <div class="aspect-[16/10] md:aspect-[3/2] overflow-hidden bg-neutral-100 mb-5">
            <img src="{esc(hero_img)}" alt="" class="w-full h-full object-cover group-hover:scale-[1.02] transition duration-700"/>
          </div>
          <p class="font-jost text-[11px] tracking-[0.25em] uppercase text-neutral-500 mb-3">{esc(hero.get('category') or 'Portada')}</p>
          <h1 class="font-serif text-3xl md:text-5xl leading-tight group-hover:underline decoration-1 underline-offset-4">{esc(hero_title)}</h1>
          <p class="mt-4 text-neutral-600 max-w-2xl">{esc(brand_es(hero.get('excerpt') or '')[:220])}</p>
          <p class="mt-3 text-[11px] tracking-[0.2em] uppercase text-neutral-500">Por {esc(hero.get('author') or 'Edit')}</p>
        </a>
        <div class="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-full shadow">
          {save_btn(hero, lang='es', href=hero_href)}
        </div>
      </article>
      <aside class="lg:col-span-4">
        <div class="border-t border-b border-black py-3 mb-2">
          <h2 class="font-jost text-[12px] tracking-[0.3em] uppercase text-center">Lo más leído</h2>
        </div>
        <ol>{most_html}</ol>
      </aside>
    </section>

    <!-- Grid -->
    <section class="mb-16">
      <div class="flex items-center gap-4 mb-8">
        <div class="flex-1 h-px bg-neutral-300"></div>
        <h2 class="font-jost text-[12px] tracking-[0.3em] uppercase">Más historias</h2>
        <div class="flex-1 h-px bg-neutral-300"></div>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">{grid}</div>
    </section>

    <!-- Shop the look -->
    <section class="mb-8">
      <div class="flex items-center gap-4 mb-8">
        <div class="flex-1 h-px bg-neutral-300"></div>
        <h2 class="font-jost text-[12px] tracking-[0.3em] uppercase">Shop the look</h2>
        <div class="flex-1 h-px bg-neutral-300"></div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">{shop_html}</div>
    </section>

  </div>
</main>
'''
        + edit_footer()
        + "</body></html>\n"
    )


def build_article_page(a: dict, *, lang: str) -> str:
    is_es = lang.startswith("es")
    title = brand_es(a["title"]) if is_es else brand_en(a["title"])
    img = cld(a)
    body = a.get("body") or []
    if not body and a.get("excerpt"):
        body = [a["excerpt"]]
    if not body:
        body = [
            (f"Lee la historia completa en Tatler: {a.get('url')}" if not is_es
             else f"Lee la historia completa en la fuente original: {a.get('url')}")
        ]
    paras = "".join(f"<p class='mb-5 text-[17px] leading-8 text-neutral-800 font-serif'>{esc(p)}</p>" for p in body[:10])
    source = a.get("url") or ""
    by = a.get("author") or ("Edit" if is_es else "Tatler Editors")
    cat = a.get("category") or ""
    href_self = f"{a['slug']}.html"

    if is_es:
        head = edit_head(f"{title} | The Edit")
        chrome_h = edit_header("article", prefix="../")
        chrome_f = edit_footer(prefix="../")
        privacy = PRIVACY_ES
        back = '<a href="../index.html" class="font-jost text-[11px] tracking-[0.2em] uppercase text-neutral-500 hover:text-black">← The Edit</a>'
        byline = f"Por {esc(by)}"
        source_lbl = "Leer en Tatler.com →"
        save_lang = "es"
    else:
        head = tatler_head(f"{title} | Tatler English · Edit")
        chrome_h = tatler_header("article", prefix="../")
        chrome_f = tatler_footer(prefix="../")
        privacy = PRIVACY_EN
        back = '<a href="../index.html" class="font-jost text-[11px] tracking-[0.2em] uppercase text-neutral-500 hover:text-black">← Tatler</a>'
        byline = f"By {esc(by)}"
        source_lbl = "Read on Tatler.com →"
        save_lang = "en"

    return (
        head
        + '<body class="flex flex-col min-h-screen bg-white text-black overflow-hidden">\n'
        + privacy
        + chrome_h
        + f'''
<main id="main-content" class="flex-grow">
  <article class="max-w-3xl mx-auto px-6 md:px-12 pt-10 pb-20">
    <div class="flex items-center justify-between mb-8">{back}
      {save_btn(a, lang=save_lang, href=href_self if is_es else href_self)}
    </div>
    <p class="font-jost text-[11px] tracking-[0.25em] uppercase text-neutral-500 mb-4">{esc(cat)}</p>
    <h1 class="font-serif text-3xl md:text-5xl leading-tight mb-4">{esc(title)}</h1>
    <p class="font-jost text-[11px] tracking-[0.2em] uppercase text-neutral-500 mb-8">{byline}</p>
    <div class="aspect-[16/10] overflow-hidden bg-neutral-100 mb-10">
      <img src="{esc(img)}" alt="" class="w-full h-full object-cover"/>
    </div>
    <div class="article-body">{paras}</div>
    <p class="mt-10 pt-6 border-t border-neutral-200">
      <a href="{esc(source)}" target="_blank" rel="noopener" class="font-jost text-[11px] tracking-[0.2em] uppercase hover:underline">{source_lbl}</a>
    </p>
  </article>
</main>
'''
        + chrome_f
        + "</body></html>\n"
    )


def build_tatler_home() -> str:
    hero = SLOTS.get("hero") or {}
    top = SLOTS.get("top_stories") or []
    stories = [hero] + [a for a in top if a.get("slug") != hero.get("slug")]
    stories = [a for a in stories if a]

    # TOP STORIES layout: 1 large + 2 side
    lead = stories[0] if stories else {}
    side = stories[1:3]
    rest = stories[3:12]

    def top_card(a, *, tall=False):
        href = article_href(a["slug"], where="tatler-home")
        aspect = "aspect-[3/4]" if tall else "aspect-[16/10]"
        return f'''
        <a href="{esc(href)}" class="group block relative">
          <div class="{aspect} overflow-hidden bg-neutral-100 mb-3">
            <img src="{esc(cld(a))}" alt="" class="w-full h-full object-cover group-hover:scale-[1.03] transition duration-700"/>
            <span class="absolute bottom-3 left-3 bg-white/90 text-[9px] tracking-[0.2em] uppercase px-2 py-1">{esc(a.get('category') or '')}</span>
          </div>
          <div class="flex items-start justify-between gap-2">
            <h3 class="font-tatler text-xl md:text-2xl leading-snug group-hover:underline decoration-1 underline-offset-4">{esc(brand_en(a['title']))}</h3>
            {save_btn(a, lang='en', href=href)}
          </div>
        </a>'''

    side_html = "".join(top_card(a, tall=True) for a in side)
    rest_html = "".join(
        card_html(a, lang="en", href=article_href(a["slug"], where="tatler-home"))
        for a in rest
    )

    lead_href = article_href(lead.get("slug", ""), where="tatler-home")

    return (
        tatler_head("Tatler | English Edition · Edit Magazine")
        + '<body class="flex flex-col min-h-screen bg-white text-black overflow-hidden">\n'
        + PRIVACY_EN
        + tatler_header("home")
        + f'''
<main class="flex-grow">
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 pt-12 pb-20">
    <div class="flex items-center gap-4 mb-10">
      <div class="flex-1 h-px bg-neutral-300"></div>
      <h1 class="font-jost text-[12px] tracking-[0.35em] uppercase">Top Stories</h1>
      <div class="flex-1 h-px bg-neutral-300"></div>
    </div>

    <section class="grid md:grid-cols-12 gap-6 mb-16">
      <div class="md:col-span-7 relative">
        <a href="{esc(lead_href)}" class="group block">
          <div class="aspect-[16/10] overflow-hidden bg-neutral-100 mb-4">
            <img src="{esc(cld(lead))}" alt="" class="w-full h-full object-cover group-hover:scale-[1.02] transition duration-700"/>
          </div>
          <p class="font-jost text-[10px] tracking-[0.3em] uppercase text-neutral-500 mb-2">{esc(lead.get('category') or '')}</p>
          <h2 class="font-tatler text-3xl md:text-5xl leading-tight group-hover:underline decoration-1 underline-offset-4">{esc(brand_en(lead.get('title') or ''))}</h2>
        </a>
        <div class="absolute top-3 right-3 bg-white/90 rounded-full shadow">{save_btn(lead, lang='en', href=lead_href)}</div>
      </div>
      <div class="md:col-span-5 grid grid-cols-2 md:grid-cols-1 gap-6">{side_html}</div>
    </section>

    <section>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">{rest_html}</div>
    </section>
  </div>
</main>
'''
        + tatler_footer()
        + "</body></html>\n"
    )


def build_tatler_section(key: str, label: str, dek: str) -> str:
    # Map section keys to category buckets
    bucket_map = {
        "fashion": ["fashion", "style"],
        "beauty": ["beauty"],
        "royals": ["royals"],
        "society": ["bystander"],
        "travel": ["travel"],
        "lifestyle": ["travel", "bystander"],
        "culture": ["fashion", "style"],
    }
    items: list[dict] = []
    seen = set()
    for b in bucket_map.get(key, [key]):
        for a in CATS.get(b) or []:
            if a["url"] in seen:
                continue
            seen.add(a["url"])
            items.append(a)
    # fallback to slots
    if len(items) < 6:
        for a in (SLOTS.get(key) or SLOTS.get("latest") or []) :
            if a["url"] not in seen:
                seen.add(a["url"])
                items.append(a)

    lead = items[0] if items else {}
    rest = items[1:10]
    lead_href = article_href(lead.get("slug", "x"), where="tatler-sec") if lead else "#"
    rest_html = "".join(
        card_html(a, lang="en", href=article_href(a["slug"], where="tatler-sec"))
        for a in rest
        if a.get("slug")
    )

    lead_block = ""
    if lead:
        lead_block = f'''
        <a href="{esc(lead_href)}" class="block group mb-14 relative">
          <div class="grid md:grid-cols-2 gap-8 items-center">
            <div class="aspect-[3/4] md:aspect-[4/5] overflow-hidden bg-neutral-100">
              <img src="{esc(cld(lead))}" alt="" class="w-full h-full object-cover group-hover:scale-[1.03] transition duration-700"/>
            </div>
            <div>
              <p class="font-jost text-[10px] tracking-[0.3em] uppercase text-neutral-500 mb-4">Lead story</p>
              <h2 class="font-tatler text-3xl md:text-5xl leading-tight group-hover:underline decoration-1 underline-offset-4">{esc(brand_en(lead.get('title') or ''))}</h2>
              <p class="mt-6 text-neutral-600">{esc((lead.get('excerpt') or '')[:200])}</p>
              <div class="mt-6">{save_btn(lead, lang='en', href=lead_href)}</div>
            </div>
          </div>
        </a>'''

    return (
        tatler_head(f"{label} | Tatler English · Edit Magazine")
        + '<body class="flex flex-col min-h-screen bg-white text-black overflow-hidden">\n'
        + PRIVACY_EN
        + tatler_header(key)
        + f'''
<main class="flex-grow">
  <div class="max-w-screen-2xl mx-auto px-6 md:px-12 pt-12 pb-20">
    <header class="mb-12 text-center border-b border-black pb-10">
      <p class="font-jost text-[10px] tracking-[0.35em] uppercase text-neutral-500 mb-3">Tatler · English</p>
      <h1 class="font-tatler text-5xl md:text-7xl tracking-[0.06em] uppercase">{esc(label)}</h1>
      <p class="mt-4 max-w-xl mx-auto text-neutral-600">{esc(dek)}</p>
    </header>
    {lead_block}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">{rest_html}</div>
  </div>
</main>
'''
        + tatler_footer()
        + "</body></html>\n"
    )


def build_guardados() -> str:
    return (
        edit_head("Guardados | The Edit")
        + '<body class="flex flex-col min-h-screen bg-white text-black">\n'
        + PRIVACY_ES
        + edit_header("guardados")
        + '''
<main id="main-content" class="flex-grow">
  <div class="max-w-3xl mx-auto px-6 md:px-12 pt-12 pb-20">
    <h1 class="font-serif text-4xl md:text-5xl mb-2">Guardados</h1>
    <p class="text-neutral-600 mb-10">Artículos que marcaste con GUARDAR ARTÍCULO. Se guardan en este navegador.</p>
    <div id="saved-empty" class="hidden text-neutral-500 border border-dashed border-neutral-300 p-10 text-center">
      Aún no tienes artículos guardados.
    </div>
    <div id="saved-articles-list"></div>
  </div>
</main>
'''
        + edit_footer()
        + "</body></html>\n"
    )


def main():
    REPO.mkdir(parents=True, exist_ok=True)
    (REPO / "js").mkdir(exist_ok=True)
    (REPO / "articles").mkdir(exist_ok=True)
    (REPO / "tatler" / "articles").mkdir(parents=True, exist_ok=True)

    # Homepage
    (REPO / "index.html").write_text(build_edit_index(), encoding="utf-8")
    (REPO / "guardados.html").write_text(build_guardados(), encoding="utf-8")
    (REPO / "tatler" / "index.html").write_text(build_tatler_home(), encoding="utf-8")

    sections = [
        ("fashion", "Fashion", "Runway, front-row and the clothes that define high society."),
        ("beauty", "Beauty", "Grooming, wellness and the Tatler beauty edit."),
        ("royals", "Royals", "Courts, crowns and the modern monarchy."),
        ("society", "Society", "Bystander: parties, weddings and the season."),
        ("travel", "Travel", "Hotels, hideaways and high-society escapes."),
        ("lifestyle", "Lifestyle", "How the other half lives — and where they go."),
        ("culture", "Culture", "Arts, film and the stories shaping society."),
    ]
    for key, label, dek in sections:
        (REPO / "tatler" / f"{key}.html").write_text(
            build_tatler_section(key, label, dek), encoding="utf-8"
        )

    # Article pages: enriched + top slots
    to_write = {}
    for a in DATA.get("enriched") or []:
        to_write[a["slug"]] = a
    for key in ("hero",):
        a = SLOTS.get(key)
        if isinstance(a, dict) and a.get("slug"):
            to_write[a["slug"]] = a
    for key in ("top_stories", "most_read", "fashion", "beauty", "royals", "society", "travel"):
        for a in SLOTS.get(key) or []:
            if a.get("slug"):
                to_write.setdefault(a["slug"], a)
    for bucket in CATS.values():
        for a in (bucket or [])[:4]:
            if a.get("slug"):
                to_write.setdefault(a["slug"], a)

    edit_n = tatler_n = 0
    for slug, a in to_write.items():
        # Spanish Edit article
        (REPO / "articles" / f"{slug}.html").write_text(
            build_article_page(a, lang="es"), encoding="utf-8"
        )
        edit_n += 1
        # English Tatler article
        (REPO / "tatler" / "articles" / f"{slug}.html").write_text(
            build_article_page(a, lang="en"), encoding="utf-8"
        )
        tatler_n += 1

    # Ensure js is present (already written)
    print(f"Built index + tatler hub/sections")
    print(f"Edit articles: {edit_n}")
    print(f"Tatler articles: {tatler_n}")
    print(f"Unique article slugs: {len(to_write)}")


if __name__ == "__main__":
    main()
