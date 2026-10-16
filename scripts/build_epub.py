"""EPUB 版を書き出す。日本語版は縦書き・右綴じ、英語版は横書き・左綴じ。

使い方:
    build/.venv/bin/python scripts/build_pdf.py     # 先に（表紙画像を PDF 用の印刷ページから作るため）
    python3 scripts/build_epub.py                   # 日本語版と英語版の両方
    python3 scripts/build_epub.py ja                # dist/ryu-no-meikyu.epub
    python3 scripts/build_epub.py en                # dist/dragons-labyrinth.epub

本の中身:
    表紙 → 扉 → 遊び方 → パラグラフ 1〜15。各パラグラフは「挿絵のページ → 本文のページ」。
    選択肢のリンクは、行き先のパラグラフの挿絵のページへ飛ぶ。

Kindle で読むときは、EPUB を「Send to Kindle」で送る（Kindle 側で変換される）。
"""

import html
import subprocess
import sys
import tomllib
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_html import CACHE_DIR, FONT_DIR, RAW_DIR, ROOT, STORY, STORY_EN, curly, en_paragraphs, paragraphs  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GRAY_PROFILE = "/System/Library/ColorSync/Profiles/Generic Gray Gamma 2.2 Profile.icc"
IMAGE_WIDTH = 900


def illustration(name):
    """挿絵をグレースケールの JPEG にする（電子書籍リーダーはどれも JPEG を表示できる）。"""
    src = RAW_DIR / f"{name}.png"
    if not src.exists():
        sys.exit(f"画像がありません: {src.relative_to(ROOT)}")
    dst = CACHE_DIR / f"{name}.epub.jpg"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "--resampleWidth", str(IMAGE_WIDTH),
             "-m", GRAY_PROFILE, str(src), "--out", str(dst)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    return dst.read_bytes()


def cover_image(edition):
    """タイトル入りの表紙。PDF 用の印刷ページの 1 ページ目（表紙）を Chrome で撮影して JPEG にする。"""
    print_html = ROOT / "dist" / f"{edition}.print.html"
    if not print_html.exists():
        sys.exit(f"{print_html.relative_to(ROOT)} がありません。先に build/.venv/bin/python scripts/build_pdf.py を実行してください")
    png = CACHE_DIR / f"{edition}.cover.png"
    jpg = CACHE_DIR / f"{edition}.cover.jpg"
    if not jpg.exists() or jpg.stat().st_mtime < print_html.stat().st_mtime:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # A6 の 105mm × 148mm は CSS で約 397 × 559 px。2.6 倍で撮って約 1030 × 1450 px にする
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=397,559",
             "--force-device-scale-factor=2.6", f"--screenshot={png}", print_html.as_uri()],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80", str(png), "--out", str(jpg)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return jpg.read_bytes()


