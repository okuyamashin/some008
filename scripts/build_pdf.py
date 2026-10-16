"""PDF 版（文庫サイズ）を書き出す。日本語版は縦書き・右綴じ、英語版は横書き・左綴じ。

使い方:
    build/.venv/bin/python scripts/build_pdf.py        # 日本語版と英語版の両方
    build/.venv/bin/python scripts/build_pdf.py ja     # dist/ryu-no-meikyu.pdf
    build/.venv/bin/python scripts/build_pdf.py en     # dist/dragons-labyrinth.pdf

準備（初回だけ）:
    python3 -m venv build/.venv && build/.venv/bin/pip install pypdf

流れ:
    1. 印刷用の HTML（1 ページ = A6 の 1 ページ）を dist/*.print.html に書き出す
    2. Chrome のヘッドレス印刷で PDF にする
    3. pypdf で綴じ方向・見開き表示とタイトル・著者を書き込む

見開き表示では表紙が 1 枚で、そのあとは 2 ページずつ並ぶ。
日本語版（右綴じ）: 表紙 → 扉（右）・遊び方（左）→ 各パラグラフの本文（右）・挿絵（左）
英語版（左綴じ）:   表紙 → 遊び方（左）・扉（右）→ 各パラグラフの本文（左）・挿絵（右）
"""

import base64
import html
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_html import CACHE_DIR, RAW_DIR, ROOT, STORY, STORY_EN, curly, en_choice, en_paragraphs, font_faces, paragraphs, tcy  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GRAY_PROFILE = "/System/Library/ColorSync/Profiles/Generic Gray Gamma 2.2 Profile.icc"


