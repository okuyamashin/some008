"""サイト共通のアイコン（ファビコン）と、SNS でリンクを共有したときの画像（OGP 画像）を書き出す。

使い方:
    build/.venv/bin/python scripts/build_brand.py

準備（初回だけ）:
    build/.venv/bin/pip install pillow
    元のアイコン画像 site/brand/raw/icon_v1.png を用意する（下の ICON_PROMPT で生成したもの。git には入れない）。

書き出すもの（site/brand/。deploy.sh がサイトの一番上に置く）:
    favicon.ico           ブラウザのタブ用（16・32・48px）
    apple-touch-icon.png  スマホのホーム画面用（180px）
    icon-512.png          大きめのアイコン
    og.png                Twitter（X）や Facebook でリンクを共有したときの画像（1200×630px）
"""

import base64
import subprocess
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pdf import CHROME  # noqa: E402
from books import ROOT  # noqa: E402

BRAND = ROOT / "site" / "brand"
SOURCE = BRAND / "raw" / "icon_v1.png"
PAPER = (243, 236, 218)

# 元のアイコンを生成したときのプロンプト（1024×1024、chatgpt-image-latest）
ICON_PROMPT = """A simple, bold emblem icon for a fantasy adventure gamebook website favicon.
An open book seen from the front, with a straight sword standing upright in the center of its pages, the blade pointing up.
Woodcut-inspired style with thick, clean lines and solid shapes, no fine hatching, no small details.
Only two colors: deep brick red (#8b2a1c) for the book and sword, on a flat warm parchment background (#f3ecda).
Centered, filling about 80% of the square, with even margins.
Must remain clearly readable when shrunk to 16×16 pixels.
No text, no letters, no gradients, no shadows, no border, no frame.
Square 1:1."""


def tight_square(img, pad=0.06):
    """絵のまわりの余白を詰めた正方形にする。小さく表示したときに絵が大きく見えるように。"""
    rgb = img.convert("RGB")
    # 紙の色から離れた画素だけを「絵」とみなす
    mask = Image.eval(rgb.convert("L"), lambda v: 255 if v < 200 else 0)
    left, top, right, bottom = mask.getbbox()
    side = max(right - left, bottom - top)
    side = int(side * (1 + pad * 2))
    cx, cy = (left + right) // 2, (top + bottom) // 2
    square = Image.new("RGB", (side, side), PAPER)
    square.paste(rgb.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)), (0, 0))
    return square


def og_image(icon):
    """OGP 画像。入口ページと同じ暗い机の色に、アイコンとサイト名を置く。Chrome で撮影する。"""
    buf = BytesIO()
    icon.resize((512, 512), Image.LANCZOS).save(buf, "PNG")
    icon_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    page = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><style>
html, body {{ margin: 0; }}
body {{
  width: 1200px; height: 630px; overflow: hidden;
  display: flex; align-items: center; gap: 64px; padding: 0 80px; box-sizing: border-box;
  background: radial-gradient(ellipse at 30% 40%, #3a332d 0%, #191513 80%);
  color: #f3ecda;
  font-family: "Hiragino Mincho ProN", "Yu Mincho", serif;
}}
.icon {{ width: 340px; height: 340px; border-radius: 28px; box-shadow: 0 18px 40px rgba(0,0,0,.55); flex: none; }}
.eyebrow {{ margin: 0; font-size: 22px; letter-spacing: .35em; color: #cdbfa8; }}
h1 {{ margin: 14px 0 18px; font-size: 64px; line-height: 1.2; letter-spacing: .08em; font-weight: 700; }}
.lead {{ margin: 0; font-size: 28px; line-height: 1.6; color: #e6dcc6; }}
.en {{ margin: 22px 0 0; font-size: 22px; font-style: italic; color: #cdbfa8; }}
.url {{ margin: 30px 0 0; font-size: 20px; letter-spacing: .08em; color: #b6432f; }}
</style></head><body>
<img class="icon" src="{icon_uri}" alt="">
<div>
  <p class="eyebrow">ADVENTURE GAMEBOOKS</p>
  <h1>アドベンチャー<br>ゲームブック</h1>
  <p class="lead">君が主人公になる、剣と魔法の短い冒険。</p>
  <p class="en">Gamebooks wherein Thou Art the Hero</p>
  <p class="url">gamebook.engawa5656.com</p>
</div>
</body></html>
"""
    html_path = ROOT / "build" / "og.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(page, encoding="utf-8")
    out = BRAND / "og.png"
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630",
         f"--screenshot={out}", html_path.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def main():
    if not SOURCE.exists():
        sys.exit(f"{SOURCE.relative_to(ROOT)} がありません。ICON_PROMPT で 1024×1024 の画像を生成して置いてください")
    BRAND.mkdir(parents=True, exist_ok=True)
    icon = Image.open(SOURCE).convert("RGB")
    small = tight_square(icon)

    small.save(BRAND / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    small.resize((180, 180), Image.LANCZOS).save(BRAND / "apple-touch-icon.png", optimize=True)
    icon.resize((512, 512), Image.LANCZOS).save(BRAND / "icon-512.png", optimize=True)
    og = og_image(icon)
    for name in ("favicon.ico", "apple-touch-icon.png", "icon-512.png", og.name):
        print(f"site/brand/{name} ({(BRAND / name).stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