def xhtml(lang, title, body, body_class=""):
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}"{cls}>
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body{cls}>
{body}
</body>
</html>
"""


class Book:
    def __init__(self, edition, lang, rtl, title, author, css, author_alt, author_file_as):
        self.edition, self.lang, self.rtl, self.title, self.author, self.css = edition, lang, rtl, title, author, css
        self.author_alt = author_alt          # (言語, 別の表記)。もう一方の言語での著者名
        self.author_file_as = author_file_as  # 並べ替え用の読み
        self.docs = []      # (id, href, content, properties)
        self.media = []     # (id, href, media_type, bytes, properties)

    def doc(self, ident, body, body_class="", properties=""):
        self.docs.append((ident, f"{ident}.xhtml", xhtml(self.lang, self.title, body, body_class), properties))

    def image_page(self, ident, image_id, data):
        self.media.append((image_id, f"images/{image_id}.jpg", "image/jpeg", data, ""))
        self.doc(ident, f'<div class="illust"><img src="images/{image_id}.jpg" alt=""/></div>', "image-page")

    def write(self, nav_items, start_href):
        out = ROOT / "dist" / f"{self.edition}.epub"
        out.parent.mkdir(parents=True, exist_ok=True)
        book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, f'https://gamebook.engawa5656.com/library/{self.edition}.epub')}"
        modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                    '<item id="css" href="style.css" media-type="text/css"/>']
        for ident, href, _, props in self.docs:
            p = f' properties="{props}"' if props else ""
            manifest.append(f'<item id="{ident}" href="{href}" media-type="application/xhtml+xml"{p}/>')
        for ident, href, mtype, _, props in self.media:
            p = f' properties="{props}"' if props else ""
            manifest.append(f'<item id="{ident}" href="{href}" media-type="{mtype}"{p}/>')
        spine = "\n    ".join(f'<itemref idref="{ident}"/>' for ident, *_ in self.docs)
        direction = ' page-progression-direction="rtl"' if self.rtl else ' page-progression-direction="ltr"'
        kindle_vertical = '\n    <meta name="primary-writing-mode" content="vertical-rl"/>' if self.rtl else ""

        opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{self.lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{book_id}</dc:identifier>
    <dc:title>{html.escape(self.title, quote=False)}</dc:title>
    <dc:creator id="creator">{html.escape(self.author, quote=False)}</dc:creator>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>
    <meta refines="#creator" property="file-as">{html.escape(self.author_file_as, quote=False)}</meta>
    <meta refines="#creator" property="alternate-script" xml:lang="{self.author_alt[0]}">{html.escape(self.author_alt[1], quote=False)}</meta>
    <dc:language>{self.lang}</dc:language>
    <dc:rights>© 2026 {html.escape(self.author, quote=False)}</dc:rights>
    <meta property="dcterms:modified">{modified}</meta>
    <meta property="rendition:layout">reflowable</meta>
    <meta name="cover" content="cover-image"/>{kindle_vertical}
  </metadata>
  <manifest>
    {chr(10).join("    " + m for m in manifest).strip()}
  </manifest>
  <spine{direction}>
    {spine}
  </spine>
  <guide>
    <reference type="cover" title="Cover" href="cover.xhtml"/>
    <reference type="text" title="Start" href="{start_href}"/>
  </guide>
</package>
"""
        toc = "\n".join(f'<li><a href="{href}">{html.escape(label)}</a></li>' for label, href in nav_items)
        nav_label = "目次" if self.lang == "ja" else "Contents"
        nav = xhtml(self.lang, self.title, f"""<nav epub:type="toc" id="toc"><h1>{nav_label}</h1><ol>
{toc}
</ol></nav>
<nav epub:type="landmarks" hidden=""><ol>
<li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
<li><a epub:type="bodymatter" href="{start_href}">Start</a></li>
</ol></nav>""")
        container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
        with zipfile.ZipFile(out, "w") as z:
            # mimetype は先頭・無圧縮でなければならない
            z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            deflate = {"compress_type": zipfile.ZIP_DEFLATED}
            z.writestr("META-INF/container.xml", container, **deflate)
            z.writestr("OEBPS/content.opf", opf, **deflate)
            z.writestr("OEBPS/nav.xhtml", nav, **deflate)
            z.writestr("OEBPS/style.css", self.css, **deflate)
            for _, href, content, _ in self.docs:
                z.writestr(f"OEBPS/{href}", content, **deflate)
            for _, href, _, data, _ in self.media:
                z.writestr(f"OEBPS/{href}", data, **deflate)
        print(f"{out.relative_to(ROOT)} ({out.stat().st_size / 1024 / 1024:.1f} MB)")
        return out


# ---------------------------------------------------------------------------
# 日本語版
# ---------------------------------------------------------------------------


def ja_tcy(n):
    return f'<span class="tcy">{n}</span>'


def ja_link(label, href, number=None):
    to = f'<span class="to">{ja_tcy(number)}へ</span>' if number else ""
    return f'<p class="choice"><a href="{href}">◆{html.escape(label)}</a>{to}</p>'


