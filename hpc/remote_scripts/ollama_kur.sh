#!/usr/bin/env bash
# hpc/remote_scripts/ollama_kur.sh — Ollama kurulumu + model çekme. [KONTEYNERDE ÇALIŞIR]
#
# ⚠ BU BETİK HENÜZ HEDEF ORTAMDA KOŞULMADI (2026-08-27).
#   Belgeden yazıldı, ÖLÇÜLMEDİ. Projenin kuralı "ölçülmeyeni varsayma" olduğu için
#   bu uyarı ilk başarılı koşuya kadar burada kalır; koşunca çıktı hpc/README.md'ye
#   ölçüm olarak yazılır ve bu blok silinir.
#
# TASARIM KARARLARI:
#
# 1) systemd YOK. Konteynerde `systemctl enable --now ollama` çalışmaz; resmî
#    install.sh systemd birimi kurmaya çalışır ve o adımda düşer. Bu yüzden ikili
#    dosya doğrudan tarball'dan açılıyor ve sunucu `setsid nohup` ile başlatılıyor
#    (aynı desen remote.nohup() ile uzun koşularda kullanılıyor).
#
# 2) OLLAMA_MODELS=/workspace/ollama/models. Varsayılan ~/.ollama OVERLAY'dedir;
#    idle-culler konteyneri durdurunca çekilen modellerin tamamı uçar. MarkLLM'de
#    aynı hata HF önbelleğinde ölçülmüştü (30 GB). env.sh tek kaynak doğruluktur.
#
# 3) 127.0.0.1, localhost DEĞİL. ORTAM.md 2.1'de ölçüldü: aynı 946 çağrı
#    localhost ile 47,7 dk, 127.0.0.1 ile 11,2 dk (×4,2); çıktılar 946/946 aynı.
#    Betikler zaten IP kullanıyor; sunucu da IP'ye bağlanıyor ki dinlediği yer eşleşsin.
#
# 4) ASGARİ küme varsayılan. GECIS_LINUX.md §3: kapalı kitap tablosunu yeniden
#    koşmak GEREKMEDİKÇE 18 modelin kalanını çekmeyin (disk ve saat). Tam küme
#    --tam ile ve disk kontrolünden sonra gelir.
#
# 5) GPU TEK ve PAYLAŞIMLI (MarkLLM oturumu da aynı kartı kullanıyor). Model
#    çekmeden önce nvidia-smi basılır; koşu sırası gözetilmelidir.
#
#   bash hpc/remote_scripts/ollama_kur.sh            # kur + asgari 3 model
#   bash hpc/remote_scripts/ollama_kur.sh --tam      # ORTAM.md 8'deki 18 modelin tamamı
#   bash hpc/remote_scripts/ollama_kur.sh --sadece-kur
set -euo pipefail

WS=/workspace
OL="$WS/ollama"
SURUM="${OLLAMA_SURUM:-v0.12.6}"          # sabitlenir: model dosyaları sürüme bağlı olabilir
KUME=asgari
for a in "$@"; do
  case "$a" in
    --tam)        KUME=tam ;;
    --sadece-kur) KUME=yok ;;
  esac
done

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

# GECIS_LINUX.md §3'ün asgari kümesi (F5 model seçimi, EK-4)
ASGARI=(
  "qwen2.5:32b-instruct"
  "gemma3:27b"
  "llama3.2:3b-instruct-q8_0"
)
# ORTAM.md §8'de kurulu olduğu KAYITLI tam küme (18 model)
TAM=(
  "qwen2.5:32b-instruct" "qwen2.5:14b-instruct"
  "qwen2.5:7b-instruct-q4_K_M" "qwen2.5:7b-instruct-q5_K_M"
  "qwen2.5:7b-instruct-q8_0"   "qwen2.5:7b-instruct-fp16"
  "qwen2.5:3b-instruct-q4_K_M" "qwen2.5:3b-instruct-q5_K_M"
  "qwen2.5:3b-instruct-q8_0"   "qwen2.5:3b-instruct-fp16"
  "gemma3:27b" "gemma3:12b" "gemma3:4b"
  "llama3.2:3b-instruct-q4_K_M" "llama3.2:3b-instruct-q5_K_M"
  "llama3.2:3b-instruct-q8_0"   "llama3.2:3b-instruct-fp16"
  "llama3.2:1b"
)

say "1/4  ortam"
mkdir -p "$OL"/{bin,models,logs}
# env.sh bootstrap.sh tarafından üretilir; yoksa burada tamamla (idempotent).
if [ -f "$WS/env.sh" ]; then
  # shellcheck disable=SC1091
  source "$WS/env.sh"
