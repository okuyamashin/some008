"""本文データと images/raw/ の画像から、1 ファイルで完結する HTML 版を書き出す。

使い方:
    python3 scripts/build_html.py                              # books/ 以下の全巻の日本語版と英語版
    python3 scripts/build_html.py --book ryu-no-meikyu         # 1 冊だけ
    python3 scripts/build_html.py --book ryu-no-meikyu ja      # 日本語版だけ（story.toml → dist/<slug_ja>.html）
    python3 scripts/build_html.py --book ryu-no-meikyu en      # 英語版だけ（story.en.toml → dist/<slug_en>.html）

画像は横 1000px の WebP に変換して build/images/<名前>/ にキャッシュし、HTML に埋め込む。
変換には cwebp（brew install webp）を使う。英語版は fonts/ のフォントも埋め込む。
"""

import base64
import html
import re
import subprocess
import sys

from books import ROOT, parse_args

FONT_DIR = ROOT / "fonts"

IMAGE_WIDTH = 1000
QUALITY_MONO = 60
QUALITY_COVER = 75


def webp_path(src, name, quality):
    png = src.raw_dir / f"{name}.png"
    if not png.exists():
        sys.exit(f"画像がありません: {png.relative_to(ROOT)}")
    dst = src.cache_dir / f"{name}.webp"
    if not dst.exists() or dst.stat().st_mtime < png.stat().st_mtime:
        src.cache_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(quality), "-resize", str(IMAGE_WIDTH), "0", str(png), "-o", str(dst)],
            check=True,
        )
    return dst


def webp_data_uri(src, name, quality):
    return "data:image/webp;base64," + base64.b64encode(webp_path(src, name, quality).read_bytes()).decode()


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


def choice_link(label, to, back=False):
    attr = ' data-dir="back"' if back else ""
    return f'<a href="#p{to}"{attr}><span class="mark">◆</span>{html.escape(label)}<span class="to">{tcy(to)}へ</span></a>'


def spread(src, p):
    n, kind = p["number"], p["kind"]
    links = []
    tail = ""
    if kind in ("choice", "result"):
        links = [choice_link(c["label"], c["to"]) for c in p["choices"]]
    elif kind == "bad":
        tail = '<p class="end">——おしまい</p>'
        links = [choice_link("気を取り直して、やり直す", p["back"], back=True)]
    elif kind == "ending":
        tail = '<p class="end">——めでたし、めでたし</p>'
        links = ['<a href="#cover" data-dir="back"><span class="mark">◆</span>最初から読む</a>']
    img = webp_data_uri(src, p["image"], QUALITY_MONO)
    return f"""
<section tabindex="-1" class="spread {kind}" id="p{n}" aria-label="パラグラフ{n}">
  <div class="page left illust"><img src="{img}" alt="" decoding="async"></div>
  <div class="page right text-page">
    <div class="num">{n}</div>
    {paragraphs(p["text"])}
    {tail}
    <nav class="choices">{"".join(links)}</nav>
  </div>
</section>"""


def build_ja(src):
    story = src.story("ja")
    book = story["book"]
    title, subtitle, author, year = (html.escape(book[k]) for k in ("title", "subtitle", "author", "year"))
    cover = webp_data_uri(src, book["cover_image"], QUALITY_COVER)
    body = "\n".join(spread(src, p) for p in story["paragraph"])

    page = f"""<!doctype html>
<html lang="ja" data-binding="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="{author}">
<meta name="description" content="{subtitle}">
<title>{title}</title>
<script>document.documentElement.classList.add("js")</script>
<style>{CSS}</style>
</head>
<body>

<section tabindex="-1" class="spread cover" id="cover" aria-label="表紙">
  <a class="page cover-page" href="#intro" style="background-image:url({cover})">
    <span class="cover-title">{title}</span>
    <span class="cover-sub">{subtitle}</span>
    <span class="cover-author">{author}</span>
    <span class="cover-start">ページをめくる</span>
  </a>
</section>

<section tabindex="-1" class="spread intro" id="intro" aria-label="扉と遊び方">
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
<script>{PAGE_JS}</script>
</body>
</html>
"""
    write(src.slug("ja"), page)