def build_ja():
    story = tomllib.loads(STORY.read_text(encoding="utf-8"))
    b = story["book"]
    book = Book("ryu-no-meikyu", "ja", True, b["title"], b["author"], CSS_JA, ("en", "Shin Okuyama"), "オクヤマ シン")

    book.media.append(("cover-image", "images/cover.jpg", "image/jpeg", cover_image("ryu-no-meikyu"), "cover-image"))
    book.doc("cover", '<div class="illust"><img src="images/cover.jpg" alt="表紙"/></div>', "image-page")
    title, subtitle, author, year = (html.escape(b[k]) for k in ("title", "subtitle", "author", "year"))
    book.doc("title", f"""<div class="tobira">
<p class="tobira-sub">{subtitle}</p>
<h1>{title}</h1>
<p class="tobira-author">{author}　作</p>
<p class="colophon">© {year}　{author}</p>
</div>""")
    book.doc("howto", f"""<h2>この本の遊び方</h2>
{paragraphs(b["how_to_play"])}
<div class="choices">{ja_link("冒険を始める", "p1.xhtml", 1)}</div>""")

    for p in sorted(story["paragraph"], key=lambda p: p["number"]):
        n, kind = p["number"], p["kind"]
        tail = ""
        if kind in ("choice", "result"):
            links = [ja_link(c["label"], f"p{c['to']}.xhtml", c["to"]) for c in p["choices"]]
        elif kind == "bad":
            tail = '<p class="end">——おしまい</p>'
            links = [ja_link("気を取り直して、やり直す", f"p{p['back']}.xhtml", p["back"])]
        else:
            tail = '<p class="end">——めでたし、めでたし</p>'
            links = [ja_link("最初から読む", "cover.xhtml")]
        book.image_page(f"p{n}", f"img{n}", illustration(p["image"]))
        body_class = "bad" if kind == "bad" else ""
        book.doc(f"p{n}t", f"""<h2 class="num">{ja_tcy(n)}</h2>
{paragraphs(p["text"])}
{tail}
<div class="choices">{"".join(links)}</div>""", body_class)

    return book.write([("表紙", "cover.xhtml"), ("扉", "title.xhtml"), ("この本の遊び方", "howto.xhtml"),
                       ("冒険の始まり（1）", "p1.xhtml")], "howto.xhtml")


CSS_JA = """
@charset "utf-8";
html {
  writing-mode: vertical-rl;
  -epub-writing-mode: vertical-rl;
  -webkit-writing-mode: vertical-rl;
}
html.image-page {
  writing-mode: horizontal-tb;
  -epub-writing-mode: horizontal-tb;
  -webkit-writing-mode: horizontal-tb;
}
body { margin: 0; padding: 0; font-family: serif; line-height: 1.75; }
p { margin: 0; text-indent: 1em; text-align: justify; }
p.talk { text-indent: 0; }
p.end { text-indent: 0; margin-right: 1em; text-align: right; color: #6f6357; }
h2 { margin: 0 0 0 1em; font-size: 1.2em; font-weight: bold; }
h2.num { font-size: 1.5em; color: #6f6357; }
.tcy {
  text-combine-upright: all;
  -epub-text-combine: horizontal;
  -webkit-text-combine: horizontal;
}
.choices { margin-right: 1.5em; }
p.choice { text-indent: 0; margin: 0; }
p.choice a { color: #8b2a1c; text-decoration: none; }
p.choice .to { margin-top: 0.6em; }
.illust { margin: 0; padding: 0; text-align: center; page-break-inside: avoid; }
.illust img { max-width: 100%; max-height: 100%; }
.tobira { text-align: left; }
.tobira h1 { margin: 0 3em; font-size: 1.8em; letter-spacing: 0.2em; }
.tobira-sub { text-indent: 0; margin-top: 2em; font-size: 0.8em; color: #6f6357; }
.tobira-author { text-indent: 0; margin-top: 8em; letter-spacing: 0.2em; }
.colophon { text-indent: 0; margin-top: 8em; font-size: 0.7em; color: #6f6357; }
"""


# ---------------------------------------------------------------------------
# 英語版
# ---------------------------------------------------------------------------


def en_link(label, href, number=None):
    to = f', turn to <span class="to">{number}</span>.' if number else "."
    return f'<p class="choice"><a href="{href}">☞ {curly(html.escape(label, quote=False))}{to}</a></p>'


EN_FONT_FILES = [
    ("Fell", "IMFeENrm28P.ttf", "normal"),
    ("Fell", "IMFeENit28P.ttf", "italic"),
    ("FellSC", "IMFeENsc28P.ttf", "normal"),
    ("Maguntia", "UnifrakturMaguntia-Book.ttf", "normal"),
]