def jpeg_data_uri(name, gray):
    """PDF 用の画像。Chrome は JPEG ならそのまま PDF に入れるが、WebP は無圧縮に近い形に変えてしまうため。"""
    src = RAW_DIR / f"{name}.png"
    if not src.exists():
        sys.exit(f"画像がありません: {src.relative_to(ROOT)}")
    dst = CACHE_DIR / f"{name}{'.gray' if gray else ''}.jpg"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "65" if gray else "75", "--resampleWidth", "1000"]
        if gray:
            cmd += ["-m", GRAY_PROFILE]
        subprocess.run(cmd + [str(src), "--out", str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return "data:image/jpeg;base64," + base64.b64encode(dst.read_bytes()).decode()


def link(label, to):
    return f'<a href="#{to}"><span class="mark">◆</span>{html.escape(label)}<span class="to">{tcy(to[1:]) + "へ" if to.startswith("p") else ""}</span></a>'


def text_page(p):
    n, kind = p["number"], p["kind"]
    tail = ""
    if kind in ("choice", "result"):
        links = [link(c["label"], f"p{c['to']}") for c in p["choices"]]
    elif kind == "bad":
        tail = '<p class="end">——おしまい</p>'
        links = [link("気を取り直して、やり直す", f"p{p['back']}")]
    else:
        tail = '<p class="end">——めでたし、めでたし</p>'
        links = [link("最初から読む", "cover")]
    return f"""
<div class="pg text" id="p{n}">
  <div class="num">{n}</div>
  {paragraphs(p["text"])}
  {tail}
  <nav class="choices">{"".join(links)}</nav>
</div>"""


def image_page(p):
    return f"""
<div class="pg illust"><img src="{jpeg_data_uri(p["image"], gray=True)}" alt=""></div>"""


def build_ja():
    story = tomllib.loads(STORY.read_text(encoding="utf-8"))
    book = story["book"]
    title, subtitle, author, year = (html.escape(book[k]) for k in ("title", "subtitle", "author", "year"))
    cover = jpeg_data_uri(book["cover_image"], gray=False)
    pages = "".join(text_page(p) + image_page(p) for p in sorted(story["paragraph"], key=lambda p: p["number"]))
    page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{PRINT_CSS}</style>
</head>
<body>
<div class="pg cover" id="cover">
  <img src="{cover}" alt="">
  <span class="cover-title">{title}</span>
  <span class="cover-sub">{subtitle}</span>
  <span class="cover-author">{author}</span>
</div>
<div class="pg tobira">
  <h1>{title}</h1>
  <p class="tobira-sub">{subtitle}</p>
  <p class="tobira-author">{author}　作</p>
  <p class="colophon">© {year}　{author}</p>
</div>
<div class="pg text howto">
  <h2>この本の遊び方</h2>
  {paragraphs(book["how_to_play"])}
  <nav class="choices">{link("冒険を始める", "p1")}</nav>
</div>
{pages}
</body>
</html>
"""
    make_pdf("ryu-no-meikyu", page, book["title"], book["author"], book["subtitle"], rtl=True)


def make_pdf(name, page, title, author, subject, rtl):
    print_html = ROOT / "dist" / f"{name}.print.html"
    raw_pdf = ROOT / "build" / f"{name}.raw.pdf"
    out_pdf = ROOT / "dist" / f"{name}.pdf"
    print_html.parent.mkdir(parents=True, exist_ok=True)
    raw_pdf.parent.mkdir(parents=True, exist_ok=True)
    print_html.write_text(page, encoding="utf-8")
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--print-to-pdf={raw_pdf}", print_html.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DictionaryObject, NameObject

    writer = PdfWriter(clone_from=PdfReader(raw_pdf))
    root = writer._root_object
    # 表紙を 1 枚にして、そのあとを見開きで並べる
    root[NameObject("/PageLayout")] = NameObject("/TwoPageRight")
    root[NameObject("/ViewerPreferences")] = DictionaryObject(
        {NameObject("/Direction"): NameObject("/R2L" if rtl else "/L2R")}
    )
    writer.add_metadata({"/Title": title, "/Author": author, "/Subject": subject})
    with out_pdf.open("wb") as f:
        writer.write(f)
    print(f"{out_pdf.relative_to(ROOT)} ({len(writer.pages)} ページ, {out_pdf.stat().st_size / 1024 / 1024:.1f} MB)")


# ---------------------------------------------------------------------------
# 英語版
# ---------------------------------------------------------------------------


def en_text_page(p):
    n, kind = p["number"], p["kind"]
    tail = ""
    if kind in ("choice", "result"):
        links = [en_choice(c["label"], c["to"]) for c in p["choices"]]
    elif kind == "bad":
        tail = '<p class="end">Here endeth thy tale.</p>'
        links = [en_choice("Take heart and try again", p["back"])]
    else:
        tail = '<p class="end finis">Finis.</p>'
        links = ['<a href="#cover"><span class="hand">☞</span> To begin anew, turn back to the cover.</a>']
    return f"""
<div class="pg text" id="p{n}">
  <div class="num">❦ {n} ❦</div>
  {en_paragraphs(p["text"])}
  {tail}
  <nav class="choices">{"".join(links)}</nav>
</div>"""


def build_en():
    story = tomllib.loads(STORY_EN.read_text(encoding="utf-8"))
    raw = story["book"]
    book = {k: curly(html.escape(v, quote=False)) if isinstance(v, str) else v for k, v in raw.items()}
    cover = jpeg_data_uri(raw["cover_image"], gray=False)
    pages = "".join(en_text_page(p) + image_page(p) for p in sorted(story["paragraph"], key=lambda p: p["number"]))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{book['title_main']} {book['title_sub']}</title>
<style>{font_faces()}
{PRINT_CSS_EN}</style>
</head>
<body>
<div class="pg cover" id="cover">
  <img src="{cover}" alt="">
  <span class="cover-title"><span class="t1">{book['title_main']}</span><span class="t2">{book['title_sub']}</span></span>
  <span class="cover-sub">{book['subtitle']}</span>
  <span class="cover-author">{book['author']}</span>
</div>
<div class="pg text howto">
  <h2>How to Use this Book</h2>
  {en_paragraphs(raw["how_to_play"])}
  <nav class="choices">{en_choice("To begin thine adventure", 1)}</nav>
</div>
<div class="pg titlepage">
  <h1><span class="t1">{book['title_main']}</span><span class="t2">{book['title_sub']}</span></h1>
  <p class="orn">❧</p>
  <p class="being">{book['title_page_text']}</p>
  <p class="by">Written by<br><span class="sc">{book['author']}</span></p>
  <p class="anno">Anno Domini {book['year']}</p>
  <p class="colophon">{book['copyright']}</p>
</div>
{pages}
</body>
</html>
"""
    make_pdf("dragons-labyrinth", page, f"{raw['title_main']} {raw['title_sub']}", raw["author"], raw["subtitle"], rtl=False)


PRINT_CSS = """
@page { size: 105mm 148mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  color: #231d19;
  font-family: "Hiragino Mincho ProN", "Hiragino Mincho Pro", "Yu Mincho", YuMincho, "Noto Serif JP", serif;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
a { color: #8b2a1c; text-decoration: none; }
.pg {
  position: relative;
  width: 105mm;
  height: 148mm;
  overflow: hidden;
  break-after: page;
  background: #fff;
}
.pg:last-child { break-after: auto; }

/* 本文：縦書き。文庫の 1 ページにおさまる大きさ */
.text {
  writing-mode: vertical-rl;
  padding: 14mm 10mm 11mm 9mm;
  font-size: 8.6pt;
  line-height: 1.7;
}
.text p { margin: 0; text-indent: 1em; text-align: justify; }
.text p.talk { text-indent: 0; }
.text p.end { text-indent: 0; margin-block-start: 1em; text-align: end; color: #6f6357; }
.num {
  position: absolute;
  top: 5.5mm;
  right: 10mm;
  writing-mode: horizontal-tb;
  font-size: 14pt;
  color: #6f6357;
}
.tcy { text-combine-upright: all; }
.choices { margin-block-start: 1.4em; }
.choices a { display: block; margin-block-end: 0.3em; }
.choices .mark { margin-inline-end: 0.3em; font-size: 0.8em; }
.choices .to { margin-inline-start: 0.6em; }

/* 挿絵 */
.illust { display: flex; align-items: center; justify-content: center; padding: 11mm 10mm; }
.illust img { display: block; max-width: 100%; max-height: 100%; }

/* 表紙 */
.cover img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.cover span {
  position: absolute;
  writing-mode: vertical-rl;
  color: #f3ecda;
  text-shadow: 0 0.6mm 3mm rgba(0, 0, 0, 0.9), 0 0 0.8mm rgba(0, 0, 0, 0.9);
}
.cover-title { top: 8mm; right: 8mm; font-size: 21pt; font-weight: 700; letter-spacing: 0.18em; }
.cover-sub { top: 9mm; right: 22mm; font-size: 7pt; letter-spacing: 0.1em; }
.cover-author { bottom: 10mm; left: 9mm; font-size: 9pt; letter-spacing: 0.3em; }

/* 扉 */
.tobira { writing-mode: vertical-rl; display: flex; align-items: center; justify-content: center; }
.tobira h1 { margin: 0; font-size: 17pt; font-weight: 700; letter-spacing: 0.2em; }
.tobira p { margin: 0; }
.tobira-sub { position: absolute; top: 20mm; right: 15mm; font-size: 6.5pt; color: #6f6357; }
.tobira-author { position: absolute; bottom: 20mm; left: 24mm; font-size: 8pt; letter-spacing: 0.2em; }
.colophon { position: absolute; bottom: 6mm; left: 0; right: 0; writing-mode: horizontal-tb; text-align: center; font-size: 5.5pt; color: #6f6357; }

/* 遊び方 */
.howto h2 { margin: 0 0 0 1.2em; font-size: 1.3em; letter-spacing: 0.15em; }
"""


PRINT_CSS_EN = """
@page { size: 105mm 148mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  color: #231d19;
  font-family: "Fell", "Iowan Old Style", Georgia, serif;
  font-variant-ligatures: common-ligatures discretionary-ligatures;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
a { color: #96241a; text-decoration: none; }
.pg {
  position: relative;
  width: 105mm;
  height: 148mm;
  overflow: hidden;
  break-after: page;
  background: #fff;
}
.pg:last-child { break-after: auto; }

/* 本文。左ページなので、のど（綴じ側）は右 */
.text {
  padding: 10mm 12mm 10mm 10mm;
  font-size: 10.2pt;
  line-height: 1.38;
  text-align: justify;
  hyphens: auto;
}
.text p { margin: 0; text-indent: 1.3em; }
.text p.first { text-indent: 0; }
.text p.first::first-letter {
  float: left;
  font-family: "Maguntia", serif;
  font-size: 3.4em;
  line-height: 0.82;
  padding: 0.06em 0.08em 0 0;
  color: #96241a;
}
.text .sc { font-family: "FellSC", serif; letter-spacing: 0.06em; }
.num { text-align: center; font-family: "FellSC", serif; font-size: 1.1em; letter-spacing: 0.25em; color: #6f6357; margin-bottom: 0.7em; }
.text p.end { text-indent: 0; text-align: center; margin-top: 0.9em; font-family: "FellSC", serif; letter-spacing: 0.12em; color: #6f6357; }
.text p.finis { font-family: "Maguntia", serif; font-size: 1.7em; letter-spacing: 0.02em; color: #231d19; }
.choices { margin-top: 0.9em; }
.choices a { display: block; margin-top: 0.3em; padding-left: 1.4em; text-indent: -1.4em; text-align: left; font-style: italic; }
.choices .hand { font-style: normal; display: inline-block; width: 1.2em; text-indent: 0; }
.choices .to { font-style: normal; font-family: "FellSC", serif; letter-spacing: 0.05em; }

/* 挿絵。右ページ */
.illust { display: flex; align-items: center; justify-content: center; padding: 11mm 10mm; }
.illust img { display: block; max-width: 100%; max-height: 100%; }

/* 表紙 */
.cover { color: #f2ead6; text-align: center; }
.cover img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.cover > span { position: absolute; left: 6mm; right: 6mm; text-shadow: 0 0.6mm 3mm rgba(0, 0, 0, 0.9), 0 0 0.8mm rgba(0, 0, 0, 0.9); }
.cover-title { top: 7mm; font-family: "Maguntia", serif; line-height: 1.05; }
.cover-title .t1 { display: block; font-size: 19pt; }
.cover-title .t2 { display: block; font-size: 12.5pt; margin-top: 0.15em; }
.cover-sub { top: 31mm; font-style: italic; font-size: 7pt; }
.cover-author { bottom: 11mm; font-family: "FellSC", serif; font-size: 9pt; letter-spacing: 0.2em; }

/* 扉。右ページ */
.titlepage { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 12mm 13mm; font-size: 8.6pt; }
.titlepage h1 { margin: 0; font-family: "Maguntia", serif; font-weight: normal; line-height: 1.1; }
.titlepage h1 .t1 { display: block; font-size: 2.2em; }
.titlepage h1 .t2 { display: block; font-size: 1.5em; margin-top: 0.25em; }
.titlepage p { margin: 0; }
.titlepage .orn { font-size: 1.8em; color: #96241a; margin: 0.6em 0; }
.titlepage .being { font-style: italic; line-height: 1.45; }
.titlepage .by { margin-top: 1.4em; line-height: 1.45; }
.titlepage .sc { font-family: "FellSC", serif; font-size: 1.3em; letter-spacing: 0.12em; }
.titlepage .anno { margin-top: 1.1em; font-family: "FellSC", serif; letter-spacing: 0.15em; }
.titlepage .colophon { margin-top: 1.8em; font-size: 0.75em; color: #6f6357; }
.howto h2 { margin: 0.6em 0 0.9em; text-align: center; font-family: "Maguntia", serif; font-weight: normal; font-size: 1.8em; }
"""


if __name__ == "__main__":
    for target in sys.argv[1:] or ["ja", "en"]:
        {"ja": build_ja, "en": build_en}[target]()
