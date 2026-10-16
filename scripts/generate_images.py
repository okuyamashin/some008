"""books/<名前>/prompts.md から各場面のプロンプトを組み立て、OpenAI で画像を生成する。

使い方:
    python3 scripts/generate_images.py                # 全巻の未作成の場面をすべて生成
    python3 scripts/generate_images.py --book ryu-no-meikyu
    python3 scripts/generate_images.py --book ryu-no-meikyu 01c_village_request 05b_lair_tavern
    python3 scripts/generate_images.py --book ryu-no-meikyu --dry-run 00_cover   # プロンプトを表示するだけ

生成した画像は books/<名前>/images/raw/<場面>_v<番号>.png に保存する。既存の番号は上書きせず、次の番号で保存する。
場面を指定しないときは、v1 がまだない場面だけを生成する。場面を指定するときは --book で本を 1 冊に絞る。
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from books import ROOT, Book, all_books

MODEL = os.environ.get("IMAGE_MODEL", "chatgpt-image-latest")
SIZE = os.environ.get("IMAGE_SIZE", "1024x1536")
QUALITY = os.environ.get("IMAGE_QUALITY", "high")
WORKERS = int(os.environ.get("IMAGE_WORKERS", "4"))


def load_api_key():
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("OPENAI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("OPENAI_API_KEY が .env にも環境変数にもありません")


def parse_prompts(text):
    """共通ブロック、場面ごとのブロック、場面ごとの Item / Tone を読み取る。

    Item は物語の途中で姿が変わる主人公の持ち物（1 冊目なら剣）。表の Item 列が before / after で始まれば
    [Item: before] / [Item: after] を、それ以外（「なし」など）なら何も付けない。
    """
    common = {}
    scenes = {}
    current_scene = None
    for match in re.finditer(r"^### (\S+).*?$|```text\n(.*?)```", text, re.S | re.M):
        if match.group(1):
            current_scene = match.group(1)
            continue
        block = match.group(2).strip()
        label = block.splitlines()[0].strip()
        if label == "[Scene]":
            scenes[current_scene] = block
        else:
            common[label] = block

    settings = {}
    for row in re.finditer(r"^\| (\d\d\w*_\w+) \| [^|]+ \| ([^|]+) \| ([^|]+) \|", text, re.M):
        name, item, tone = row.group(1), row.group(2).strip(), row.group(3).strip()
        item_key = "[Item: after]" if item.startswith("after") else "[Item: before]" if item.startswith("before") else None
        tone_key = "[Tone: story]" if tone == "story" else "[Tone: bad ending]" if tone == "bad ending" else None
        settings[name] = (item_key, tone_key)
    return common, scenes, settings


def build_prompt(name, common, scenes, settings):
    item_key, tone_key = settings[name]
    is_cover = name == "00_cover"
    keys = ["[Cover Style]" if is_cover else "[Style]", "[Hero]", item_key, tone_key]
    parts = [common[k] for k in keys if k]
    parts.append(scenes[name])
    parts.append(common["[Cover Frame]" if is_cover else "[Frame]"])
    return "\n\n".join(parts)


def next_path(raw_dir, name):
    n = 1
    while (raw_dir / f"{name}_v{n}.png").exists():
        n += 1
    return raw_dir / f"{name}_v{n}.png"


def generate(raw_dir, name, prompt, api_key):
    body = json.dumps({"model": MODEL, "prompt": prompt, "size": SIZE, "quality": QUALITY, "n": 1}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as res:
            data = json.load(res)
    except urllib.error.HTTPError as e:
        return f"{name}: 失敗 {e.code} {e.read().decode(errors='replace')[:300]}"
    path = next_path(raw_dir, name)
    path.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
    return f"{name}: {path.relative_to(ROOT)}"


def run(book, names, dry_run):
    common, scenes, settings = parse_prompts(book.prompts_path.read_text(encoding="utf-8"))
    if not names:
        names = [n for n in settings if not (book.raw_dir / f"{n}_v1.png").exists()]
    unknown = [n for n in names if n not in settings or n not in scenes]
    if unknown:
        sys.exit(f"{book.prompts_path.relative_to(ROOT)} にない場面です: {', '.join(unknown)}")
    if not names:
        return

    if dry_run:
        for n in names:
            print(f"===== {book.name}/{n} =====\n{build_prompt(n, common, scenes, settings)}\n")
        return

    book.raw_dir.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print(f"{book.name}: {MODEL} / {SIZE} / {QUALITY} で {len(names)} 枚生成します: {', '.join(names)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        prompts = [(n, build_prompt(n, common, scenes, settings)) for n in names]
        for result in pool.map(lambda np: generate(book.raw_dir, *np, api_key), prompts):
            print(result, flush=True)


def main():
    parser = argparse.ArgumentParser(description="挿絵を生成する")
    parser.add_argument("--book", action="append", metavar="名前", help="books/ の下の本の名前。省略時は全巻")
    parser.add_argument("--dry-run", action="store_true", help="プロンプトを表示するだけ")
    parser.add_argument("names", nargs="*", metavar="場面", help="場面の名前（例: 00_cover）。省略時は未作成の場面すべて")
    args = parser.parse_args()
    books = [Book(n) for n in args.book] if args.book else all_books()
    if args.names and len(books) != 1:
        parser.error("場面を指定するときは --book で本を 1 冊に絞ってください")
    for book in books:
        run(book, args.names, args.dry_run)


if __name__ == "__main__":
    main()
