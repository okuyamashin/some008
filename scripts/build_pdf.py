"""日本語版の PDF（文庫サイズ・縦書き・右綴じ）を書き出す。

使い方:
    build/.venv/bin/python scripts/build_pdf.py

準備（初回だけ）:
    python3 -m venv build/.venv && build/.venv/bin/pip install pypdf

流れ:
    1. 印刷用の HTML（1 ページ = A6 の 1 ページ）を dist/ryu-no-meikyu.print.html に書き出す
    2. Chrome のヘッドレス印刷で PDF にする
    3. pypdf で「右綴じ・見開き表示」とタイトル・著者を書き込み、dist/ryu-no-meikyu.pdf にする

ページの順番: 表紙 → 扉 → 遊び方 → パラグラフ 1〜15（本文のページ → 挿絵のページ）。
右綴じの見開き表示では、表紙が 1 枚で、そのあとは偶数ページが右、奇数ページが左に並ぶ。
"""

import base64
import html
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_html import CACHE_DIR, RAW_DIR, ROOT, STORY, paragraphs, tcy  # noqa: E402

PRINT_HTML = ROOT / "dist" / "ryu-no-meikyu.print.html"
RAW_PDF = ROOT / "build" / "ryu-no-meikyu.raw.pdf"
OUT_PDF = ROOT / "dist" / "ryu-no-meikyu.pdf"
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


def build_print_html():
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
    PRINT_HTML.parent.mkdir(parents=True, exist_ok=True)
    PRINT_HTML.write_text(page, encoding="utf-8")
    return book


def print_pdf():
    RAW_PDF.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--print-to-pdf={RAW_PDF}", PRINT_HTML.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def finish_pdf(book):
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DictionaryObject, NameObject

    writer = PdfWriter(clone_from=PdfReader(RAW_PDF))
    root = writer._root_object
    root[NameObject("/PageLayout")] = NameObject("/TwoPageRight")
    root[NameObject("/ViewerPreferences")] = DictionaryObject({NameObject("/Direction"): NameObject("/R2L")})
    writer.add_metadata({"/Title": book["title"], "/Author": book["author"], "/Subject": book["subtitle"]})
    with OUT_PDF.open("wb") as f:
        writer.write(f)
    print(f"{OUT_PDF.relative_to(ROOT)} ({len(writer.pages)} ページ, {OUT_PDF.stat().st_size / 1024 / 1024:.1f} MB)")


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


if __name__ == "__main__":
    book = build_print_html()
    print_pdf()
    finish_pdf(book)
