"""次の本の雛形を books/<名前>/ に作る。

使い方:
    python3 scripts/new_book.py <名前>      # 例: python3 scripts/new_book.py majo-no-tou

型（どの本も同じ）:
    選択の場面が 5 つ。場面ごとに「選択（c）→ 正解の結果（r）／バッドエンド（b）」の 3 パラグラフで、全 15 パラグラフ。
    挿絵は各パラグラフに 1 枚と表紙の 16 枚。パラグラフ番号・kind・飛び先は下の SCENES で固定。
    5 つめの場面の正解（r）はエンディング。

作るもの:
    story.toml      日本語版。[book] と 15 パラグラフ。書名・本文・選択肢の文言は空欄
    story.en.toml   英語版。同じ構成で空欄
    prompts.md      挿絵のプロンプト集。[Style] [Tone] [Frame] などは 1 冊目と同じ。[Hero] [Item] と場面は空欄
    images/raw/     生成した挿絵の置き場所（git には入れない）

<名前> は日本語版の書き出し名（slug_ja）にもなる。英語版の名前（slug_en）は story.toml に書き足す。
"""

import re
import sys

from books import BOOKS_DIR, ROOT, all_books

# (場面, 選択の番号, 正解の番号, バッドエンドの番号, 選択肢の並び（正解が先なら True）)
SCENES = [
    (1, 1, 7, 12, True),
    (2, 4, 10, 14, False),
    (3, 9, 2, 13, False),
    (4, 6, 11, 3, False),
    (5, 15, 8, 5, False),
]

# 挿絵の Item（前／後）。2 つめの場面の正解で姿が変わる（1 冊目の剣と同じ流れ）。合わなければ prompts.md の表を書き換える。
ITEMS = {"00_cover": "after", "01c": "before", "01r": "before", "01b": "なし",
         "02c": "before", "02r": "after（手に持つ）", "02b": "before"}


def paragraphs():
    """15 パラグラフを、本の中の並び（場面ごとに c, r, b）で返す。"""
    out = []
    for i, (scene, c, r, b, correct_first) in enumerate(SCENES):
        last = i == len(SCENES) - 1
        nxt = None if last else SCENES[i + 1][1]
        choices = [r, b] if correct_first else [b, r]
        out.append({"number": c, "key": f"0{scene}c_choice", "kind": "choice", "choices": choices})
        out.append({"number": r, "key": f"0{scene}r_{'ending' if last else 'result'}", "kind": "ending" if last else "result",
                    "choices": [] if last else [nxt]})
        out.append({"number": b, "key": f"0{scene}b_bad", "kind": "bad", "back": c})
    return out


def toml_paragraph(p):
    lines = ["[[paragraph]]", f"number = {p['number']}", f'key = "{p["key"]}"', f'kind = "{p["kind"]}"',
             f'image = "{p["key"]}_v1"']
    if p["kind"] == "bad":
        lines.append(f"back = {p['back']}")
    lines += ['text = """', '"""']
    if p.get("choices"):
        lines.append("choices = [")
        lines += [f'  {{ label = "", to = {to} }},' for to in p["choices"]]
        lines.append("]")
    return "\n".join(lines)


def story_ja(name, author):
    body = "\n\n".join(toml_paragraph(p) for p in paragraphs())
    return f'''# 『』本文データ
#
# kind:
#   choice = 選択の場面（choices に 2 つの選択肢）
#   result = 正解の結果の場面（choices に「次へ」1 つ）
#   bad    = バッドエンド（back に戻り先の番号）
#   ending = エンディング
# number はパラグラフ番号。本の中ではこの番号で飛ぶ。1 が最初の場面。
# number・kind・choices の to・back は型どおりなので変えない。
# image は images/raw/ の画像名（拡張子なし）。key と合わせて、場面の中身がわかる名前に変えてよい（prompts.md も合わせる）。
# text は空行で段落を分ける。数字は漢数字で書く。

[book]
# 書き出すファイルと公開 URL の名前（英数字）。日本語版は dist/<slug_ja>.*、英語版は dist/<slug_en>.*
slug_ja = "{name}"
slug_en = ""
title = ""
subtitle = "君が主人公になるアドベンチャーゲームブック"
author = "{author.get("author", "")}"
author_file_as = "{author.get("author_file_as", "")}"      # 著者名の読み（電子書籍の並べ替え用）
author_en = "{author.get("author_en", "")}"            # 英語での著者名（日本語版 EPUB の別言語表記）
author_en_file_as = "{author.get("author_en_file_as", "")}"   # 英語版での並べ替え用（英語版 EPUB の別言語表記は author）
year = ""
cover_image = "00_cover_v1"
# 入口ページ（site/index.html）の紹介文
lead = ""
how_to_play = """
この本では、君が主人公だ。

場面の終わりには、いくつかの選択肢が出てくる。どれか一つを選んで、示された番号の場面へ進んでほしい。

道を誤ると、冒険はそこで終わってしまうこともある。そのときは「やり直す」を選べば、迷った場面へ戻ることができる。

それでは、冒険を始めよう。
"""

{body}
'''