def build_en():
    story = tomllib.loads(STORY_EN.read_text(encoding="utf-8"))
    b = story["book"]
    faces = "\n".join(
        f'@font-face {{ font-family: "{fam}"; font-style: {style}; src: url("fonts/{file}"); }}'
        for fam, file, style in EN_FONT_FILES
    )
    # アポストロフィは文字参照にせず、組版用の ’ を直接書く（Kindle は &#39; のまま表示してしまうため）
    full_title = curly(f"{b['title_main']} {b['title_sub']}")
    book = Book("dragons-labyrinth", "en", False, full_title, b["author"], faces + CSS_EN, ("ja", "奥山晋"), "Okuyama, Shin")
    for i, (_, file, _) in enumerate(EN_FONT_FILES):
        book.media.append((f"font{i}", f"fonts/{file}", "font/ttf", (FONT_DIR / file).read_bytes(), ""))

    book.media.append(("cover-image", "images/cover.jpg", "image/jpeg", cover_image("dragons-labyrinth"), "cover-image"))
    book.doc("cover", '<div class="illust"><img src="images/cover.jpg" alt="Cover"/></div>', "image-page")
    e = {k: curly(html.escape(v, quote=False)) for k, v in b.items() if isinstance(v, str)}
    book.doc("title", f"""<div class="titlepage">
<h1><span class="t1">{e['title_main']}</span><br/><span class="t2">{e['title_sub']}</span></h1>
<p class="orn">❧</p>
<p class="being">{e['title_page_text']}</p>
<p class="by">Written by<br/><span class="sc">{e['author']}</span></p>
<p class="anno">Anno Domini {e['year']}</p>
<p class="colophon">{e['copyright']}</p>
</div>""")
    book.doc("howto", f"""<h2 class="howto">How to Use this Book</h2>
{en_paragraphs(b["how_to_play"])}
<div class="choices">{en_link("To begin thine adventure", "p1.xhtml", 1)}</div>""")

    for p in sorted(story["paragraph"], key=lambda p: p["number"]):
        n, kind = p["number"], p["kind"]
        tail = ""
        if kind in ("choice", "result"):
            links = [en_link(c["label"], f"p{c['to']}.xhtml", c["to"]) for c in p["choices"]]
        elif kind == "bad":
            tail = '<p class="end">Here endeth thy tale.</p>'
            links = [en_link("Take heart and try again", f"p{p['back']}.xhtml", p["back"])]
        else:
            tail = '<p class="end finis">Finis.</p>'
            links = [en_link("To begin anew, turn back to the cover", "cover.xhtml")]
        book.image_page(f"p{n}", f"img{n}", illustration(p["image"]))
        book.doc(f"p{n}t", f"""<p class="num">❦ {n} ❦</p>
{en_paragraphs(p["text"])}
{tail}
<div class="choices">{"".join(links)}</div>""")

    return book.write([("Cover", "cover.xhtml"), ("Title Page", "title.xhtml"), ("How to Use this Book", "howto.xhtml"),
                       ("The Adventure Begins (1)", "p1.xhtml")], "howto.xhtml")


CSS_EN = """
body { margin: 0; padding: 0; font-family: "Fell", serif; line-height: 1.4; }
p { margin: 0; text-indent: 1.3em; text-align: justify; }
p.first { text-indent: 0; }
p.first::first-letter { float: left; font-family: "Maguntia", serif; font-size: 3.2em; line-height: 0.85; padding: 0.05em 0.08em 0 0; color: #96241a; }
.sc { font-family: "FellSC", serif; letter-spacing: 0.06em; }
p.num { text-indent: 0; text-align: center; font-family: "FellSC", serif; letter-spacing: 0.25em; color: #6f6357; margin-bottom: 0.8em; }
p.end { text-indent: 0; text-align: center; margin-top: 1em; font-family: "FellSC", serif; letter-spacing: 0.12em; color: #6f6357; }
p.finis { font-family: "Maguntia", serif; font-size: 1.6em; color: inherit; }
.choices { margin-top: 1em; }
p.choice { text-indent: 0; margin-top: 0.4em; text-align: left; }
p.choice a { color: #96241a; font-style: italic; text-decoration: none; }
p.choice .to { font-style: normal; font-family: "FellSC", serif; }
h2.howto { text-align: center; font-family: "Maguntia", serif; font-weight: normal; font-size: 1.7em; margin: 0.5em 0 1em; }
.illust { margin: 0; padding: 0; text-align: center; }
.illust img { max-width: 100%; max-height: 100%; }
.titlepage { text-align: center; margin-top: 2em; }
.titlepage h1 { font-family: "Maguntia", serif; font-weight: normal; line-height: 1.15; margin: 0; }
.titlepage .t1 { font-size: 1.6em; }
.titlepage .t2 { font-size: 1.15em; }
.titlepage p { text-indent: 0; text-align: center; }
.titlepage .orn { font-size: 1.6em; color: #96241a; margin: 0.6em 0; }
.titlepage .being { font-style: italic; }
.titlepage .by { margin-top: 1.5em; }
.titlepage .anno { margin-top: 1em; font-family: "FellSC", serif; letter-spacing: 0.15em; }
.titlepage .colophon { margin-top: 2em; font-size: 0.75em; color: #6f6357; }
"""


if __name__ == "__main__":
    for target in sys.argv[1:] or ["ja", "en"]:
        {"ja": build_ja, "en": build_en}[target]()
