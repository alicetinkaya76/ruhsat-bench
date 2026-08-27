# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — P6 YUZEY KALIBI SIZINTISI OLCUMU (yeni cikarim YOK).

SORU
----
Uretecte P6 iki kalipla uretiliyor ve her kalip TEK bir altin etikete
baglaniyor:

    P6_yil        "... N. maddesinde YYYY yilinda degisiklik yapilmistir."   -> DOGRU
    P6_degismedi  "... N. maddesi, ... bu yana hic degistirilmemistir."      -> YANLIS

Yani P6'da altin etiket CUMLE KALIBINDAN okunabilir. Diger problarda bu
yok: P1 / P2_swap / P5_* ayni yuzey kalibini paylasir, P3_yil ile
P3_yil_dogru de ayni kalibi paylasir (yalnizca yil degisir).

Bu betik, modellerin bu kisayolu KULLANIP KULLANMADIGINI mevcut konsensus
kosusundan olcer. Yeni GPU zamani gerekmez.

YONTEM ve POZITIF/NEGATIF KONTROL
---------------------------------
Tek sinifli bir tabakada "dogruluk" = cevap yanliligi. O yuzden dogruluga
degil, IKI SINIFI DA ICEREN tabakalarda DENGELI DOGRULUGA (bacc) bakilir.
Bunu hesaplayabildigimiz yalnizca iki yer var:

  bacc(P6) = 1/2 [ P(DOGRU | P6_yil) + P(YANLIS | P6_degismedi) ]
  bacc(P3) = 1/2 [ P(DOGRU | P3_dogru-alt) + P(YANLIS | P3_yil) ]   <- KONTROL

P3 kontroldur cunku ayni kalibi kullanir: yuksek bacc(P3) gercek bilgi
demektir (kanunlarin kabul yili genel kulturdur). P6'nin icerigi ise
ezberlenemez (bir yonetmeligin 17. maddesinin degisiklik yili).

  bacc(P6) >> bacc(P3) ve bacc(P6) >> bacc(genel)
      -> kalip okunuyor. Sizinti gercek.
  bacc(P6) ~ bacc(genel)
      -> kisayol kullanilmiyor; sizinti tasarim kusuru olarak kalir ama
         mevcut sonuclari kirletmiyor.

Ayrica yanlilik referansi olarak tek sinifli tabakalar basilir:
P1 (hepsi DOGRU) ve P5 (hepsi YANLIS) — bunlarin "dogrulugu" modelin
DOGRU/YANLIS egilimidir, bilgi degil.

Kullanim:
    python scripts/p6_kestirilebilirlik.py
    python scripts/p6_kestirilebilirlik.py --csv data/iddialar/uretilen_iddialar_v4_temiz.csv