def write(slug, page):
    out = ROOT / "dist" / f"{slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} ({out.stat().st_size / 1024 / 1024:.1f} MB)")


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
html:not(.js) .spread:target,
html:not(.js) body:not(:has(.spread:target)) #cover { display: flex; animation: turn 0.35s ease; }
html.js .spread.current, html.js .spread.leaving { display: flex; }
.spread { grid-area: 1 / 1; }
.spread.leaving { z-index: 2; }
.spread:focus { outline: none; }
@keyframes turn { from { opacity: 0; } to { opacity: 1; } }
/* めくれる紙（JS が作る） */
.leaf { position: fixed; z-index: 10; pointer-events: none; transform-style: preserve-3d; will-change: transform; }
.leaf .face { position: absolute; inset: 0; display: flex; backface-visibility: hidden; -webkit-backface-visibility: hidden; }
.leaf .face > .page { flex: 1 1 100%; height: 100%; }
.leaf .face.back { transform: rotateY(180deg); }
.leaf .shade { position: absolute; inset: 0; background: #1e140a; opacity: 0; pointer-events: none; }
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


# ---------------------------------------------------------------------------
# 英語版（Early Modern English 風）。横書き・左綴じなので、見開きは左に本文、右に挿絵。
# ---------------------------------------------------------------------------

EN_FONTS = [
    ("Fell", "IMFeENrm28P.ttf", "normal"),
    ("Fell", "IMFeENit28P.ttf", "italic"),
    ("FellSC", "IMFeENsc28P.ttf", "normal"),
    ("Maguntia", "UnifrakturMaguntia-Book.ttf", "normal"),
]


def font_faces():
    faces = []
    for family, file, style in EN_FONTS:
        data = base64.b64encode((FONT_DIR / file).read_bytes()).decode()
        faces.append(
            f"@font-face {{ font-family: '{family}'; font-style: {style}; font-display: block; "
            f"src: url(data:font/ttf;base64,{data}) format('truetype'); }}"
        )
    return "\n".join(faces)


def curly(text):
    """まっすぐな引用符を、組版らしい曲がった引用符にする。"""
    text = re.sub(r'(^|[\s(—])"', r"\1“", text)
    text = text.replace('"', "”")
    return text.replace("'", "’")


def en_paragraphs(text):
    out = []
    for i, block in enumerate(text.strip().split("\n\n")):
        line = curly(html.escape(block.strip().replace("\n", " "), quote=False))
        # 札などの大文字だけの語句は、スモールキャップスで組む
        line = re.sub(r"\b[A-Z]{2,}(?:[ .,]+[A-Z]{2,})*\.?", lambda m: f'<span class="sc">{m.group(0).lower()}</span>', line)
        cls = ' class="first"' if i == 0 else ""
        out.append(f"<p{cls}>{line}</p>")
    return "\n".join(out)


def en_choice(label, to, back=False):
    attr = ' data-dir="back"' if back else ""
    return (
        f'<a href="#p{to}"{attr}><span class="hand">☞</span> {curly(html.escape(label, quote=False))}, '
        f'turn to <span class="to">{to}</span>.</a>'
    )


def en_spread(src, p):
    n, kind = p["number"], p["kind"]
    tail = ""
    if kind in ("choice", "result"):
        links = [en_choice(c["label"], c["to"]) for c in p["choices"]]
    elif kind == "bad":
        tail = '<p class="end">Here endeth thy tale.</p>'
        links = [en_choice("Take heart and try again", p["back"], back=True)]
    else:
        tail = '<p class="end finis">Finis.</p>'
        links = ['<a href="#cover" data-dir="back"><span class="hand">☞</span> To begin anew, turn back to the cover.</a>']
    img = webp_data_uri(src, p["image"], QUALITY_MONO)
    return f"""
<section tabindex="-1" class="spread {kind}" id="p{n}" aria-label="Passage {n}">
  <div class="page left text-page">
    <div class="num">❦ {n} ❦</div>
    {en_paragraphs(p["text"])}
    {tail}
    <nav class="choices">{"".join(links)}</nav>
  </div>
  <div class="page right illust"><img src="{img}" alt="" decoding="async"></div>
</section>"""


def build_en(src):
    story = src.story("en")
    book = {k: curly(html.escape(v, quote=False)) if isinstance(v, str) else v for k, v in story["book"].items()}
    cover = webp_data_uri(src, story["book"]["cover_image"], QUALITY_COVER)
    body = "\n".join(en_spread(src, p) for p in story["paragraph"])
    title = f"{book['title_main']} {book['title_sub']}"

    page = f"""<!doctype html>
<html lang="en" data-binding="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="{book['author']}">
<meta name="description" content="{book['subtitle']}">
<title>{title}</title>
<script>document.documentElement.classList.add("js")</script>
<style>{font_faces()}
{CSS_EN}</style>
</head>
<body>

<section tabindex="-1" class="spread cover" id="cover" aria-label="Cover">
  <a class="page cover-page" href="#intro" style="background-image:url({cover})">
    <span class="cover-title"><span class="t1">{book['title_main']}</span><span class="t2">{book['title_sub']}</span></span>
    <span class="cover-sub">{book['subtitle']}</span>
    <span class="cover-author">{book['author']}</span>
    <span class="cover-start">Turn the Page</span>
  </a>
</section>

<section tabindex="-1" class="spread intro" id="intro" aria-label="How to use this book, and title page">
  <div class="page left text-page howto">
    <h2>How to Use this Book</h2>
    {en_paragraphs(story["book"]["how_to_play"])}
    <nav class="choices">{en_choice("To begin thine adventure", 1)}</nav>
  </div>
  <div class="page right titlepage">
    <h1><span class="t1">{book['title_main']}</span><span class="t2">{book['title_sub']}</span></h1>
    <p class="orn">❧</p>
    <p class="being">{book['title_page_text']}</p>
    <p class="by">Written by<br><span class="sc">{book['author']}</span></p>
    <p class="anno">Anno Domini {book['year']}</p>
    <p class="colophon">{book['copyright']}</p>
  </div>
</section>
{body}
<script>{PAGE_JS}</script>
</body>
</html>
"""
    write(src.slug("en"), page)


CSS_EN = """
:root {
  --paper: #f2ead6;
  --paper-bad: #e2d6bc;
  --ink: #2a221c;
  --ink-soft: #75685a;
  --red: #96241a;
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
  font-family: "Fell", "Iowan Old Style", Georgia, serif;
  font-variant-ligatures: common-ligatures discretionary-ligatures;
}

.spread {
  display: none;
  height: var(--h);
  aspect-ratio: 210 / 148;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}
html:not(.js) .spread:target,
html:not(.js) body:not(:has(.spread:target)) #cover { display: flex; animation: turn 0.35s ease; }
html.js .spread.current, html.js .spread.leaving { display: flex; }
.spread { grid-area: 1 / 1; }
.spread.leaving { z-index: 2; }
.spread:focus { outline: none; }
@keyframes turn { from { opacity: 0; } to { opacity: 1; } }
/* めくれる紙（JS が作る） */
.leaf { position: fixed; z-index: 10; pointer-events: none; transform-style: preserve-3d; will-change: transform; }
.leaf .face { position: absolute; inset: 0; display: flex; backface-visibility: hidden; -webkit-backface-visibility: hidden; }
.leaf .face > .page { flex: 1 1 100%; height: 100%; }
.leaf .face.back { transform: rotateY(180deg); }
.leaf .shade { position: absolute; inset: 0; background: #1e140a; opacity: 0; pointer-events: none; }
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

.illust { display: flex; align-items: center; justify-content: center; padding: 8% 9%; }
.illust img { display: block; max-width: 100%; max-height: 100%; mix-blend-mode: multiply; }

/* 本文 */
.text-page {
  padding: 7% 11% 6% 9%;
  font-size: calc(var(--h) * 0.0205);
  line-height: 1.38;
  text-align: justify;
  hyphens: auto;
  overflow: auto;
}
.text-page p { margin: 0; text-indent: 1.3em; }
.text-page p.first { text-indent: 0; }
.text-page .sc { font-family: "FellSC", serif; letter-spacing: 0.06em; }
.text-page p.first::first-letter {
  float: left;
  font-family: "Maguntia", serif;
  font-size: 3.4em;
  line-height: 0.82;
  padding: 0.06em 0.08em 0 0;
  color: var(--red);
}
.num {
  text-align: center;
  font-family: "FellSC", serif;
  font-size: 1.15em;
  letter-spacing: 0.25em;
  color: var(--ink-soft);
  margin-bottom: 0.7em;
}
.text-page p.end {
  text-indent: 0;
  text-align: center;
  margin-top: 0.9em;
  font-family: "FellSC", serif;
  letter-spacing: 0.12em;
  color: var(--ink-soft);
}
.text-page p.finis { font-family: "Maguntia", serif; font-size: 1.7em; letter-spacing: 0.02em; color: var(--ink); }

.choices { margin-top: 0.9em; }
.choices a {
  display: block;
  margin-top: 0.3em;
  padding-left: 1.4em;
  text-indent: -1.4em;
  text-align: left;
  color: var(--red);
  font-style: italic;
  text-decoration: none;
}
.choices a:hover { text-decoration: underline; text-underline-offset: 0.15em; }
.choices a:focus-visible { outline: 2px solid var(--red); outline-offset: 3px; }
.choices .hand { font-style: normal; display: inline-block; width: 1.2em; text-indent: 0; }
.choices .to { font-style: normal; font-family: "FellSC", serif; letter-spacing: 0.05em; }

/* 表紙 */
.cover { aspect-ratio: 105 / 148; }
.cover-page {
  display: block;
  background-size: cover;
  background-position: center;
  color: var(--paper);
  text-decoration: none;
  text-align: center;
}
.cover-title, .cover-sub, .cover-author { position: absolute; left: 6%; right: 6%; text-shadow: 0 2px 14px rgba(0, 0, 0, 0.9), 0 0 3px rgba(0, 0, 0, 0.9); }
.cover-title { top: 4.5%; font-family: "Maguntia", serif; line-height: 1.05; }
.cover-title .t1 { display: block; font-size: calc(var(--h) * 0.062); }
.cover-title .t2 { display: block; font-size: calc(var(--h) * 0.04); margin-top: 0.15em; }
.cover-sub { top: 21%; font-style: italic; font-size: calc(var(--h) * 0.021); }
.cover-author { bottom: 11%; font-family: "FellSC", serif; font-size: calc(var(--h) * 0.026); letter-spacing: 0.2em; }
.cover-start {
  position: absolute;
  bottom: 4%;
  left: 50%;
  transform: translateX(-50%);
  font-family: "FellSC", serif;
  font-size: calc(var(--h) * 0.019);
  letter-spacing: 0.2em;
  padding: 0.35em 1.2em;
  border: 1px solid rgba(242, 234, 214, 0.7);
  background: rgba(20, 15, 10, 0.45);
  white-space: nowrap;
}
.cover-page:hover .cover-start, .cover-page:focus-visible .cover-start { background: rgba(150, 36, 26, 0.75); }

/* 扉（右ページ）と遊び方（左ページ） */
.titlepage {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 9% 12%;
  font-size: calc(var(--h) * 0.0205);
}
.titlepage h1 { margin: 0; font-family: "Maguntia", serif; font-weight: normal; line-height: 1.1; }
.titlepage h1 .t1 { display: block; font-size: 1.65em; }
.titlepage h1 .t2 { display: block; font-size: 1.2em; margin-top: 0.25em; }
.titlepage p { margin: 0; }
.titlepage .orn { font-size: 1.8em; color: var(--red); margin: 0.6em 0; }
.titlepage .being { font-style: italic; line-height: 1.45; max-width: 22em; }
.titlepage .by { margin-top: 1.2em; line-height: 1.45; }
.titlepage .sc { font-family: "FellSC", serif; font-size: 1.3em; letter-spacing: 0.12em; }
.titlepage .anno { margin-top: 1em; font-family: "FellSC", serif; letter-spacing: 0.15em; }
.titlepage .colophon { margin-top: 1.6em; font-size: 0.7em; color: var(--ink-soft); }
.howto h2 { margin: 0.4em 0 0.8em; text-align: center; font-family: "Maguntia", serif; font-weight: normal; font-size: 1.9em; }

/* スマホ・縦長の画面：絵を上、本文を下に */
@media (max-width: 720px), (max-aspect-ratio: 4 / 5) {
  body { display: block; min-height: 0; background: var(--paper); }
  .spread { width: 100%; height: auto; aspect-ratio: auto; flex-direction: column; box-shadow: none; }
  .page { flex: none; }
  .page.left, .page.right { background-image: none; }
  .illust { order: -1; padding: 20px 20px 0; }
  .illust img { max-height: 55svh; }
  .text-page { font-size: 19px; line-height: 1.5; padding: 22px 22px 40px; overflow: visible; text-align: left; }
  .choices a { padding-top: 0.45em; padding-bottom: 0.45em; border-top: 1px solid rgba(150, 36, 26, 0.2); margin: 0; }
  .cover { width: 100%; height: 100svh; aspect-ratio: auto; }
  .cover-page { height: 100%; }
  .cover-title .t1 { font-size: 40px; }
  .cover-title .t2 { font-size: 26px; }
  .cover-sub { top: 24%; font-size: 15px; }
  .cover-author { font-size: 17px; }
  .cover-start { font-size: 14px; }
  .intro .titlepage { order: -1; min-height: 100svh; font-size: 17px; }
}
"""


# ページめくり。選択肢で進むときと、ブラウザの「戻る」や data-dir="back" のリンクで戻るときで、めくる向きを変える。
# 綴じ方向（data-binding）で、進むときにめくれる側が決まる：右綴じ（rtl）は左ページ、左綴じ（ltr）は右ページ。
PAGE_JS = """
(() => {
  const root = document.documentElement;
  const ltr = root.dataset.binding === "ltr";
  const spreads = new Map([...document.querySelectorAll(".spread")].map((s) => [s.id, s]));
  const narrow = matchMedia("(max-width: 720px), (max-aspect-ratio: 4 / 5)");
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  const fromHash = () => spreads.get(decodeURIComponent(location.hash.slice(1))) || spreads.get("cover");

  let current = fromHash();
  current.classList.add("current");
  let index = (history.state && history.state.i) || 0;
  history.replaceState({ i: index }, "");
  history.scrollRestoration = "manual";
  // 進行中のめくりの後片付け。次のめくりを始める前に必ず済ませる。
  let pending = null;
  function settle() {
    if (pending) {
      const p = pending;
      pending = null;
      p();
    }
  }

  function show(next, dir) {
    if (!next || next === current) return;
    settle();
    const old = current;
    current = next;
    next.classList.add("current");
    window.scrollTo(0, 0);
    next.focus({ preventScroll: true });
    if (still.matches) {
      old.classList.remove("current");
    } else if (narrow.matches || old.id === "cover" || next.id === "cover") {
      old.classList.remove("current");
      const dx = (dir === "forward") === ltr ? 48 : -48;
      const slide = next.animate(
        [{ opacity: 0, transform: `translateX(${dx}px)` }, { opacity: 1, transform: "none" }],
        { duration: 380, easing: "cubic-bezier(.2,.7,.3,1)" }
      );
      const stop = () => { slide.cancel(); if (pending === stop) pending = null; };
      pending = stop;
      setTimeout(stop, 450);
    } else {
      flip(old, next, dir);
    }
  }

  function face(page, spread, back) {
    const f = document.createElement("div");
    const kinds = [...spread.classList].filter((c) => !["spread", "current", "leaving"].includes(c));
    f.className = ["face", ...kinds, back ? "back" : ""].join(" ");
    // 余白は % 指定で、基準が見開きの幅。複製では 1 ページ分の幅が基準になってずれるので、実際の値を写す。
    const copy = page.cloneNode(true);
    copy.style.padding = getComputedStyle(page).padding;
    f.append(copy);
    const shade = document.createElement("div");
    shade.className = "shade";
    f.append(shade);
    return f;
  }

  function flip(old, next, dir) {
    const side = (dir === "forward") === ltr ? "right" : "left";
    const other = side === "right" ? "left" : "right";
    const oldPage = old.querySelector(`:scope > .page.${side}`);
    const newPage = next.querySelector(`:scope > .page.${other}`);
    const r = oldPage.getBoundingClientRect();
    const leaf = document.createElement("div");
    leaf.className = "leaf";
    Object.assign(leaf.style, {
      left: r.left + "px", top: r.top + "px", width: r.width + "px", height: r.height + "px",
      transformOrigin: side === "right" ? "left center" : "right center",
    });
    const front = face(oldPage, old, false);
    const back = face(newPage, next, true);
    leaf.append(front, back);
    document.body.append(leaf);
    old.classList.add("leaving");
    oldPage.style.visibility = "hidden";

    const angle = side === "right" ? -180 : 180;
    const opts = { duration: 820, easing: "cubic-bezier(.45,.05,.25,1)", fill: "forwards" };
    const turn = leaf.animate(
      [
        { transform: "perspective(2600px) rotateY(0deg)" },
        { transform: `perspective(2600px) rotateY(${angle / 2}deg) scale(1.02)`, offset: 0.5 },
        { transform: `perspective(2600px) rotateY(${angle}deg)` },
      ],
      opts
    );
    front.querySelector(".shade").animate([{ opacity: 0 }, { opacity: 0.4 }], { ...opts, duration: opts.duration / 2 });
    back.querySelector(".shade").animate([{ opacity: 0.4 }, { opacity: 0.4, offset: 0.5 }, { opacity: 0 }], opts);
    let finished = false;
    const done = () => {
      if (finished) return;
      finished = true;
      leaf.remove();
      oldPage.style.visibility = "";
      old.classList.remove("leaving");
      if (old !== current) old.classList.remove("current");
      if (pending === done) pending = null;
    };
    pending = done;
    turn.onfinish = done;
    // タブが裏にあるとアニメーションが止まることがあるので、時間で必ず片付ける
    setTimeout(done, opts.duration + 150);
  }

  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const next = spreads.get(a.getAttribute("href").slice(1));
    if (!next) return;
    e.preventDefault();
    index += 1;
    history.pushState({ i: index }, "", "#" + next.id);
    show(next, a.dataset.dir === "back" ? "back" : "forward");
  });

  window.addEventListener("popstate", (e) => {
    const i = (e.state && e.state.i) || 0;
    const dir = i < index ? "back" : "forward";
    index = i;
    show(fromHash(), dir);
  });
})();
"""


if __name__ == "__main__":
    args = parse_args("HTML 版を書き出す")
    for src in args.books:
        for lang in args.langs:
            {"ja": build_ja, "en": build_en}[lang](src)
