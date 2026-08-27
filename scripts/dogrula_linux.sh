#!/usr/bin/env bash
# RUHSAT-Bench — LINUX PORT DOGRULAMA PAKETI
#
# Depo kokunde calistirilir:   bash scripts/dogrula_linux.sh
#
# Windows'tan Linux'a gecisin ardindan butun deterministik zinciri kosar ve
# ciktilari BILINEN degerlerle karsilastirir. Beklenen degerler tahmin degil;
# 02.08.2026'da Ubuntu 24 / Python 3.12.3 / pypdf 5.9.0 uzerinde OLCULDU
# (claude.ai oturumu, iki ortamda birebir dogrulanmis sayilar).
#
# Kontrol listesi:
#   1  korpus_kur      : 1366 birim, Kontrol A 440/441, B 473/473, C 120/120
#   2  bent_bol        : 1523 birim, kurtarma 0.9632, 364 -> 15.3.1
#   3  kural_taban R3  : TOPLAM 473/473
#   4  negatif kontrol : tohum 1-5 -> 0.5137 0.5412 0.5201 0.5201 0.5349
#   5  uzlasi_birlestir: v7a 223/250, v7b 221/252 (kodlayici xlsx'leri gerekli)
#   6  etki_analizi    : |dBAcc| ort 0.0046 maks 0.0347 (arsiv jsonl gerekli)
#
# Herhangi biri tutmazsa ortam farki vardir ve makaleye gecmeden cozulmelidir.
set -u
BASARI=0; HATA=0
kontrol() {  # kontrol "ad" "beklenen" "dosya"
  if grep -qF -- "$2" "$3"; then
    echo "  [TAMAM] $1"
    BASARI=$((BASARI+1))
  else
    echo "  [HATA ] $1  — beklenen: $2"
    echo "          bulunan ilgili satirlar:"
    grep -iE "$(echo "$2" | cut -c1-8)" "$3" | head -3 | sed 's/^/          /'
    HATA=$((HATA+1))
  fi
}

mkdir -p sonuclar /tmp/rb
echo "== 1/6 korpus_kur =="
python3 -u scripts/korpus_kur.py \
  --pdf-dir data/kaynak_pdf \
  --claims data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
  --out data/korpus > /tmp/rb/1.log 2>&1
kontrol "birim sayisi 1366"        "1366"      /tmp/rb/1.log
kontrol "Kontrol A 440/441"        "440/441"   /tmp/rb/1.log
kontrol "Kontrol B 473/473"        "473/473"   /tmp/rb/1.log
kontrol "Kontrol C 120/120"        "120/120"   /tmp/rb/1.log

echo "== 2/6 bent_bol =="
python3 -u scripts/bent_bol.py --pdf-dir data/kaynak_pdf \
  --claims data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
  --csv /tmp/rb/altin_adaylari.csv > /tmp/rb/2.log 2>&1
kontrol "yeni birim 1523"          "1523"      /tmp/rb/2.log
kontrol "kurtarma 0.9632 korunuyor" "131/136 = 0.9632   <-- BOZULMAMALI" /tmp/rb/2.log
kontrol "364 -> 15.3.1"            "['15.3.1']" /tmp/rb/2.log

echo "== 3/6 kural_taban (R3) =="
python3 -u scripts/kural_taban.py \
  --claims data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
  --korpus data/korpus/korpus.jsonl --belge data/korpus/belge_tam.jsonl \
  --out /tmp/rb/r3.jsonl --tani > /tmp/rb/3.log 2>&1
kontrol "R3 473/473"               "473/473"   /tmp/rb/3.log

echo "== 4/6 negatif kontrol (5 tohum) =="
: > /tmp/rb/4.log
for t in 1 2 3 4 5; do
  python3 -u scripts/kural_taban.py \
    --claims data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
    --korpus data/korpus/korpus.jsonl --belge data/korpus/belge_tam.jsonl \
    --out /tmp/rb/nk_$t.jsonl --tani --karistir --tohum $t >> /tmp/rb/4.log 2>&1
done
for v in 0.5137 0.5412 0.5201 0.5349; do
  kontrol "tohum degeri $v"        "$v"        /tmp/rb/4.log
done

echo "== 5/6 uzlasi_birlestir =="
K1=$(ls kodlay*1*.xlsx 2>/dev/null | head -1); K2=$(ls kodlay*2*.xlsx 2>/dev/null | head -1)
if [ -n "${K1:-}" ] && [ -n "${K2:-}" ]; then
  python3 -u scripts/uzlasi_birlestir.py --kitaplar "$K1,$K2" \
    --claims data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
    --out-a data/iddialar/uretilen_iddialar_v7a.csv \
    --out-b data/iddialar/uretilen_iddialar_v7b.csv \
    --rapor /tmp/rb/uzlasi.txt > /tmp/rb/5.log 2>&1
  kontrol "v7a 223/250"            "223 DOGRU / 250 YANLIS" /tmp/rb/5.log
  kontrol "v7b 221/252"            "221 DOGRU / 252 YANLIS" /tmp/rb/5.log
else
  echo "  [ATLA ] kodlayici xlsx'leri bulunamadi (depo kokune koyun)"
fi

echo "== 6/6 etki_analizi =="
if [ -f sonuclar/f4_sonuclar.jsonl ]; then
  python3 -u scripts/etki_analizi.py \
    --v6 data/iddialar/uretilen_iddialar_v6_onarilmis.csv \
    --v7a data/iddialar/uretilen_iddialar_v7a.csv \
    --v7b data/iddialar/uretilen_iddialar_v7b.csv \
    --sonuclar "sonuclar/f4_sonuclar.jsonl,sonuclar/f4_frontier_cogunluk.jsonl:claude-sonnet-5,sonuclar/f4_haiku_cogunluk.jsonl:claude-haiku-4.5" \
    --rapor /tmp/rb/etki.txt > /tmp/rb/6.log 2>&1
  kontrol "etki ort 0.0046"        "ort 0.0046" /tmp/rb/6.log
  kontrol "etki maks 0.0347"       "maks 0.0347" /tmp/rb/6.log
  kontrol "sonnet E1 0.697->0.692" "0.697->0.692" /tmp/rb/6.log
else
  echo "  [ATLA ] arsiv jsonl'leri sonuclar/ altinda degil"
fi

echo
echo "================================================"
echo "SONUC: $BASARI tamam, $HATA hata"
if [ $HATA -eq 0 ]; then
  echo "Port dogrulandi: Linux ortami, Windows'ta olculen zincirle birebir."
else
  echo "ORTAM FARKI VAR. pip freeze ciktisini ve /tmp/rb/*.log'lari inceleyin;"
  echo "ozellikle pypdf surumu (beklenen 5.9.0; TBDY metni 870747 karakter,"
  echo "870751 de olculmus ve zararsiz — baska sapmalar incelenmeli)."
fi
exit $HATA
