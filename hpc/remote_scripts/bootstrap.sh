#!/usr/bin/env bash
# hpc/remote_scripts/bootstrap.sh — konteyner kurulumu. [KONTEYNERDE ÇALIŞIR]
#
# YENİDEN ÇALIŞTIRILABİLİR (idempotent): konteyner yeniden başlarsa tekrar koştur.
#
# TASARIM KARARLARI ve gerekçeleri:
#
# 1) HER ŞEY /workspace ALTINDA. Konteynerin kök dosya sistemi OVERLAY'dir; JupyterHub
#    idle-culler sunucuyu durdurunca yazılabilir overlay katmanı gider. /workspace ise
#    ayrı bir ext4 blok cihazdır (MarkLLM oturumunda ölçüldü: 478 GB boş, 326 MB/s).
#    Ollama modelleri varsayılan olarak ~/.ollama'ya, yani OVERLAY'e inerdi ->
#    18 modelin tamamı her yeniden başlatmada uçardı. OLLAMA_MODELS bu yüzden ZORUNLU.
#
# 2) TEMİZ venv (--system-site-packages DEĞİL). MarkLLM'de tersi yapılmıştı çünkü orada
#    sistemdeki torch 2.10.0+cu128 sürücüyle eşleşiyordu ve korunması gerekiyordu.
#    Burada torch yok; bağımlılık listesi dört saf-python paketi. Buna karşılık
#    pypdf sürümü BİLİMSEL OLARAK BAĞLAYICI: kusur kütüğü #5, iki pypdf sürümünün
#    TBDY metninde 870747 / 870751 karakter farkı ürettiğini ölçmüş. Sistem paketleri
#    pinleri gölgeleyebileceği için temiz venv seçildi.
#
# 3) requirements.txt DEĞİŞTİRİLMEZ. GECIS_LINUX.md 2.6: "sürümler SABİT, pypdf'i
#    serbest bırakmayın". Taşıma katmanının kendi bağımlılıkları (websocket-client,
#    python-dotenv) YEREL tarafta çalışır ve hpc/requirements-hpc.txt'de durur —
#    bilimsel pin listesine karıştırılmaz.
#
# 4) KABUL KAPISI scripts/dogrula_linux.sh'tir. Bu betik kurulumu bitirir ve kapıyı
#    KOŞMAZ; kapıyı deploy.py çağırır, çünkü 17/17 görülmeden hiçbir yeni koşu
#    başlatılmamalıdır (GECIS_LINUX.md §5).
#
#   bash hpc/remote_scripts/bootstrap.sh
set -euo pipefail

WS=/workspace
REPO="$WS/ruhsat-bench"

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- 1. dizinler + ortam
say "1/5  kalıcı dizinler ve ortam değişkenleri"
mkdir -p "$WS"/{logs,ollama} "$REPO"
# ⚠ /workspace/env.sh'e YAZMIYORUZ. O dosya MarkLLM'in (2026-08-19) ve ~/.bashrc onu
#   source ediyor; uzerine yazmak HF_HOME, TRANSFORMERS_CACHE ve PYTHONPATH'ini
#   silerdi -- yani PAYLASILAN konteynerdeki DIGER projeyi bozardik. Olculdu:
#   deploy oncesi `ls /workspace` env.sh'i 19 Ağu tarihli buldu. Kendi ortamimiz
#   depo altinda yasar; MarkLLM'in dosyasina ve ~/.bashrc satirina DOKUNULMAZ.
cat > "$REPO/env.sh" <<'EOF'
# /workspace/ruhsat-bench/env.sh — bu depo icin ortam. bootstrap.sh uretir.
# TEK KAYNAK DOGRULUK: yol sabitleri buradan okunur, betiklere gomulmez.
# MarkLLM'in /workspace/env.sh'inden AYRIDIR ve onu ezmez; ikisi yan yana yasar.
export OLLAMA_MODELS=/workspace/ollama/models   # overlay DEGIL: yeniden baslatmada korunur
export OLLAMA_HOST=127.0.0.1:11434              # localhost DEGIL (ORTAM.md 2.1: x4.2 yavaslama)
export PATH=/workspace/ollama/bin:/workspace/ruhsat-bench/.venv/bin:$PATH
export PYTHONUNBUFFERED=1
EOF
# shellcheck disable=SC1091
source "$REPO/env.sh"
echo "  ortam dosyasi: $REPO/env.sh  (MarkLLM'in /workspace/env.sh'i KORUNDU)"
echo "  OLLAMA_MODELS=$OLLAMA_MODELS  (overlay DEGIL)"

# ---------------------------------------------------------------- 2. disk
say "2/5  disk (mount seçeneklerinde usrquota,grpquota var; değer okunamıyor)"
df -h "$WS" | tail -1 | awk '{print "  dosya sistemi: "$2" toplam, "$4" boş, %"$5" dolu"}'
if command -v quota >/dev/null 2>&1; then quota -s 2>&1 | head -4 | sed 's/^/  /'
else echo "  quota komutu yok -> kota SINIRI OKUNAMIYOR; gerçek tüketim izlenerek ölçülecek"; fi
du -sh "$REPO" 2>/dev/null | awk '{print "  depo şu an: "$1}'