"""
import argparse
import csv
import json
import math
import os
from collections import defaultdict

DOGRU_ALT = {"P3_yil_dogru", "P3_yururluk"}


def oku_karar(r):
    for k in ("karar", "cevap", "tahmin", "pred"):
        v = r.get(k)
        if isinstance(v, str) and v.strip():
            v = v.strip().upper()
            if v.startswith("D"):
                return "DOGRU"
            if v.startswith("Y"):
                return "YANLIS"
            if v.startswith("E") or v.startswith("B"):
                return "EMIN_DEGILIM"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v4_temiz.csv")
    ap.add_argument("--jsonl", default="sonuclar/konsensus.jsonl")
    ap.add_argument("--out", default="sonuclar/p6_kestirilebilirlik.txt")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        kayit = {r["id"]: r for r in csv.DictReader(fh)}

    if not os.path.exists(a.jsonl):
        print(f"! {a.jsonl} yok.")
        return

    cevap = defaultdict(dict)
    with open(a.jsonl, encoding="utf-8") as fh:
        for satir in fh:
            satir = satir.strip()
            if not satir:
                continue
            r = json.loads(satir)
            k = oku_karar(r)
            if k:
                cevap[f"{r.get('model','?')} / {r.get('kosul','?')}"][str(r.get("id"))] = k

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — P6 YUZEY KALIBI SIZINTISI (mevcut kosudan, yeni cikarim yok)")
    e("=" * 78)
    e(f"temiz kume: {a.csv} ({len(kayit)} iddia) | kosu: {a.jsonl}")
    p6 = sum(1 for r in kayit.values() if r.get("probe") == "P6_guncellik")
    e(f"P6 payi: {p6}/{len(kayit)} = %{100*p6/max(len(kayit),1):.1f}")

    def oran(hucre, model, alt_kume, beklenen):
        n = d = 0
        for cid in alt_kume:
            k = cevap[model].get(cid)
            if k in ("DOGRU", "YANLIS"):
                n += 1
                d += (k == beklenen)
        return (d / n if n else float("nan"), n)

    grup = defaultdict(list)
    for cid, r in kayit.items():
        grup[r.get("probe_alt", "")].append(cid)
    P6Y = grup.get("P6_yil", [])
    P6D = grup.get("P6_degismedi", [])
    P3D = [c for k in DOGRU_ALT for c in grup.get(k, [])]
    P3Y = grup.get("P3_yil", [])
    P1 = grup.get("P1_verbatim", []) + grup.get("P1_madde_atifli", [])
    P5 = grup.get("P5_maddeshift", []) + grup.get("P5_lawshuffle", [])
    tum_d = [c for c, r in kayit.items() if r.get("gold") == "DOGRU"]
    tum_y = [c for c, r in kayit.items() if r.get("gold") == "YANLIS"]

    e()
    e("[1] MODEL x KOSUL")
    e(f"    {'model / kosul':<36} {'bacc':>6} {'baccP3':>7} {'baccP6':>7} "
      f"{'P1(D)':>6} {'P5(Y)':>6} {'kazanc':>7}")
    kazanclar = []
    for model in sorted(cevap):
        gd, nd = oran(None, model, tum_d, "DOGRU")
        gy, ny = oran(None, model, tum_y, "YANLIS")
        bacc = (gd + gy) / 2 if nd and ny else float("nan")
        a6d, n6d = oran(None, model, P6Y, "DOGRU")
        a6y, n6y = oran(None, model, P6D, "YANLIS")
        b6 = (a6d + a6y) / 2 if n6d and n6y else float("nan")
        a3d, n3d = oran(None, model, P3D, "DOGRU")
        a3y, n3y = oran(None, model, P3Y, "YANLIS")
        b3 = (a3d + a3y) / 2 if n3d and n3y else float("nan")
        p1, _ = oran(None, model, P1, "DOGRU")
        p5, _ = oran(None, model, P5, "YANLIS")
        kaz = b6 - bacc
        if kaz == kaz:
            kazanclar.append(kaz)
        e(f"    {model:<36} {bacc:>6.2f} {b3:>7.2f} {b6:>7.2f} "
          f"{p1:>6.2f} {p5:>6.2f} {kaz:>+7.2f}")

    e()
    e("  bacc   : tum kume, dengeli dogruluk (0.50 = sans)")
    e("  baccP6 : P6_yil(DOGRU) vs P6_degismedi(YANLIS) — kalip etiketi ele veriyor")
    e("  baccP3 : KONTROL. Ayni kalip, yalnizca yil degisiyor; gercek bilgi olcer.")
    e("  P1/P5  : tek sinifli tabakalar. Bunlar BILGI DEGIL, cevap yanliligidir.")

    e()
    e("[2] KARAR")
    if not kazanclar:
        e("  olculemedi.")
    else:
        ort = sum(kazanclar) / len(kazanclar)
        poz = sum(1 for k in kazanclar if k > 0)
        n = len(kazanclar)
        # isaret testi (iki yonlu binom, p=0.5)
        p = min(1.0, 2 * sum(math.comb(n, i) for i in range(poz, n + 1)) / 2 ** n)
        en_kucuk_p = 2 / 2 ** n
        e(f"  ortalama kazanc (baccP6 - bacc): {ort:+.3f}")
        e(f"  pozitif hucre: {poz}/{n}   isaret testi p={p:.3f}")
        if en_kucuk_p > 0.10:
            e(f"  ! {n} hucreyle isaret testinin ulasabilecegi en kucuk p = {en_kucuk_p:.3f};")
            e("    karar buyukluge gore verilir, p yalnizca destekleyicidir.")
        if ort > 0.15 and (p < 0.10 or en_kucuk_p > 0.10):
            e("  => KALIP OKUNUYOR. P6 sonuclari yuzey ipucuyla kirlenmis;")
            e("     F4 oncesi P6 dengelenmeli, aksi halde P6 metrikleri raporlanamaz.")
        elif ort > 0.05:
            e("  => ZAYIF ISARET. Yon dogru ama kanit guclu degil; P6 ayri raporlansin")
            e("     ve sizinti sinirlilik olarak yazilsin.")
        else:
            e("  => KISAYOL KULLANILMIYOR gorunuyor. Sizinti bir TASARIM kusuru olarak")
            e("     kalir (genisletmede duzeltilecek) ama mevcut olcumleri kirletmiyor.")

    e()
    e("[3] NOT")
    e("  Bu test tek basina nedensel degildir: baccP6'nin yuksek olmasi 'kalip")
    e("  okundu' ya da 'metadata sorusu kolay' demek olabilir. Ayrimi kesinlestiren")
    e("  tek sey eksik iki hucreyi uretmektir (yanlis yilli P6_yil -> YANLIS,")
    e("  gercekten degismemis madde -> P6_degismedi DOGRU). O zaman kalip ile")
    e("  etiket arasindaki bag kopar ve olcum dogrudan olur.")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\nyazildi: {a.out}")


if __name__ == "__main__":
    main()
