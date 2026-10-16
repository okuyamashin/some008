#!/bin/sh
# gamebook.engawa5656.com に公開する。
#
# 使い方:
#   python3 scripts/build_html.py && build/.venv/bin/python scripts/build_pdf.py && python3 scripts/build_epub.py
#   sh scripts/deploy.sh
#
# 置き場所:
#   /index.html                     入口ページ（site/index.html）
#   /assets/cover.webp              入口ページの表紙
#   /library/*.html, *.pdf, *.epub  書き出した本（dist/）
set -eu

BUCKET=gamebook.engawa5656.com
DISTRIBUTION_ID=${DISTRIBUTION_ID:-E1P47C37OV1I3G}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

for f in dist/ryu-no-meikyu.html dist/ryu-no-meikyu.pdf dist/ryu-no-meikyu.epub \
         dist/dragons-labyrinth.html dist/dragons-labyrinth.pdf dist/dragons-labyrinth.epub build/images/00_cover_v1.webp; do
  [ -f "$f" ] || { echo "見つかりません: $f（先にビルドしてください）" >&2; exit 1; }
done

put() { # put <ローカルのファイル> <S3 のキー> <Content-Type> <Cache-Control>
  aws s3 cp "$1" "s3://$BUCKET/$2" --content-type "$3" --cache-control "$4" --only-show-errors
  echo "  $2"
}

echo "アップロード:"
put site/index.html index.html "text/html; charset=utf-8" "public, max-age=300"
put build/images/00_cover_v1.webp assets/cover.webp "image/webp" "public, max-age=86400"
for name in ryu-no-meikyu dragons-labyrinth; do
  put "dist/$name.html" "library/$name.html" "text/html; charset=utf-8" "public, max-age=300"
  put "dist/$name.pdf" "library/$name.pdf" "application/pdf" "public, max-age=3600"
  put "dist/$name.epub" "library/$name.epub" "application/epub+zip" "public, max-age=3600"
done

echo "CloudFront のキャッシュを消去:"
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths "/*" --query Invalidation.Id --output text
echo "https://$BUCKET/"
