"""本ごとの素材（books/<名前>/）の場所と、各スクリプトに共通する --book の扱い。

books/<名前>/
    story.toml      日本語版の本文。[book] に書名・著者・書き出す名前（slug_ja / slug_en）など
    story.en.toml   英語版の本文
    prompts.md      挿絵のプロンプト集
    images/raw/     生成した挿絵の元画像（git には入れない）
"""

import argparse
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "books"


class Book:
    def __init__(self, name):
        self.name = name
        self.dir = BOOKS_DIR / name
        if not (self.dir / "story.toml").exists():
            raise SystemExit(f"本がありません: {(self.dir / 'story.toml').relative_to(ROOT)}")
        self.story_path = self.dir / "story.toml"
        self.story_en_path = self.dir / "story.en.toml"
        self.prompts_path = self.dir / "prompts.md"
        self.raw_dir = self.dir / "images" / "raw"
        self.cache_dir = ROOT / "build" / "images" / name
        self.info = tomllib.loads(self.story_path.read_text(encoding="utf-8"))["book"]
        self.slug_ja = self.info["slug_ja"]
        self.slug_en = self.info["slug_en"]
        if not (self.slug_ja and self.slug_en):
            raise SystemExit(f"{self.story_path.relative_to(ROOT)} の slug_ja と slug_en を埋めてください")

    def story(self, lang):
        path = self.story_path if lang == "ja" else self.story_en_path
        return tomllib.loads(path.read_text(encoding="utf-8"))

    def slug(self, lang):
        return self.slug_ja if lang == "ja" else self.slug_en


def all_books():
    return [Book(p.parent.name) for p in sorted(BOOKS_DIR.glob("*/story.toml"))]


def parse_args(description, langs=True):
    """--book <名前>（省略時は books/ 以下の全巻）と、ja / en の指定（省略時は両方）を読む。"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--book", action="append", metavar="名前", help="books/ の下の本の名前。複数回指定できる。省略時は全巻")
    if langs:
        parser.add_argument("langs", nargs="*", metavar="ja|en", help="版。省略時は両方")
    args = parser.parse_args()
    args.books = [Book(n) for n in args.book] if args.book else all_books()
    if langs:
        if bad := [x for x in args.langs if x not in ("ja", "en")]:
            parser.error(f"版は ja か en です: {' '.join(bad)}")
        args.langs = args.langs or ["ja", "en"]
    return args


if __name__ == "__main__":
    # scripts/deploy.sh 用。版ごとに「言語<TAB>英数字の名前<TAB>書名」を 1 行ずつ書き出す。
    from build_html import curly

    for book in parse_args("版の一覧を書き出す", langs=False).books:
        en = book.story("en")["book"]
        print(f"ja\t{book.slug_ja}\t{book.info['title']}")
        print(f"en\t{book.slug_en}\t{curly(en['title_main'] + ' ' + en['title_sub'])}")
