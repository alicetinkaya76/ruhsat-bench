# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — SONDA KARSILASTIRMA  (max_token pozitif kontrolu)

SORU
----
Istem B, --max-token 32 ile arsiv A kollarindan ~35 kat fazla kesiliyor
(3/80 vs 3/2838). 128'e cikarmak kesilmeyi sifirliyor. Fakat sinir
yukseltmek KARARLARI degistiriyorsa, A@32 ile B@128 karsilastirmasi
istem etkisiyle butce etkisini karistirir.

MANTIK
------
Sicaklik gonderilmediginden iki kosu ZATEN belirlenimsizdir. B@32 ile
B@128, ayni kosulun iki bagimsiz kosusudur. O halde uyusmalari KOL ICI
TEKRAR GURULTUSU kadar olmalidir.

    Olculmus referans (arsiv, frontC k1/k2/k3 ikilileri):
        kol ici etiket uyusmasi 0.9070  [0.9017 - 0.9133]

    Uyusma bu bandin icindeyse  -> max_token davranis parametresi DEGIL,
                                   yalnizca ust sinirdir. 128'e gecilir.
    Belirgin altindaysa         -> max_token cikti daGilimini degistiriyor.
                                   A kolu da 128'de yeniden kosulmalidir.

Ek olarak: 32'de KESILEN maddelerin 128'de ne yaptigi ayri raporlanir.
Bunlar EK-3'teki kayip yapisinin ta kendisidir — madde ancak model kisa
cevap verdiginde puanlaniyorsa kayip rastgele olmaz.

