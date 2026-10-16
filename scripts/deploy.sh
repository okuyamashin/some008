#!/bin/sh
# gamebook.engawa5656.com に公開する。
#
# 使い方:
#   python3 scripts/build_html.py && build/.venv/bin/python scripts/build_pdf.py && python3 scripts/build_epub.py
#   python3 scripts/build_index.py
#   sh scripts/deploy.sh                       # books/ 以下の全巻
#   sh scripts/deploy.sh --book ryu-no-meikyu  # 1 冊だけ（入口ページはいつも全巻分を上げる）
#
# 置き場所:
#   /index.html                     入口ページ（dist/index.html。型は site/index.html）
#   /assets/<slug_ja>.webp          入口ページの表紙
#   /library/*.html, *.pdf, *.epub  書き出した本（dist/）。名前は story.toml の slug_ja / slug_en
set -eu

BUCKET=gamebook.engawa5656.com
DISTRIBUTION_ID=${DISTRIBUTION_ID:-E1P47C37OV1I3G}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

# 版ごとに「言語<TAB>英数字の名前<TAB>書名」（scripts/books.py が story.toml から読む）
EDITIONS=$(python3 scripts/books.py "$@")
# 入口ページはいつも全巻を載せるので、表紙も全巻分を上げる
COVERS=$(python3 scripts/books.py | awk -F '\t' '$1 == "ja" { print $2 }')

TAB=$(printf '\t')
for f in dist/index.html $(for slug in $COVERS; do echo "dist/assets/$slug.webp"; done); do
  [ -f "$f" ] || { echo "見つかりません: $f（先に python3 scripts/build_index.py を実行してください）" >&2; exit 1; }
done

echo "$EDITIONS" | while IFS="$TAB" read -r lang name title; do
  for ext in html pdf epub; do
    [ -f "dist/$name.$ext" ] || { echo "見つかりません: dist/$name.$ext（先にビルドしてください）" >&2; exit 1; }
  done
done

put() { # put <ローカルのファイル> <S3 のキー> <Content-Type> <Cache-Control> [Content-Disposition]
  if [ $# -ge 5 ]; then
    aws s3 cp "$1" "s3://$BUCKET/$2" --content-type "$3" --cache-control "$4" --content-disposition "$5" --only-show-errors
  else
    aws s3 cp "$1" "s3://$BUCKET/$2" --content-type "$3" --cache-control "$4" --only-show-errors
  fi
  echo "  $2"
}

# ダウンロードしたときのファイル名を本のタイトルにする（Send to Kindle などはファイル名をタイトルに使うことがある）。
# URL は英数字のまま。disposition <inline|attachment> <英数字の名前> <タイトルの名前>
disposition() {
  python3 -c "import sys, urllib.parse; print(f\"{sys.argv[1]}; filename=\\\"{sys.argv[2]}\\\"; filename*=UTF-8''{urllib.parse.quote(sys.argv[3])}\")" "$1" "$2" "$3"
}

echo "アップロード:"
put dist/index.html index.html "text/html; charset=utf-8" "public, max-age=300"
for slug in $COVERS; do
  put "dist/assets/$slug.webp" "assets/$slug.webp" "image/webp" "public, max-age=86400"
done
echo "$EDITIONS" | while IFS="$TAB" read -r lang name title; do
  put "dist/$name.html" "library/$name.html" "text/html; charset=utf-8" "public, max-age=300"
  put "dist/$name.pdf" "library/$name.pdf" "application/pdf" "public, max-age=3600" \
    "$(disposition inline "$name.pdf" "$title.pdf")"
  put "dist/$name.epub" "library/$name.epub" "application/epub+zip" "public, max-age=3600" \
    "$(disposition attachment "$name.epub" "$title.epub")"
done

echo "CloudFront のキャッシュを消去:"
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths "/*" --query Invalidation.Id --output text
echo "https://$BUCKET/"
