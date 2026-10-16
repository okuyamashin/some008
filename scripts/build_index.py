"""入口ページ（gamebook.engawa5656.com/）を書き出す。books/ 以下の全巻を書棚に並べる。

使い方:
    python3 scripts/build_index.py

site/index.html を型にして、books/*/story.toml から dist/index.html を作る。
表紙の画像は dist/assets/<slug_ja>.webp に置く（HTML 版と同じ WebP を使う）。
"""

import html
import re
import shutil
from string import Template

from books import ROOT, all_books
from build_html import QUALITY_COVER, curly, webp_path

TEMPLATE = ROOT / "site" / "index.html"
BLOCK = re.compile(r"[ \t]*<!-- 本ごとに繰り返す -->\n(?P<body>.*?)[ \t]*<!-- ここまで -->\n", re.S)


def main():
    books = all_books()
    page = TEMPLATE.read_text(encoding="utf-8")
    page = re.sub(r"\A(<!doctype html>\n)<!--.*?-->\n", r"\1", page, flags=re.S)  # 型の説明は書き出さない
    # 1 冊だけのときはその本の名前を、何冊もあるときは書棚全体の名前を、ページの名前にする
    single = html.escape(books[0].info["title"]) if len(books) == 1 else None
    page = Template(page).safe_substitute(
        page_title=f"{single} — ゲームブック" if single else "アドベンチャーゲームブック",
        og_title=single or "アドベンチャーゲームブック",
        og_cover=f"assets/{books[0].slug_ja}.webp",
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
            slug_ja=src.slug_ja,
            slug_en=src.slug_en,
            cover=cover,
        ))

    page = BLOCK.sub(lambda _: "\n".join(shelves), page, count=1)
    out = ROOT / "dist" / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} ({len(books)} 冊)")


if __name__ == "__main__":
    main()
