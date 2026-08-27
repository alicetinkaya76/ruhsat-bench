# hpc/deploy.py — yerelden TF-HPC'ye tek komutla kurulum. [YEREL ÇALIŞIR]
#
# AKIŞ: depo gönder -> bootstrap -> sürüm kayması ölç -> KABUL KAPISI (17/17).
# Son iki adım isteğe bağlı değil. GECIS_LINUX.md §5: "Çıktının son satırı
# 'SONUC: 17 tamam, 0 hata' olmalı. Değilse ortam farkı vardır: makaleye tek sayı
# geçmeden kapatın." `--sadece-gonder` yalnız kod tazelemek içindir.
#
# NE GÖNDERİLİR: bütün depo (25 MB; PDF'ler 9 MB, arşiv jsonl'leri 8 MB).
#   MarkLLM'de çekirdek upstream'den klonlanıyordu; burada klonlanacak bir upstream
#   YOK — kaynak PDF'ler ve arşiv koşuları deponun kendisidir ve taşınmaları şart
#   (dogrula_linux.sh 6/6 adımı arşiv jsonl'lerini okur).
# NE GÖNDERİLMEZ: .git, .venv, __pycache__ (push_dir süzer).
#
#   python -m hpc.deploy                 # gönder + kur + kayma + kabul kapısı
#   python -m hpc.deploy --sadece-gonder # yalnız kodu tazele
#   python -m hpc.deploy --ollama        # + ollama_kur.sh (asgari küme)
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from hpc.remote import REMOTE_ROOT, connect  # noqa: E402

# Depo kökünün ALTINDAN gönderilecek dizinler. Kök dosyaları (requirements.txt,
# *.md) ayrıca tek tek yüklenir — push_dir dizin alır, dosya almaz.
GONDERILECEK = ["scripts", "hpc", "data", "sonuclar", "uzlasi", "beyanlar"]
KOK_DOSYALARI = ["requirements.txt", "ORTAM.md", "HANDOVER.md", "GECIS_LINUX.md",
                 "kusur_kutugu.md", "REKONSTRUKSIYON.md"]
# dogrula_linux.sh §5 bunları depo kökünde `kodlay*1*.xlsx` kalıbıyla arar.
KOK_DESENLERI = ["kodlayici*.xlsx"]


def main() -> None:
    ap = argparse.ArgumentParser(description="TF-HPC kurulumu (RUHSAT-Bench)")
    ap.add_argument("--sadece-gonder", action="store_true", help="yalnız kodu gönder")
    ap.add_argument("--ollama", action="store_true", help="ollama_kur.sh da koştur")
    ap.add_argument("--ollama-tam", action="store_true", help="18 modelin tamamını çek")
    args = ap.parse_args()

    h = connect()
    try:
        print(f"HEDEF: {REMOTE_ROOT}\n")

        print("1) depo gönderiliyor")
        toplam = 0
        for d in GONDERILECEK:
            src = _ROOT / d
            if not src.is_dir():
                print(f"   {d:10s} ATLANDI (yok)")
                continue
            n = h.push_dir(src, REMOTE_ROOT)
            toplam += n
            print(f"   {d:10s} {n / 1024:8.0f} KiB")
        koku = [_ROOT / f for f in KOK_DOSYALARI]
        for desen in KOK_DESENLERI:
            koku += sorted(_ROOT.glob(desen))
        for f in koku:
            if not f.is_file():
                print(f"   {f.name:10s} ATLANDI (yok)")
                continue
            blob = f.read_bytes()
            h.put_bytes_parcali(f"{REMOTE_ROOT}/{f.name}", blob)
            toplam += len(blob)
            print(f"   {f.name:30s} {len(blob) / 1024:8.0f} KiB")
        print(f"   {'TOPLAM':30s} {toplam / 1048576:8.1f} MiB")

        if args.sadece_gonder:
            print("\n--sadece-gonder verildi; kurulum, kayma ölçümü ve kabul kapısı ATLANDI.")
            return

        print("\n2) bootstrap (venv + pinli paketler)")
        out, err, rc = h.sh(
            f"cd {REMOTE_ROOT} && bash hpc/remote_scripts/bootstrap.sh 2>&1", timeout=1800)
        print(out)
        if rc != 0:
            print(f"\n⛔ bootstrap BAŞARISIZ (rc={rc})", file=sys.stderr)
            if err.strip():
                print(err, file=sys.stderr)
            sys.exit(1)

        print("\n3) sürüm kayması ölçümü (pypdf metin çıkarımı — kusur kütüğü #5)")
        out, err, rc_kayma = h.sh(
            f"cd {REMOTE_ROOT} && python hpc/remote_scripts/ortam_kayma.py --yeniden-kur 2>&1",
            timeout=1800, venv=True)
        print(out)
        if err.strip():
            print("--- stderr ---\n" + err, file=sys.stderr)
        _indir(h, f"{REMOTE_ROOT}/sonuclar/ortam_kayma.json",
               _ROOT / "sonuclar" / "ortam_kayma_hpc.json")
        if rc_kayma != 0:
            print("\n⛔ SÜRÜM KAYMASI BLOKE EDİCİ (yukarı bak). Kabul kapısı koşulmadı.",
                  file=sys.stderr)
            sys.exit(2)

        print("\n4) KABUL KAPISI — scripts/dogrula_linux.sh (17/17 şart)")
        out, err, rc_kapi = h.sh(
            f"cd {REMOTE_ROOT} && PATH={REMOTE_ROOT}/.venv/bin:$PATH "
            f"bash scripts/dogrula_linux.sh 2>&1", timeout=3600)
        print(out)
        h.sh(f"cd {REMOTE_ROOT} && cp /tmp/rb/*.log sonuclar/ 2>/dev/null; true", timeout=60)
        if rc_kapi != 0:
            print("\n⛔ KABUL KAPISI GEÇİLMEDİ. GECIS_LINUX.md §5: makaleye tek sayı "
                  "geçmeden ortam farkını çözün (/tmp/rb/*.log).", file=sys.stderr)
            sys.exit(3)
        print("\n✓ 17/17 — port doğrulandı.")

        if args.ollama or args.ollama_tam:
            print("\n5) Ollama (⚠ bu betik hedef ortamda HENÜZ KOŞULMADI)")
            bayrak = " --tam" if args.ollama_tam else ""
            out, err, rc = h.sh(
                f"cd {REMOTE_ROOT} && bash hpc/remote_scripts/ollama_kur.sh{bayrak} 2>&1",
                timeout=7200)
            print(out)
            if rc != 0:
                print(f"\n⚠ Ollama kurulumu rc={rc} — yerel model kolları henüz koşulamaz. "
                      "Deterministik zincir (adım 4) bundan ETKİLENMEZ.", file=sys.stderr)
    finally:
        h.close()


def _indir(h, uzak: str, yerel: Path) -> None:
    try:
        yerel.parent.mkdir(parents=True, exist_ok=True)
        blob = h.get_bytes(uzak)
        yerel.write_bytes(blob)
        print(f"   yerele alındı: {yerel.relative_to(_ROOT)} ({len(blob)} bayt)")
    except Exception as e:
        print(f"   UYARI: {uzak} indirilemedi ({type(e).__name__}) — ölçüm uzakta kalmış olabilir.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
