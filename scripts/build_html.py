"""story/story.toml と images/raw/ の画像から、1 ファイルで完結する HTML 版を書き出す。

使い方:
    python3 scripts/build_html.py

出力: dist/ryu-no-meikyu.html
画像は横 1000px の WebP に変換して build/images/ にキャッシュし、HTML に埋め込む。
変換には cwebp（brew install webp）を使う。
"""

import base64
import html
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY = ROOT / "story" / "story.toml"
RAW_DIR = ROOT / "images" / "raw"
CACHE_DIR = ROOT / "build" / "images"
OUT = ROOT / "dist" / "ryu-no-meikyu.html"

IMAGE_WIDTH = 1000
QUALITY_MONO = 60
QUALITY_COVER = 75


def webp_data_uri(name, quality):
    src = RAW_DIR / f"{name}.png"
    if not src.exists():
        sys.exit(f"画像がありません: {src.relative_to(ROOT)}")
    dst = CACHE_DIR / f"{name}.webp"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(quality), "-resize", str(IMAGE_WIDTH), "0", str(src), "-o", str(dst)],
            check=True,
        )
    return "data:image/webp;base64," + base64.b64encode(dst.read_bytes()).decode()


def tcy(number):
    """縦書きの中で数字を横に並べる（縦中横）。"""
    return f'<span class="tcy">{number}</span>'


def paragraphs(text):
    out = []
    for block in text.strip().split("\n\n"):
        line = html.escape(block.strip().replace("\n", ""))
        cls = ' class="talk"' if line[:1] in "「『" else ""
        out.append(f"<p{cls}>{line}</p>")
    return "\n".join(out)


def choice_link(label, to):
    return f'<a href="#p{to}"><span class="mark">◆</span>{html.escape(label)}<span class="to">{tcy(to)}へ</span></a>'


def spread(p):
    n, kind = p["number"], p["kind"]
    links = []
    tail = ""
    if kind in ("choice", "result"):
        links = [choice_link(c["label"], c["to"]) for c in p["choices"]]
    elif kind == "bad":
        tail = '<p class="end">——おしまい</p>'
        links = [choice_link("気を取り直して、やり直す", p["back"])]
    elif kind == "ending":
        tail = '<p class="end">——めでたし、めでたし</p>'
        links = ['<a href="#intro"><span class="mark">◆</span>最初から読む</a>']
    img = webp_data_uri(p["image"], QUALITY_MONO)
    return f"""
<section class="spread {kind}" id="p{n}" aria-label="パラグラフ{n}">
  <div class="page left illust"><img src="{img}" alt="" decoding="async"></div>
  <div class="page right text-page">
    <div class="num">{n}</div>
    {paragraphs(p["text"])}
    {tail}
    <nav class="choices">{"".join(links)}</nav>
  </div>
</section>"""


def build():
    story = tomllib.loads(STORY.read_text(encoding="utf-8"))
    book = story["book"]
    title, subtitle, author, year = (html.escape(book[k]) for k in ("title", "subtitle", "author", "year"))
    cover = webp_data_uri(book["cover_image"], QUALITY_COVER)
    body = "\n".join(spread(p) for p in story["paragraph"])

    page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="{author}">
<meta name="description" content="{subtitle}">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>

<section class="spread cover" id="cover" aria-label="表紙">
  <a class="page cover-page" href="#intro" style="background-image:url({cover})">
    <span class="cover-title">{title}</span>
    <span class="cover-sub">{subtitle}</span>
    <span class="cover-author">{author}</span>
    <span class="cover-start">ページをめくる</span>
  </a>
</section>

<section class="spread intro" id="intro" aria-label="扉と遊び方">
  <div class="page left text-page howto">
    <h2>この本の遊び方</h2>
    {paragraphs(book["how_to_play"])}
    <nav class="choices">{choice_link("冒険を始める", 1)}</nav>
  </div>
  <div class="page right tobira">
    <h1>{title}</h1>
    <p class="tobira-sub">{subtitle}</p>
    <p class="tobira-author">{author}　作</p>
    <p class="colophon">© {year}　{author}</p>
  </div>
</section>
{body}
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024 / 1024:.1f} MB)")


