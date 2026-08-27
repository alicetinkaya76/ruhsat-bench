#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hpc/remote_scripts/ortam_kayma.py — SÜRÜM KAYMASI ÖLÇÜMÜ. [KONTEYNERDE ÇALIŞIR]

MarkLLM'deki `drift.py`'nin bu projedeki karşılığı. Oradaki sorular torch/transformers
davranışıydı; burada tek bir bağımlılık bilimsel olarak bağlayıcı: **pypdf**.

NEDEN AYRI BİR ÖLÇÜM: `scripts/dogrula_linux.sh` birim SAYILARINI ve kontrol
oranlarını kapılıyor (1366 / 440-441 / 473-473 / 120-120). Ama kusur kütüğü #5,
iki pypdf sürümünün TBDY metninde **870747 / 870751 karakter** farkı ürettiğini
ölçmüştü ve o farkın birim sayısını DEĞİŞTİRMEDİĞİNİ raporlamıştı. Yani metin
düzeyindeki kayma, sayı düzeyindeki kapıdan SESSİZCE geçer. Bu betik o boşluğu
kapatır: çıkarılan metnin sha256'sını ve karakter sayısını belge belge ölçer.

Kapı politikası (`f4_dayanak.py`'nin BM25 getirimi bu metinler üzerinde çalışacağı için):
  - `pdf_sha256` farklıysa       -> ÇIKIŞ 2 (bloke edici: kaynak belge değişmiş)
  - `birim` sayısı farklıysa     -> ÇIKIŞ 2 (bloke edici: ayrıştırma kaymış)
  - `metin_sha256` farklı ama karakter farkı |Δ| <= 8 ise -> UYARI, çıkış 0
    (kütük #5'te ölçülen zararsız sınıf; makalede pypdf sürümü + metin hash beyan edilir)
  - `metin_sha256` farklı ve |Δ| > 8 ise -> ÇIKIŞ 2 (ölçülmemiş büyüklükte kayma)

REFERANS ÖLÇÜM: macOS 25.5 · Python 3.11.9 · pypdf 5.9.0 · 2026-08-27,
rekonstrüksiyon sonrası `dogrula_linux.sh` 17/17 koşusunun ürettiği
`data/korpus/belge_manifest.txt`. TBDY 870747 dalı (kütük #5'in iki dalından biri).

Koşu:
    cd /workspace/ruhsat-bench
    source /workspace/env.sh
    python hpc/remote_scripts/ortam_kayma.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Betik başında stdout/stderr UTF-8 reconfigure (ORTAM.md 2.2; Linux'ta zararsız,
# dosya Windows'a dönerse cp1252 borulama çökmesini önler).
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8")
    except Exception:
        pass

KOK = Path(__file__).resolve().parents[2]

REFERANS = {
    "6331":    dict(dosya="6331_isg_kanunu.pdf",
                    pdf_sha256="2c4862501446271079d88776109717df747a9030dc355c941f21cf2afbec0404",
                    metin_sha256="3a9d8c567103501d2b8d4371fdd290d056a1266cd28ccaf176cddba723325ae4",
                    karakter=71025, birim=39),
    "4708":    dict(dosya="4708_yapi_denetimi.pdf",
                    pdf_sha256="e4ad97473caf12d58bbab0b45e685e5079602d109fb8ad9c966d129199297bab",
                    metin_sha256="3a1978358d749314b7ef9331561ae0d87ab2442b17094e909c89859e82e25413",
                    karakter=55563, birim=15),
    "3194":    dict(dosya="3194_imar_kanunu.pdf",
                    pdf_sha256="5557b139186efcd6d61af58e563f29cae0e9fe383d0e2ef264be5d6f289fd70d",
                    metin_sha256="78bd9bd09f8f3381afd0c62994a1555df43e9911fff61d0c00ad8c5850dfa255",
                    karakter=158417, birim=49),
    "ISGRISK": dict(dosya="isg_risk_yonetmeligi.pdf",
                    pdf_sha256="47ec8c68a5c1d931818e557a382fd6f44bb69d302182622fdb18af9fb10a27dc",
                    metin_sha256="18fadf50081029c50fe21068868cd84976364ffda0b78b979ab7fb1d27393c39",
                    karakter=16703, birim=19),
    "TBDY":    dict(dosya="TBDY_2018.pdf",
                    pdf_sha256="8d3a9a463d4a534ec2c6834c557b5f706e2ad976c2d6837f6c9b6242e38a6bb2",
                    metin_sha256="387b6df226caaf7461266990b13b4d87751a481da4e50c3e15fd27b00124be75",
                    karakter=870747, birim=1208),
    "YDUY":    dict(dosya="yapi_denetim_uygulama_yon.pdf",
                    pdf_sha256="cdb4aef16da40cd2345efab42837d7586608c4f20e8ee2b81ae51e027ade7753",
                    metin_sha256="3927d2136b7df795f9e88daaab8ab5cd3d5eeb3a6e1c6797e91272c085b79c64",
                    karakter=94556, birim=36),
}

# Kütük #5'te ÖLÇÜLEN zararsız sapma 4 karakterdi. Sınırı 8'e koyuyorum: ölçülenin
# iki katı, ama "birkaç yüz karakter kaydı" durumunu hâlâ bloke eder. Bu sınır
# DIŞSAL OLARAK GEREKÇELENDİRİLMİŞ DEĞİLDİR ve rapora böyle yazılır.
KARAKTER_TOLERANSI = 8

BLOK = re.compile(
    r"kanun: (?P<kanun>\S+)\n"
    r"dosya: (?P<dosya>\S+)\n"
    r"pdf_sha256: (?P<pdf_sha256>\w+)\n"
    r"metin_sha256: (?P<metin_sha256>\w+)\n"
    r"karakter: (?P<karakter>\d+)\n"
    r"birim_sayisi: (?P<birim>\d+)")


def manifest_oku(yol: Path) -> dict:
    metin = yol.read_text(encoding="utf-8-sig")
    return {m["kanun"]: {"dosya": m["dosya"], "pdf_sha256": m["pdf_sha256"],
                         "metin_sha256": m["metin_sha256"],
                         "karakter": int(m["karakter"]), "birim": int(m["birim"])}
            for m in BLOK.finditer(metin)}


def surumler() -> dict:
    import importlib.metadata as md
    d = {"python": sys.version.split()[0]}
    for pkg in ("pypdf", "openpyxl", "requests", "rank_bm25"):
        try:
            d[pkg] = md.version(pkg)
        except Exception as e:
            d[pkg] = f"<okunamadi: {type(e).__name__}>"
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description="RUHSAT-Bench sürüm kayması ölçümü")
    ap.add_argument("--manifest", default="data/korpus/belge_manifest.txt",
                    help="karşılaştırılacak manifest (varsayılan: mevcut korpus çıktısı)")
    ap.add_argument("--yeniden-kur", action="store_true",
                    help="önce korpus_kur.py'yi koşup manifesti TAZE üret")
    ap.add_argument("--json", default="sonuclar/ortam_kayma.json")
    args = ap.parse_args()

    print("== RUHSAT-Bench sürüm kayması ölçümü ==")
    sv = surumler()
    print("  ortam :", " · ".join(f"{k} {v}" for k, v in sv.items()))
    print("  referans: macOS · Python 3.11.9 · pypdf 5.9.0 · 2026-08-27")
    if sv.get("pypdf") != "5.9.0":
        print(f"  ⚠ pypdf {sv.get('pypdf')} — referans 5.9.0. Metin kayması BEKLENİR.")

    if args.yeniden_kur:
        print("\n  korpus_kur.py yeniden koşuluyor (taze manifest)...")
        r = subprocess.run(
            [sys.executable, "-u", "scripts/korpus_kur.py",
             "--pdf-dir", "data/kaynak_pdf",
             "--claims", "data/iddialar/uretilen_iddialar_v6_onarilmis.csv",
             "--out", "data/korpus"],
            cwd=KOK, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            print("  ⛔ korpus_kur.py başarısız:\n" + (r.stderr or r.stdout)[-2000:])
            return 2

    yol = KOK / args.manifest
    if not yol.exists():
        print(f"  ⛔ manifest yok: {yol}  (--yeniden-kur ile üretebilirsin)")
        return 2
    olculen = manifest_oku(yol)

    bloke, uyari, satirlar = [], [], []
    print(f"\n  {'belge':<10}{'karakter':>10}{'Δkar':>7}{'birim':>7}  pdf   metin")
    print("  " + "-" * 56)
    for kanun, bek in REFERANS.items():
        g = olculen.get(kanun)
        if g is None:
            print(f"  {kanun:<10}{'—':>10}{'':>7}{'':>7}  ⛔ manifestte yok")
            bloke.append(f"{kanun}: manifestte yok")
            continue
        d_kar = g["karakter"] - bek["karakter"]
        pdf_ok = g["pdf_sha256"] == bek["pdf_sha256"]
        met_ok = g["metin_sha256"] == bek["metin_sha256"]
        bir_ok = g["birim"] == bek["birim"]
        print(f"  {kanun:<10}{g['karakter']:>10}{d_kar:>+7}{g['birim']:>7}  "
              f"{'✓' if pdf_ok else '⛔'}     {'✓' if met_ok else ('~' if abs(d_kar) <= KARAKTER_TOLERANSI else '⛔')}")
        if not pdf_ok:
            bloke.append(f"{kanun}: pdf_sha256 farklı — KAYNAK BELGE DEĞİŞMİŞ")
        if not bir_ok:
            bloke.append(f"{kanun}: birim {bek['birim']} -> {g['birim']} — AYRIŞTIRMA KAYMIŞ")
        if not met_ok:
            (uyari if abs(d_kar) <= KARAKTER_TOLERANSI else bloke).append(
                f"{kanun}: metin_sha256 farklı, Δkarakter={d_kar:+d}")
        satirlar.append(dict(kanun=kanun, olculen=g, beklenen=bek, d_karakter=d_kar,
                             pdf_ok=pdf_ok, metin_ok=met_ok, birim_ok=bir_ok))

    (KOK / args.json).parent.mkdir(parents=True, exist_ok=True)
    (KOK / args.json).write_text(json.dumps(
        {"surumler": sv, "tolerans": KARAKTER_TOLERANSI,
         "belgeler": satirlar, "uyari": uyari, "bloke": bloke},
        ensure_ascii=False, indent=2), encoding="utf-8-sig")
    print(f"\n  json: {args.json}")

    if uyari:
        print("\n  UYARI (kütük #5 sınıfı — zararsız ölçüldü, makalede beyan edilir):")
        for u in uyari:
            print("    ~", u)
    if bloke:
        print("\n  ⛔ BLOKE EDİCİ:")
        for b in bloke:
            print("    ⛔", b)
        print("\n  Yeni koşu BAŞLATILMAZ. pypdf sürümünü referansa çek ya da")
        print("  farkı ölçüp kusur kütüğüne yaz, kullanıcıya bildir.")
        return 2

    print("\n  SONUÇ: sürüm kayması YOK" + (" (yalnız tolerans içi metin farkı)" if uyari else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
