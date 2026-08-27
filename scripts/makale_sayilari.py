# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — MAKALE SAYILARI DOGRULAMA TABLOSU.

NE ISE YARAR
------------
Makale metnindeki her sayi bir dosyadan geliyor. Elle kopyalanan sayilar
kaybolur, kayar, eskir. Bu betik butun sonuc dosyalarini okur ve makalede
gecen rakamlari TEK YERDE basar; yazarken metni buna karsi okursunuz.

Eksik dosya varsa sessizce atlamaz, "EKSIK" der. Veri erisilebilirlik
beyani icin de dosya listesi cikarir.

Kullanim:
    python scripts/makale_sayilari.py
    python scripts/makale_sayilari.py --out sonuclar/makale_sayilari.txt
"""
import argparse
import csv
import os
import re
import statistics

L = []


def e(s=""):
    L.append(s)
    print(s)


def oku_csv(yol):
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def sayi(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def aralik(satirlar, alan, sadece=None):
    v = [sayi(r.get(alan)) for r in satirlar
         if (sadece is None or sadece(r)) and sayi(r.get(alan)) is not None]
    if not v:
        return "-"
    return f"{min(v):.2f} – {max(v):.2f}  (medyan {statistics.median(v):.2f}, n={len(v)})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", default="sonuclar")
    ap.add_argument("--out", default="sonuclar/makale_sayilari.txt")
    a = ap.parse_args()
    k = a.kok

    e("=" * 88)
    e("RUHSAT-Bench — MAKALEDE GECEN SAYILAR (dosyalardan uretildi)")
    e("=" * 88)

    # ---------------------------------------------------------- 4.2 / 4.3
    yerel = oku_csv(os.path.join(k, "f4_metrikler.csv"))
    e()
    e("[4.2-4.4] YEREL KOL")
    if not yerel:
        e("  EKSIK: f4_metrikler.csv")
    else:
        gec = [r for r in yerel if r.get("puanlanabilir") == "1"]
        yet = [r for r in gec if r.get("metrik_yeterli") == "1"]
        e(f"  hucre: {len(yerel)} | yanit esigini gecen: {len(gec)} | "
          f"metrik yeterli (n>=30): {len(yet)}")
        e(f"  elenen model: "
          f"{sorted({r['model'] for r in yerel if r.get('puanlanabilir') != '1'})}")
        e(f"  dengeli dogruluk : {aralik(yet, 'dengeli_dogruluk')}")
        e(f"  Youden J         : {aralik(yet, 'youden_J')}")
        e(f"  ECE              : {aralik(yet, 'ECE')}")
        e(f"  guven AUROC      : {aralik(yet, 'guven_AUROC')}")
        e(f"  kacinma (E1)     : {aralik([r for r in gec if r['kosul']=='E1'], 'kacinma_orani')}")

    # ---------------------------------------------------------- 4.5
    vk = oku_csv(os.path.join(k, "varyant_kararlilik.csv"))
    e()
    e("[4.5] VARYANT KARARSIZLIGI")
    if not vk:
        e("  EKSIK: varyant_kararlilik.csv")
    else:
        dahil = [r for r in vk if r.get("ozete_dahil") == "1"]
        e(f"  hucre: {len(vk)} | ozete giren (n>=30, iki varyant): {len(dahil)}")
        for ad, aA, aB in (("P(DOGRU)", "pDOGRU_A", "pDOGRU_B"),
                           ("taahhut dogrulugu", "dogruluk_A", "dogruluk_B"),
                           ("lambda", "lambda_A", "lambda_B")):
            d = [abs(sayi(r[aA]) - sayi(r[aB])) for r in dahil
                 if sayi(r.get(aA)) is not None and sayi(r.get(aB)) is not None]
            if d:
                e(f"  |A-B| {ad:<20} ort {statistics.mean(d):.3f}  "
                  f"medyan {statistics.median(d):.3f}  en buyuk {max(d):.3f}")
        dp = [abs(sayi(r["pDOGRU_A"]) - sayi(r["pDOGRU_B"])) for r in dahil]
        dl = [abs(sayi(r["lambda_A"]) - sayi(r["lambda_B"])) for r in dahil
              if sayi(r.get("lambda_A")) is not None and sayi(r.get("lambda_B")) is not None]
        if dp and dl:
            e(f"  ORAN P(DOGRU)/lambda = x{statistics.mean(dp)/max(statistics.mean(dl),1e-9):.1f}")

    # ---------------------------------------------------------- 4.6
    e()
    e("[4.6] BARINDIRILAN MODELLER")
    for etiket, dosya in (("sonnet", "f4_metrikler_frontier.csv"),
                          ("haiku", "f4_metrikler_haiku.csv")):
        r_ = oku_csv(os.path.join(k, dosya))
        if not r_:
            e(f"  EKSIK: {dosya}")
            continue
        for r in r_:
            e(f"  {etiket:<7} {r['kosul']}  yanit {r['yanit_orani']}  "
              f"kacinma {r['kacinma_orani']}  n {r['n_taahhut']}  "
              f"bacc {r.get('dengeli_dogruluk','-')}  J {r.get('youden_J','-')}  "
              f"ECE {r.get('ECE','-')}  AUROC {r.get('guven_AUROC','-')}")

    # ---------------------------------------------------------- rapor icinden
    e()
    e("[4.3 / 4.6] KACINMANIN BILGI DEGERI  (rapor dosyalarindan)")
    for etiket, dosya in (("yerel", "f4_rapor.txt"),
                          ("sonnet", "f4_rapor_frontier.txt"),
                          ("haiku", "f4_rapor_haiku.txt")):
        yol = os.path.join(k, dosya)
        if not os.path.exists(yol):
            e(f"  EKSIK: {dosya}")
            continue
        metin = open(yol, encoding="utf-8-sig", errors="replace").read()
        blok = metin.split("[1.5]")[-1].split("[1.6]")[0] if "[1.5]" in metin else ""
        satir = [s for s in blok.splitlines()
                 if re.search(r"[+-]\d\.\d\d\s+\d\.\d{3,4}", s)]
        e(f"  --- {etiket} ({len(satir)} satir)")
        for s in satir:
            e("   " + s.strip())

    # ---------------------------------------------------------- 4.8
    e()
    e("[4.8] KOSULAR ARASI TEKRAR")
    # Ad-turetilmis kararsizlik dosyalarinin HEPSI okunur. Eskiden tek bir
    # f4_kararsizlik.txt okunuyordu ve her kosu oncekini eziyordu.
    bulundu = False
    for ad in sorted(os.listdir(k) if os.path.isdir(k) else []):
        if not ad.startswith("kararsizlik_") or not ad.endswith(".txt"):
            continue
        bulundu = True
        e(f"  --- {ad}")
        for s in open(os.path.join(k, ad), encoding="utf-8-sig", errors="replace"):
            if "/ E" in s and re.search(r"0\.\d\d", s):
                e("   " + s.rstrip())
    if not bulundu:
        e("  EKSIK: kararsizlik_*.txt bulunamadi")

    # ---------------------------------------------------------- 3.6
    e()
    e("[3.6] UZMAN DENETIMI")
    for etiket, dosya, anahtarlar in (
            ("gecis 1", "kappa_raporu.txt", ("kappa", "tuzak", "ust sinir")),
            ("gecis 2", "gecis2_raporu.txt", ("kappa", "CERCEVE TAHMINI",
                                              "UST SINIR", "BILESIK", "Fisher"))):
        yol = os.path.join(k, dosya)
        if not os.path.exists(yol):
            e(f"  EKSIK: {dosya}")
            continue
        e(f"  --- {etiket}")
        for s in open(yol, encoding="utf-8-sig", errors="replace"):
            if any(x.lower() in s.lower() for x in anahtarlar):
                e("   " + s.rstrip())

    # ---------------------------------------------------------- dosya listesi
    e()
    e("=" * 88)
    e("VERI ERISILEBILIRLIK — sonuclar/ altindaki dosyalar")
    e("=" * 88)
    if os.path.isdir(k):
        for ad in sorted(os.listdir(k)):
            p = os.path.join(k, ad)
            if os.path.isfile(p):
                e(f"  {os.path.getsize(p):>10,} bayt  {ad}")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\nyazildi: {a.out}")


if __name__ == "__main__":
    main()