CSS = """
:root {
  --paper: #f3ecda;
  --paper-bad: #e4d9c1;
  --ink: #2a2420;
  --ink-soft: #7a6c5f;
  --accent: #8b2a1c;
  --desk-1: #3a332d;
  --desk-2: #191513;
  --h: min(92vh, calc(94vw / 1.419));
}
@supports (height: 1svh) {
  :root { --h: min(92svh, calc(94vw / 1.419)); }
}
* { box-sizing: border-box; }
html, body { margin: 0; }
body {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(ellipse at center, var(--desk-1) 0%, var(--desk-2) 100%) fixed;
  color: var(--ink);
  font-family: "Hiragino Mincho ProN", "Hiragino Mincho Pro", "Yu Mincho", YuMincho, "Noto Serif JP", "Noto Serif CJK JP", serif;
  font-feature-settings: "palt" 0;
}

/* 見開き。表示するのは :target の 1 つだけ。ハッシュがないときは表紙。 */
.spread {
  display: none;
  height: var(--h);
  aspect-ratio: 210 / 148;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}
.spread:target,
body:not(:has(.spread:target)) #cover { display: flex; animation: turn 0.35s ease; }
@keyframes turn { from { opacity: 0; } to { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .spread { animation: none !important; } }

.page {
  position: relative;
  flex: 1 1 50%;
  min-width: 0;
  background-color: var(--paper);
  overflow: hidden;
}
.page.left { background-image: linear-gradient(to left, rgba(60, 40, 20, 0.16), rgba(60, 40, 20, 0) 9%); }
.page.right { background-image: linear-gradient(to right, rgba(60, 40, 20, 0.16), rgba(60, 40, 20, 0) 9%); }
.bad .page { background-color: var(--paper-bad); }

/* 挿絵。白地を紙の色になじませる。 */
.illust { display: flex; align-items: center; justify-content: center; padding: 8% 9%; }
.illust img { display: block; max-width: 100%; max-height: 100%; mix-blend-mode: multiply; }

/* 本文。縦書き。 */
.text-page {
  writing-mode: vertical-rl;
  padding: 11% 8% 7% 7%;
  font-size: calc(var(--h) * 0.0185);
  line-height: 1.65;
  overflow: auto;
}
.text-page p { margin: 0; text-indent: 1em; text-align: justify; }
.text-page p.talk { text-indent: 0; }
.text-page p.end { text-indent: 0; margin-block-start: 1em; text-align: end; color: var(--ink-soft); }
.num {
  position: absolute;
  top: 3.5%;
  right: 9%;
  writing-mode: horizontal-tb;
  font-size: calc(var(--h) * 0.04);
  color: var(--ink-soft);
  letter-spacing: 0.05em;
}
.tcy { text-combine-upright: all; }

.choices { margin-block-start: 1.6em; }
.choices a {
  display: block;
  color: var(--accent);
  text-decoration: none;
  margin-block-end: 0.4em;
}
.choices a:hover { text-decoration: underline; text-underline-offset: 0.2em; }
.choices a:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; }
.choices .mark { margin-inline-end: 0.3em; font-size: 0.8em; }
.choices .to { margin-inline-start: 0.6em; }

/* 表紙 */
.cover { aspect-ratio: 105 / 148; }
.cover-page {
  display: block;
  background-size: cover;
  background-position: center;
  color: var(--paper);
  text-decoration: none;
}
.cover-title, .cover-sub, .cover-author {
  position: absolute;
  writing-mode: vertical-rl;
  text-shadow: 0 2px 14px rgba(0, 0, 0, 0.85), 0 0 3px rgba(0, 0, 0, 0.9);
}
.cover-title { top: 6%; right: 8%; font-size: calc(var(--h) * 0.068); font-weight: 700; letter-spacing: 0.18em; }
.cover-sub { top: 7%; right: calc(8% + var(--h) * 0.09); font-size: calc(var(--h) * 0.022); letter-spacing: 0.1em; }
.cover-author { bottom: 7%; left: 8%; font-size: calc(var(--h) * 0.026); letter-spacing: 0.3em; }
.cover-start {
  position: absolute;
  bottom: 4%;
  left: 50%;
  transform: translateX(-50%);
  font-size: calc(var(--h) * 0.018);
  letter-spacing: 0.2em;
  padding: 0.4em 1.2em;
  border: 1px solid rgba(243, 236, 218, 0.7);
  background: rgba(20, 15, 10, 0.45);
}
.cover-page:hover .cover-start, .cover-page:focus-visible .cover-start { background: rgba(139, 42, 28, 0.75); }

/* 扉と遊び方 */
.tobira {
  writing-mode: vertical-rl;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 14% 12%;
}
.tobira h1 { margin: 0 auto; font-size: calc(var(--h) * 0.055); letter-spacing: 0.2em; font-weight: 700; }
.tobira p { margin: 0; text-align: end; }
.tobira-sub { position: absolute; top: 14%; right: 14%; font-size: calc(var(--h) * 0.02); color: var(--ink-soft); }
.tobira-author { position: absolute; bottom: 14%; left: 22%; font-size: calc(var(--h) * 0.024); letter-spacing: 0.2em; }
.colophon { position: absolute; bottom: 4%; left: 50%; transform: translateX(-50%); writing-mode: horizontal-tb; font-size: calc(var(--h) * 0.014); color: var(--ink-soft); white-space: nowrap; }
.howto h2 { margin: 0 0 0 1.2em; font-size: 1.3em; letter-spacing: 0.15em; }

/* スマホ・縦長の画面：見開きをやめ、絵の下に本文。本文は横書き。 */
@media (max-width: 720px), (max-aspect-ratio: 4 / 5) {
  body { display: block; min-height: 0; background: var(--paper); }
  .spread { width: 100%; height: auto; aspect-ratio: auto; flex-direction: column; box-shadow: none; }
  .page { flex: none; }
  .page.left, .page.right { background-image: none; }
  .illust { padding: 20px 20px 0; }
  .illust img { max-height: 55svh; }
  .text-page {
    writing-mode: horizontal-tb;
    font-size: 17px;
    line-height: 1.9;
    padding: 56px 22px 40px;
    overflow: visible;
  }
  .num { top: 14px; left: 22px; right: auto; font-size: 26px; }
  .text-page p.end { text-align: right; }
  .choices a { padding: 0.5em 0; border-top: 1px solid rgba(139, 42, 28, 0.2); margin: 0; }
  .choices .to { margin-left: 0.6em; }
  .cover { width: 100%; height: 100svh; aspect-ratio: auto; }
  .cover-page { height: 100%; }
  .cover-title { font-size: 34px; }
  .cover-sub { right: calc(8% + 48px); font-size: 13px; }
  .cover-author { font-size: 15px; }
  .cover-start { font-size: 14px; }
  .intro .tobira { order: -1; min-height: 100svh; }
  .tobira h1 { font-size: 30px; }
  .tobira-sub { font-size: 13px; }
  .tobira-author { font-size: 15px; }
  .colophon { font-size: 11px; }
  .howto h2 { margin: 0 0 1em; }
  .bad .page { background-color: var(--paper-bad); }
}
"""


if __name__ == "__main__":
    build()
