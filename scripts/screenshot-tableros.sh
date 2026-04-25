#!/usr/bin/env bash
# Genera capturas de los tableros listados en scripts/tableros.tsv
# Formato TSV: <slug>\t<url>
# Salida: img/tableros/<slug>.png

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/scripts/tableros.tsv"
OUT_DIR="$ROOT/img/tableros"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WIDTH=1400
HEIGHT=900
WAIT_MS=10000

mkdir -p "$OUT_DIR"

while IFS=$'\t' read -r slug url; do
  [[ -z "${slug// }" || "$slug" == \#* ]] && continue
  out="$OUT_DIR/$slug.png"
  echo "→ $slug  ($url)"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --virtual-time-budget="$WAIT_MS" \
    --window-size="$WIDTH,$HEIGHT" \
    --screenshot="$out" \
    "$url" 2>/dev/null
done < "$MANIFEST"

echo "✔ Capturas generadas en $OUT_DIR"