KULLANIM
--------
    python -u scripts\\sonda_karsilastir.py `
        --a sonuclar\\sonda_B32.jsonl --b sonuclar\\sonda_B128.jsonl

    # istege bagli: ayni maddelerde arsivlenmis A kolu ile de karsilastir
    python -u scripts\\sonda_karsilastir.py `
        --a sonuclar\\sonda_B32.jsonl --b sonuclar\\sonda_B128.jsonl `
        --arsiv sonuclar\\frontC_k1.jsonl
"""
import argparse
import collections
import json
import math
import os
import sys

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                       # noqa: BLE001
        pass

REFERANS_ALT, REFERANS_UST = 0.9017, 0.9133      # arsivden olculmus kol ici band
KESIK = ("max_tokens", "length")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def yukle(yol):
    d = {}
    with open(yol, encoding="utf-8-sig") as fh:
        for s in fh:
            s = s.strip()
            if not s:
                continue
            r = json.loads(s)
            d[(r["kosul"], r["id"])] = r
    return d


def ozet(ad, d):
    n = len(d)
    kes = sum(1 for r in d.values() if r.get("bitis_sebebi") in KESIK)
    ayr = sum(1 for r in d.values() if r.get("karar") in ("DOGRU", "YANLIS", "EMIN_DEGILIM"))
    kac = sum(1 for r in d.values() if r.get("karar") == "EMIN_DEGILIM")
    e1 = [r for r in d.values() if r["kosul"] == "E1"]
    lo, hi = wilson(kes, n)
    print(f"  {ad:<14} n={n:<5} kesilen={kes:<3} ({kes/n:.4f}) [%95 {lo:.4f}-{hi:.4f}]"
          f"  yanit={ayr/n:.4f}  kacinma(E1)="
          f"{sum(1 for r in e1 if r.get('karar')=='EMIN_DEGILIM')/max(len(e1),1):.4f}")
    return kes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="dusuk max_token kosusu")
    ap.add_argument("--b", required=True, help="yuksek max_token kosusu")
    ap.add_argument("--arsiv", default=None, help="istege bagli ucuncu kosu")
    ap.add_argument("--goster", type=int, default=10)
    a = ap.parse_args()

    A, B = yukle(a.a), yukle(a.b)
    print("=" * 78)
    print("SONDA KARSILASTIRMA — max_token pozitif kontrolu")
    print("=" * 78)
    print(f"\nKOSU OZETLERI  ({os.path.basename(a.a)} vs {os.path.basename(a.b)})")
    kes_a = ozet(os.path.basename(a.a), A)
    ozet(os.path.basename(a.b), B)

    ortak = sorted(set(A) & set(B))
    if not ortak:
        print("\n! Ortak madde yok. Ayni --sinir ile kosuldugundan emin olun.")
        sys.exit(1)

    # ---- 1) 32'de kesilen maddeler 128'de ne yapti
    kesikler = [k for k in ortak if A[k].get("bitis_sebebi") in KESIK]
    print(f"\n1) 32'DE KESILEN {len(kesikler)} MADDE, 128'DE:")
    if not kesikler:
        print("    (kesilen madde yok)")
    for k in kesikler:
        ra, rb = A[k], B[k]
        print(f"    {k[0]}/{k[1]}  32: karar={ra.get('karar')} durum={ra.get('durum')}"
              f" ham={str(ra.get('ham'))[:34]!r}")
        print(f"    {'':<{len(k[0])+len(str(k[1]))+2}}  128: karar={rb.get('karar')}"
              f" durum={rb.get('durum')} bitis={rb.get('bitis_sebebi')}")

    # ---- 2) IKI KOSUDA DA AYRISAN maddelerde etiket uyusmasi
    ikisi = [k for k in ortak
             if A[k].get("karar") in ("DOGRU", "YANLIS", "EMIN_DEGILIM")
             and B[k].get("karar") in ("DOGRU", "YANLIS", "EMIN_DEGILIM")]
    ayni = sum(1 for k in ikisi if A[k]["karar"] == B[k]["karar"])
    oran = ayni / len(ikisi) if ikisi else float("nan")
    lo, hi = wilson(ayni, len(ikisi))
    print(f"\n2) ETIKET UYUSMASI (ikisinde de ayrisan {len(ikisi)} madde)")
    print(f"    uyusma = {ayni}/{len(ikisi)} = {oran:.4f}   [%95 {lo:.4f} - {hi:.4f}]")
    print(f"    referans kol ici band (arsiv): {REFERANS_ALT:.4f} - {REFERANS_UST:.4f}")

    gv = [abs((A[k].get("guven") or 0) - (B[k].get("guven") or 0)) for k in ikisi]
    print(f"    ortalama |guven farki| = {sum(gv)/len(gv):.2f}"
          f"  (arsiv kol ici referans ~2.5)")

    print("\n3) KARAR DAGILIMLARI")
    for ad, d in ((os.path.basename(a.a), A), (os.path.basename(a.b), B)):
        c = collections.Counter(d[k].get("karar") for k in ortak)
        print(f"    {ad:<20}{dict(c)}")

    farklar = [k for k in ikisi if A[k]["karar"] != B[k]["karar"]]
    if farklar:
        print(f"\n4) UYUSMAYAN {len(farklar)} MADDE (ilk {a.goster})")
        for k in farklar[:a.goster]:
            print(f"    {k[0]}/{k[1]}  32={A[k]['karar']}({A[k].get('guven')})"
                  f"  128={B[k]['karar']}({B[k].get('guven')})")

    if a.arsiv:
        C = yukle(a.arsiv)
        o3 = [k for k in ikisi if k in C
              and C[k].get("karar") in ("DOGRU", "YANLIS", "EMIN_DEGILIM")]
        if o3:
            ua = sum(1 for k in o3 if A[k]["karar"] == C[k]["karar"]) / len(o3)
            ub = sum(1 for k in o3 if B[k]["karar"] == C[k]["karar"]) / len(o3)
            print(f"\n5) ARSIV A KOLU ILE ({os.path.basename(a.arsiv)}, n={len(o3)})")
            print(f"    A@32  ile uyusma: {ua:.4f}")
            print(f"    B@128 ile uyusma: {ub:.4f}")
            print("    Bunlar FARKLI ISTEMLER; uyusmanin kol ici bandin ALTINDA")
            print("    olmasi BEKLENIR ve istem etkisinin varligini gosterir.")

    # ---- HUKUM
    print("\n" + "=" * 78)
    if math.isnan(oran):
        print("HUKUM: yeterli veri yok.")
        sys.exit(1)
    if hi < REFERANS_ALT:
        print("HUKUM: uyusma kol ici bandin ALTINDA (guven araligi bandi kesmiyor).")
        print("  max_token cikti dagilimini degistiriyor. B'yi 128'de kosarsaniz")
        print("  A kolunu da 128'de yeniden kosmalisiniz; aksi halde istem etkisi")
        print("  ile butce etkisi ayirt edilemez.")
        sys.exit(2)
    print("HUKUM: uyusma kol ici tekrar gurultusuyle uyumlu.")
    print("  max_token bir DAVRANIS parametresi degil, UST SINIRDIR.")
    print(f"  32'de kesilen {kes_a} madde 128'de kurtariliyor ve kayip yapisi")
    print("  (EK-3'teki gibi kolay maddelere yanli olma riski) ortadan kalkiyor.")
    print("  ONERI: B kolu 128'de uc kez kosulur. Karsilastirilabilirligi")
    print("  kanitlamak icin A kolunda TEK bir 128 kosusu daha yapilip")
    print("  arsivlenmis A@32 cogunlugu ile uyusmasi raporlanir.")


if __name__ == "__main__":
    main()