def story_en(author):
    body = "\n\n".join(toml_paragraph(p) for p in paragraphs())
    return f'''# Early Modern English flavor
#
# Same structure as story.toml (numbers, kinds, images, links).
# Choice labels are completed as "<label>, turn to <n>."
# Mood over correctness: modern spelling, archaic grammar where it sounds good.

[book]
title_main = ""
title_sub = ""
subtitle = "A Gamebook wherein Thou Art the Hero"
title_page_text = ""
author = "{author.get("author_en", "")}"
year = ""
copyright = ""
cover_image = "00_cover_v1"
how_to_play = """
In this book, thou art the hero.

At the close of each passage thou shalt be offered a choice. Choose but one, and turn to the passage whose number is shown.

Shouldst thou choose amiss, thine adventure may come to an untimely end. Fear not: take heart, and thou mayest return to the place where thou didst stray.

Now let thine adventure begin.
"""

{body}
'''


def prompts(name):
    rows = []
    sections = []
    for p in [{"key": "00_cover"}] + paragraphs():
        key = p["key"]
        cover = key == "00_cover"
        item = ITEMS.get(key[:3], "after") if not cover else ITEMS["00_cover"]
        tone = "なし（Cover Style）" if cover else "bad ending" if p["kind"] == "bad" else "story"
        label = "表紙" if cover else f"場面{key[1]}：" + {"choice": "選択", "result": "正解", "ending": "正解（エンディング）", "bad": "バッドエンド"}[p["kind"]]
        rows.append(f"| {key} | {label} | {item} | {tone} | 未作成 |")
        item_part = f" + [Item: {item.split('（')[0]}]" if item.startswith(("before", "after")) else ""
        recipe = (f"[Cover Style] + [Hero]{item_part} + 以下 + [Cover Frame]" if cover
                  else f"[Style] + [Hero]{item_part} + [Tone: {tone}] + 以下 + [Frame]")
        sections.append(f"""### {key}　{label}

{recipe}

```text
[Scene]

[Composition]
```
""")
    return f"""# 『』画像プロンプト集

## 組み立て方

1枚のプロンプトは、次のブロックを上から順につなげて作ります。

```
[Style] + [Hero] + [Item] + [Tone] + [Scene] + [Composition] + [Frame]
```

- [Style] [Hero] [Frame] は全ページ共通です。一字一句変えずに使います。
- [Item] と [Tone] は、場面ごとに指定された方を選びます。[Item] は物語の途中で姿が変わる主人公の持ち物です。
- [Scene] と [Composition] は場面ごとに書き換えます。
- 表紙だけはカラーなので、[Style] の代わりに [Cover Style] を使います。
- 保存先は `books/{name}/images/raw/<ファイル名>_v1.png` です。候補が複数あるときは `_v2`、`_v3` と番号を増やします。
- 下の表の Item 列が before / after で始まる場面に [Item: before] / [Item: after] を付けます（「なし」なら付けない）。

## 共通ブロック

### [Style]（表紙以外）

```text
[Style]
Black-and-white copperplate engraving, in the manner of 19th-century book illustrations such as Gustave Doré.
Fine-line cross-hatching and stippling, pure black ink on white paper.
Every tone, including mist, fog and beams of light, is rendered only with fine engraved lines and dots.
No color, no gray wash, no airbrushed or photographic shading, no soft gradients. High contrast.
No text, no letters, no signature, no frame or border.
```

### [Cover Style]（表紙のみ）

```text
[Cover Style]
A painted cover for a classic 1980s fantasy adventure gamebook paperback.
Rich color, gouache and oil painting look, dramatic lighting, heroic and serious mood.
No text, no letters, no title, no signature, no frame or border.
```

### [Hero]

```text
[Hero]
```

### [Item]（どちらか1つ）

before は、物語の前半（姿が変わる前）で使います。

```text
[Item: before]
```

after は、姿が変わった後と表紙で使います。

```text
[Item: after]
```

### [Tone]（どちらか1つ。表紙には付けない）

```text
[Tone: story]
Light and airy overall, with generous white areas.
```

```text
[Tone: bad ending]
Darker and denser, with deep shadows, drawn completely seriously like a tragic scene in an old book. Not cartoonish, not cute.
```

### [Frame]

```text
[Frame]
Vertical portrait composition for a book page.
Open white space around the edges so the image sits on the page like a printed vignette.
```

表紙だけは [Frame] の代わりに [Cover Frame] を使います。

```text
[Cover Frame]
Vertical portrait composition for a book cover, painted all the way to the edges with no white margin.
```

## 場面ごとのブロック

| ファイル名 | 場面 | Item | Tone | 状態 |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

{chr(10).join(sections)}"""


def main():
    if len(sys.argv) != 2:
        sys.exit("使い方: python3 scripts/new_book.py <名前>")
    name = sys.argv[1]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        sys.exit(f"名前は英小文字・数字・ハイフンにしてください（URL になります）: {name}")
    target = BOOKS_DIR / name
    if target.exists():
        sys.exit(f"もうあります: {target.relative_to(ROOT)}")
    taken = {s for b in all_books() for s in (b.slug_ja, b.slug_en)}
    if name in taken:
        sys.exit(f"ほかの本の書き出し名と重なります: {name}")

    # 著者まわりは、既にある本から引き継ぐ（同じ著者で続けて作るため）
    existing = all_books()
    keys = ("author", "author_file_as", "author_en", "author_en_file_as")
    author = {k: existing[0].info.get(k, "") for k in keys} if existing else {}

    (target / "images" / "raw").mkdir(parents=True)
    (target / "story.toml").write_text(story_ja(name, author), encoding="utf-8")
    (target / "story.en.toml").write_text(story_en(author), encoding="utf-8")
    (target / "prompts.md").write_text(prompts(name), encoding="utf-8")
    print(f"{target.relative_to(ROOT)}/ を作りました。story.toml の slug_en・書名・本文と、prompts.md を埋めてください。")


if __name__ == "__main__":
    main()