# ---------------------------------------------------------------- 3. venv
say "3/5  sanal ortam (TEMİZ; pinler gölgelenmesin)"
# SİSTEM python'u MUTLAK yolla sabitlenir. env.sh PATH'in başına venv/bin koyuyor;
# o dizin silindikten sonra kabuk `python3`ü ÖNBELLEKTEN eski yolda arayıp rc=127
# veriyordu (MarkLLM kurulumunda ölçüldü). hash -r + mutlak yol ikisini de kapatır.
SYSPY=/usr/bin/python3
[ -x "$SYSPY" ] || SYSPY=$(PATH=/usr/local/bin:/usr/bin:/bin command -v python3)
hash -r 2>/dev/null || true

# Konteynerde ensurepip YOK (ölçüldü). Konteynerde root'uz, apt kullanılabilir.
if ! "$SYSPY" -c "import ensurepip" 2>/dev/null; then
  echo "  ensurepip yok -> python3-venv kuruluyor"
  apt-get update -qq && apt-get install -y -qq python3-venv >/dev/null 2>&1 || \
    apt-get install -y -qq "python$("$SYSPY" -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')-venv" >/dev/null
  "$SYSPY" -c "import ensurepip" 2>/dev/null || { echo "  ⛔ python3-venv kurulamadı"; exit 1; }
fi
# VARLIK değil KULLANILABİLİRLİK sınanır: ensurepip'siz ilk denemeden kalan venv'de
# bin/python VAR ama pip YOK; sadece dosya varlığına bakmak kırık venv'i sağlam sanar.
if "$REPO/.venv/bin/python" -m pip --version >/dev/null 2>&1; then
  echo "  zaten var ve çalışıyor: $REPO/.venv"
else
  [ -e "$REPO/.venv" ] && { echo "  mevcut venv kırık (pip yok) -> siliniyor"; rm -rf "$REPO/.venv"; hash -r 2>/dev/null || true; }
  "$SYSPY" -m venv "$REPO/.venv"
  echo "  oluşturuldu: $REPO/.venv"
fi
"$REPO/.venv/bin/python" -m pip install -q --upgrade pip
"$REPO/.venv/bin/pip" install -q -r "$REPO/requirements.txt"
"$REPO/.venv/bin/pip" freeze > "$REPO/sonuclar/pip_freeze_hpc_$(date +%Y%m%d).txt"
echo "  pip freeze yazıldı: sonuclar/pip_freeze_hpc_$(date +%Y%m%d).txt"

# ---------------------------------------------------------------- 4. pin doğrulaması
say "4/5  pin doğrulaması (pypdf BİLİMSEL OLARAK BAĞLAYICI — kusur kütüğü #5)"
"$REPO/.venv/bin/python" - <<'PY'
import sys, importlib.metadata as md
print(f"  python  {sys.version.split()[0]}   (referans ölçüm: 3.12.3)")
kapali = False
for pkg, bek in (("pypdf", "5.9.0"), ("openpyxl", "3.1.5"),
                 ("requests", "2.32.3"), ("rank_bm25", "0.2.2")):
    try:
        g = md.version(pkg)
    except Exception as e:
        print(f"  {pkg:10s} ⛔ okunamadı ({type(e).__name__})"); kapali = True; continue
    im = "" if g == bek else f"   ⛔ {bek} bekleniyordu"
    if g != bek and pkg == "pypdf":
        kapali = True          # yalnız pypdf bloke edicidir: metin çıkarımını değiştirir
    print(f"  {pkg:10s} {g}{im}")
eksik = [m for m in ("pypdf", "openpyxl", "rank_bm25", "requests")
         if not __import__("importlib.util", fromlist=["x"]).find_spec(m)]
print("  eksik paket:", eksik or "yok")
sys.exit(1 if (kapali or eksik) else 0)
PY

# ---------------------------------------------------------------- 5. python -m py_compile
say "5/5  betiklerin derlenebilirliği (HANDOVER kabul kriteri)"
BOZUK=0
for f in "$REPO"/scripts/*.py "$REPO"/hpc/*.py "$REPO"/hpc/remote_scripts/*.py; do
  [ -e "$f" ] || continue
  "$REPO/.venv/bin/python" -m py_compile "$f" 2>/dev/null || { echo "  ⛔ derlenmedi: $(basename "$f")"; BOZUK=$((BOZUK+1)); }
done
echo "  derlenemeyen betik: $BOZUK"
[ "$BOZUK" -eq 0 ] || exit 1

say "KURULUM TAMAM"
cat <<EOF
  depo   : $REPO
  venv   : $REPO/.venv          (source $REPO/env.sh)
  loglar : $WS/logs

  SIRADAKİ ADIM — KABUL KAPISI (17/17 görülmeden yeni koşu başlatma):
    cd $REPO && PATH=$REPO/.venv/bin:\$PATH bash scripts/dogrula_linux.sh

  Ollama (yerel model kolları için, ayrı adım):
    bash hpc/remote_scripts/ollama_kur.sh
EOF
