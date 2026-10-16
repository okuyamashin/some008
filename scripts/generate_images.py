"""prompts/image_prompts.md から各場面のプロンプトを組み立て、OpenAI で画像を生成する。

使い方:
    python3 scripts/generate_images.py                # 未作成の場面をすべて生成
    python3 scripts/generate_images.py 01c_village_request 05b_lair_tavern
    python3 scripts/generate_images.py --dry-run 00_cover   # プロンプトを表示するだけ

生成した画像は images/raw/<名前>_v<番号>.png に保存する。既存の番号は上書きせず、次の番号で保存する。
引数なしのときは、v1 がまだない場面だけを生成する。
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts" / "image_prompts.md"
RAW_DIR = ROOT / "images" / "raw"

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
    """共通ブロック、場面ごとのブロック、場面ごとの Sword / Tone を読み取る。"""
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
    for row in re.finditer(r"^\| (\d\d\w_\w+|00_cover) \| [^|]+ \| ([^|]+) \| ([^|]+) \|", text, re.M):
        name, sword, tone = row.group(1), row.group(2).strip(), row.group(3).strip()
        sword_key = "[Sword: holy]" if sword.startswith("holy") else "[Sword: rusty]" if sword.startswith("rusty") else None
        tone_key = "[Tone: story]" if tone == "story" else "[Tone: bad ending]" if tone == "bad ending" else None
        settings[name] = (sword_key, tone_key)
    return common, scenes, settings


def build_prompt(name, common, scenes, settings):
    sword_key, tone_key = settings[name]
    is_cover = name == "00_cover"
    keys = ["[Cover Style]" if is_cover else "[Style]", "[Hero]", sword_key, tone_key]
    parts = [common[k] for k in keys if k]
    parts.append(scenes[name])
    parts.append(common["[Cover Frame]" if is_cover else "[Frame]"])
    return "\n\n".join(parts)


def next_path(name):
    n = 1
    while (RAW_DIR / f"{name}_v{n}.png").exists():
        n += 1
    return RAW_DIR / f"{name}_v{n}.png"


def generate(name, prompt, api_key):
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
    path = next_path(name)
    path.write_bytes(base64.b64decode(data["data"][0]["b64_json"]))
    return f"{name}: {path.relative_to(ROOT)}"


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    names = [a for a in args if a != "--dry-run"]

    common, scenes, settings = parse_prompts(PROMPTS.read_text(encoding="utf-8"))
    if not names:
        names = [n for n in settings if not (RAW_DIR / f"{n}_v1.png").exists()]
    unknown = [n for n in names if n not in settings or n not in scenes]
    if unknown:
        sys.exit(f"プロンプト集にない場面です: {', '.join(unknown)}")

    if dry_run:
        for n in names:
            print(f"===== {n} =====\n{build_prompt(n, common, scenes, settings)}\n")
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    print(f"{MODEL} / {SIZE} / {QUALITY} で {len(names)} 枚生成します: {', '.join(names)}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for result in pool.map(lambda n: generate(n, build_prompt(n, common, scenes, settings), api_key), names):
            print(result, flush=True)


if __name__ == "__main__":
    main()
