#!/usr/bin/env bash
# F5 URETIM KOSUSU — birincil korpus (EK-6: korpus_v2 + v7a)
# Kutuk #29 geregi 3 TEKRAR (dayanakli kollar deterministik DEGIL).
# Kutuk #28 geregi yalniz 27B+ modeller (3B bicim talimatini birakiyor).
set -u
cd /workspace/ruhsat-bench
source env.sh
mkdir -p sonuclar/f5
echo "=== BASLADI $(date -u +%FT%TZ) ==="
# R3bm25 modelden BAGIMSIZ — bir kez kosulur
python -u scripts/f4_dayanak.py --kol R3bm25 --korpus data/korpus_v2/korpus.jsonl \
  --out sonuclar/f5/r3bm25.jsonl 2>&1 | tail -6
for m in qwen2.5:32b-instruct gemma3:27b; do
  ad=$(echo "$m" | tr ':/.' '___')
  for k in 1 2 3; do
    echo "=== $m tekrar $k  $(date -u +%FT%TZ) ==="
    python -u scripts/f4_dayanak.py --kol R1 R2 --kosul E1 E2 --models "$m" \
      --korpus data/korpus_v2/korpus.jsonl --max-token 128 \
      --out "sonuclar/f5/${ad}_k${k}.jsonl" 2>&1 | tail -12
  done
done
echo "=== BITTI $(date -u +%FT%TZ) ==="