else
  export OLLAMA_MODELS="$OL/models" OLLAMA_HOST=127.0.0.1:11434 PATH="$OL/bin:$PATH"
  echo "  UYARI: /workspace/env.sh yok — önce bootstrap.sh koşulmalı"
fi
echo "  OLLAMA_MODELS=$OLLAMA_MODELS"
echo "  OLLAMA_HOST=$OLLAMA_HOST"
df -h "$WS" | tail -1 | awk '{print "  /workspace: "$4" bos"}'
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv 2>&1 | head -3 | sed 's/^/  gpu: /'

say "2/4  ollama ikilisi ($SURUM)"
if [ -x "$OL/bin/ollama" ] && "$OL/bin/ollama" --version >/dev/null 2>&1; then
  echo "  zaten kurulu: $("$OL/bin/ollama" --version 2>&1 | head -1)"
else
  TGZ=/tmp/ollama-linux-amd64.tgz
  URL="https://github.com/ollama/ollama/releases/download/${SURUM}/ollama-linux-amd64.tgz"
  echo "  indiriliyor: $URL"
  curl -fL --retry 3 -o "$TGZ" "$URL"
  # tarball kökünde bin/ ve lib/ vardır; OL altına açıyoruz
  tar xzf "$TGZ" -C "$OL"
  rm -f "$TGZ"
  chmod +x "$OL/bin/ollama"
  echo "  kuruldu: $("$OL/bin/ollama" --version 2>&1 | head -1)"
fi

say "3/4  sunucu (setsid nohup — websocket/VPN kopsa da yaşar)"
if curl -s --max-time 3 "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
  echo "  zaten ayakta: http://$OLLAMA_HOST"
else
  setsid nohup env OLLAMA_MODELS="$OLLAMA_MODELS" OLLAMA_HOST="$OLLAMA_HOST" \
    "$OL/bin/ollama" serve > "$OL/logs/serve.log" 2>&1 < /dev/null &
  echo "  başlatıldı (pid $!), log: $OL/logs/serve.log"
  for i in $(seq 1 30); do
    sleep 2
    curl -s --max-time 3 "http://$OLLAMA_HOST/api/tags" >/dev/null 2>&1 && break
    [ "$i" -eq 30 ] && { echo "  ⛔ sunucu 60 s'de ayağa kalkmadı:"; tail -20 "$OL/logs/serve.log"; exit 1; }
  done
  echo "  ayakta."
fi

if [ "$KUME" = "yok" ]; then
  say "MODEL ÇEKİLMEDİ (--sadece-kur)"
  exit 0
fi

say "4/4  modeller ($KUME küme)"
if [ "$KUME" = "tam" ]; then
  MODELLER=("${TAM[@]}")
  BOS_GB=$(df -BG --output=avail "$WS" | tail -1 | tr -dc '0-9')
  echo "  ⚠ tam küme 18 model. /workspace'te $BOS_GB GB boş."
  [ "$BOS_GB" -lt 200 ] && echo "  ⚠ 200 GB'ın altında — çekim yarıda kalabilir, disk izlenmeli."
else
  MODELLER=("${ASGARI[@]}")
fi
BASARI=0; HATA=0
for m in "${MODELLER[@]}"; do
  if "$OL/bin/ollama" list 2>/dev/null | awk '{print $1}' | grep -qx "$m"; then
    echo "  [VAR  ] $m"; BASARI=$((BASARI+1)); continue
  fi
  printf '  [ÇEK  ] %s ... ' "$m"
  if "$OL/bin/ollama" pull "$m" >> "$OL/logs/pull.log" 2>&1; then
    echo "tamam"; BASARI=$((BASARI+1))
  else
    echo "⛔ BAŞARISIZ (log: $OL/logs/pull.log)"; HATA=$((HATA+1))
  fi
done

say "SONUÇ: $BASARI model hazır, $HATA hata"
du -sh "$OLLAMA_MODELS" 2>/dev/null | awk '{print "  model dizini: "$1}'
cat <<EOF

  Determinizm kuralı (ORTAM.md §3'te ölçüldü): temperature 0 + sabit seed ->
  946/946 birebir tekrar. Betikler http://127.0.0.1:11434'e bağlanır.

  ⚠ Ollama SÜRÜMÜ sonuç dosyalarına yazılmalı: GECIS_LINUX.md §7, model
  dosyalarının sürümler arası bayt-birebir aynı olacağının GARANTİ OLMADIĞINI
  söylüyor. Yerel koşular yeniden yapılacaksa bu beyan edilir.
EOF
[ "$HATA" -eq 0 ] || exit 1
