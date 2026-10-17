"""入口ページ（gamebook.engawa5656.com/）を書き出す。books/ 以下の全巻を書棚に並べる。

使い方:
    python3 scripts/build_index.py

site/index.html を型にして、books/*/story.toml から dist/index.html を作る。
表紙の画像は dist/assets/<slug_ja>.webp に置く（HTML 版と同じ WebP を使う）。
あわせて、検索エンジン向けの dist/sitemap.xml と dist/robots.txt も書き出す。
サイトマップには入口ページと、各巻の日英のブラウザ版と PDF を載せる（EPUB は検索結果から開けないので載せない）。
"""

import html
import re
import shutil
from datetime import datetime, timezone
from string import Template

from books import ROOT, all_books
from build_html import QUALITY_COVER, curly, webp_path

TEMPLATE = ROOT / "site" / "index.html"
SITE = "https://gamebook.engawa5656.com"
BLOCK = re.compile(r"[ \t]*<!-- 本ごとに繰り返す -->\n(?P<body>.*?)[ \t]*<!-- ここまで -->\n", re.S)


def main():
    # 公開日の新しい順（同じ日の並びは問わない）
    books = sorted(all_books(), key=lambda b: b.info["published"], reverse=True)
    page = TEMPLATE.read_text(encoding="utf-8")
    page = re.sub(r"\A(<!doctype html>\n)<!--.*?-->\n", r"\1", page, flags=re.S)  # 型の説明は書き出さない
    # 1 冊だけのときはその本の名前を、何冊もあるときは書棚全体の名前を、ページの名前にする
    single = html.escape(books[0].info["title"]) if len(books) == 1 else None
    page = Template(page).safe_substitute(
        page_title=f"{single} — ゲームブック" if single else "アドベンチャーゲームブック",
        og_title=single or "アドベンチャーゲームブック",
    )
    block = Template(BLOCK.search(page).group("body"))

    assets = ROOT / "dist" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shelves = []
    for src in books:
        ja, en = src.info, src.story("en")["book"]
        cover = f"assets/{src.slug_ja}.webp"
        shutil.copyfile(webp_path(src, ja["cover_image"], QUALITY_COVER), ROOT / "dist" / cover)
        shelves.append(block.substitute(
            title=html.escape(ja["title"]),
            title_en=curly(html.escape(f"{en['title_main']} {en['title_sub']}", quote=False)),
            title_en_main=curly(html.escape(en["title_main"], quote=False)),
            lead=html.escape(ja["lead"]),
            published=ja["published"],
            published_ja=published_ja(ja["published"]),
            slug_ja=src.slug_ja,
            slug_en=src.slug_en,
            cover=cover,
        ))

    page = BLOCK.sub(lambda _: "\n".join(shelves), page, count=1)
    out = ROOT / "dist" / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} ({len(books)} 冊)")
    write_sitemap(books)


def published_ja(iso):
    """2026-10-17 → 2026年10月17日"""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{y}年{m}月{d}日"


def lastmod(path):
    """書き出したファイルの更新日（なければ今日）。"""
    t = path.stat().st_mtime if path.exists() else datetime.now().timestamp()
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")


def write_sitemap(books):
    dist = ROOT / "dist"
    entries = [f"""  <url>
    <loc>{SITE}/</loc>
    <lastmod>{lastmod(dist / "index.html")}</lastmod>
  </url>"""]
    for src in books:
        # 同じ本の日本語版と英語版を、互いの別言語版として示す（hreflang）
        alternates = "\n".join(
            f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{SITE}/library/{src.slug(lang)}.html"/>'
            for lang in ("ja", "en")
        )
        for lang in ("ja", "en"):
            name = src.slug(lang)
            entries.append(f"""  <url>
    <loc>{SITE}/library/{name}.html</loc>
    <lastmod>{lastmod(dist / f"{name}.html")}</lastmod>
{alternates}
  </url>""")
            entries.append(f"""  <url>
    <loc>{SITE}/library/{name}.pdf</loc>
    <lastmod>{lastmod(dist / f"{name}.pdf")}</lastmod>
  </url>""")
    sitemap = dist / "sitemap.xml"
    sitemap.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    (dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"{sitemap.relative_to(ROOT)} ({len(entries)} 件), dist/robots.txt")


if __name__ == "__main__":
    main()
