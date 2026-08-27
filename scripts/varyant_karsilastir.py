# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F4 — VARYANTLAR ARASI KARARLILIK (EK-2).

SORU
----
Ayni model, ayni 473 madde, ayni kosul. Degisen tek sey sistem promptunun
IFADESI. Olcum ne kadar kayiyor?

Bu bir tutarlilik kontrolu DEGILDIR (on kayit oyle diyordu, EK-2 duzeltti).
Kontrollu bir manipulasyondur ve sonucu olcumun kararliligi hakkindadir.

OLCUTLER — iki aileye ayrilir
-----------------------------
  YANLILIK AILESI (cevap politikasini olcer)
      kacinma orani
      P(DOGRU | taahhut)
      taahhut dogrulugu
  BILGI AILESI (yanliliktan arindirilmis)
      lambda = dogruluk(P1) + dogruluk(P5) - 1

Beklenen desen: yanlilik ailesi savrulur, lambda savrulmaz. Cunku
yanliligi b olan bir model P1'de b, P5'te 1-b alir ve lambda = 0 verir;
b degisse bile lambda degismez. Lambda'nin sifira YAPISIK kalmasi
"bilgi yok" demektir ve prompt bunu degistiremez.

Bu dogruysa aktarilabilir sonuc su olur: YANLILIK DUZELTMESI ICERMEYEN
HICBIR METRIK MODELI OLCMEZ, PROMPTU OLCER.

DONME TESTI
-----------
Iki varyantta da CEVAPLANAN maddelerde kararin degisip degismedigi
sayilir ve McNemar ile test edilir. Yuksek donme, iki varyantin ayni
maddede farkli sonuca vardigini gosterir — model degismemistir, olcum
degismistir.

Kullanim:
    python scripts/varyant_karsilastir.py
"""
import argparse
import csv
import json
import math
import os
import statistics
from collections import defaultdict


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default="sonuclar/f4_sonuclar.jsonl")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--out", default="sonuclar/varyant_kararlilik.txt")
    ap.add_argument("--csv-out", default="sonuclar/varyant_kararlilik.csv")
    ap.add_argument("--min-taahhut", type=int, default=30,
                    help="ozette yalnizca IKI varyantta da bu kadar taahhut olan hucreler")
    a = ap.parse_args()

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddia = {r["id"]: r for r in csv.DictReader(fh)}
    N = len(iddia)

    h = defaultdict(dict)
    with open(a.jsonl, encoding="utf-8-sig") as fh:
        for satir in fh:
            r = json.loads(satir)
            h[(r["model"], r["kosul"], r.get("varyant", "A"))][str(r["id"])] = r

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    KESIN = ("DOGRU", "YANLIS")

    def olc(c):
        com = {i: v["karar"] for i, v in c.items() if v.get("karar") in KESIN}
        if not com:
            return None
        kac = sum(1 for v in c.values() if v.get("karar") == "EMIN_DEGILIM") / N
        pD = sum(1 for k in com.values() if k == "DOGRU") / len(com)
        dog = sum(1 for i, k in com.items() if k == iddia[i]["gold"]) / len(com)
        p1 = [i for i in com if iddia[i]["probe"] == "P1_dogrudan"]
        p5 = [i for i in com if iddia[i]["probe"] == "P5_capraz"]
        lam = None
        if p1 and p5:
            lam = (sum(1 for i in p1 if com[i] == "DOGRU") / len(p1)
                   + sum(1 for i in p5 if com[i] == "YANLIS") / len(p5) - 1)
        return dict(n=len(com), kac=kac, pD=pD, dog=dog, lam=lam, com=com)

    hucreler = sorted({(m, k) for (m, k, v) in h if (m, k, "A") in h and (m, k, "B") in h})
    e("=" * 104)
    e("RUHSAT-Bench F4 — VARYANTLAR ARASI KARARLILIK  (EK-2, KESIFSEL)")
    e(f"iki varyantta da kosulmus hucre: {len(hucreler)}")
    e("=" * 104)
    e()
    e(f"{'model / kosul':<32}{'kacinma A>B':>13}{'P(D) A>B':>13}{'dogruluk A>B':>14}"
      f"{'lambda A>B':>14}{'donen':>9}{'p':>9}")
    e("-" * 104)

    satirlar, d_kac, d_pD, d_dog, d_lam, disarida = [], [], [], [], [], []
    m_kac, m_pD, m_dog, m_lam = [], [], [], []
    for (m, k) in hucreler:
        A, B = olc(h[(m, k, "A")]), olc(h[(m, k, "B")])
        if not A or not B:
            continue
        ort = set(A["com"]) & set(B["com"])
        don = sum(1 for i in ort if A["com"][i] != B["com"][i])
        b_ = sum(1 for i in ort if A["com"][i] == "DOGRU" and B["com"][i] == "YANLIS")
        c_ = sum(1 for i in ort if A["com"][i] == "YANLIS" and B["com"][i] == "DOGRU")
        p = mcnemar(b_, c_)
        lam_txt = ("{:.2f}>{:.2f}".format(A["lam"], B["lam"])
                   if A["lam"] is not None and B["lam"] is not None else "     -")
        e(f"{m + ' / ' + k:<32}"
          f"{A['kac']:>6.2f}>{B['kac']:<6.2f}"
          f"{A['pD']:>6.2f}>{B['pD']:<6.2f}"
          f"{A['dog']:>7.2f}>{B['dog']:<6.2f}"
          f"{lam_txt:>14}"
          f"{don:>5}/{len(ort):<4}{p:>9.4f}{'  *' if p < 0.05 else ''}")
        # OZETE YALNIZCA YETERLI TAAHHUTLU HUCRELER GIRER.
        # Gerekce: lambda P1 ve P5 alt kumelerinden hesaplanir; toplam taahhut
        # 6 ya da 9 oldugunda lambda birkac gozleme dayanir ve savrulmasi
        # olcum gurultusudur, prompt etkisi degildir. Bu filtre olmadan
        # ozet, en zayif hucrelerin gurultusuyle yonlendirilir.
        yeterli = A["n"] >= a.min_taahhut and B["n"] >= a.min_taahhut
        if yeterli:
            d_kac.append(abs(A["kac"] - B["kac"]))
            d_pD.append(abs(A["pD"] - B["pD"]))
            d_dog.append(abs(A["dog"] - B["dog"]))
            m_kac.append((A["kac"] + B["kac"]) / 2)
            m_pD.append(abs((A["pD"] - 0.5) + (B["pD"] - 0.5)) / 2)
            m_dog.append(abs((A["dog"] - 0.5) + (B["dog"] - 0.5)) / 2)
            if A["lam"] is not None and B["lam"] is not None:
                d_lam.append(abs(A["lam"] - B["lam"]))
                m_lam.append(abs(A["lam"] + B["lam"]) / 2)
        else:
            disarida.append(f"{m}/{k} (n_A={A['n']}, n_B={B['n']})")
        satirlar.append(dict(model=m, kosul=k,
                             kacinma_A=round(A["kac"], 4), kacinma_B=round(B["kac"], 4),
                             pDOGRU_A=round(A["pD"], 4), pDOGRU_B=round(B["pD"], 4),
                             dogruluk_A=round(A["dog"], 4), dogruluk_B=round(B["dog"], 4),
                             lambda_A=(round(A["lam"], 4) if A["lam"] is not None else ""),
                             lambda_B=(round(B["lam"], 4) if B["lam"] is not None else ""),
                             n_A=A["n"], n_B=B["n"],
                             n_ortak=len(ort), donen=don,
                             donme_orani=round(don / max(len(ort), 1), 4),
                             mcnemar_p=round(p, 6),
                             ozete_dahil=int(yeterli)))

    lam_buyukluk = statistics.mean(m_lam) if m_lam else 0.0
    pD_buyukluk = statistics.mean(m_pD) if m_pD else 0.0
    dog_buyukluk = statistics.mean(m_dog) if m_dog else 0.0
    kac_buyukluk = statistics.mean(m_kac) if m_kac else 0.0
    e()
    e("=" * 104)
    e("OZET — OLCUTLER VARYANT DEGISIMINE NE KADAR DAYANIKLI")
    e(f"  Ozete giren hucre: {len(d_pD)}/{len(hucreler)}  "
      f"(iki varyantta da taahhut >= {a.min_taahhut})")
    for x in disarida:
        e(f"    disarida: {x}")
    e("=" * 104)
    # MUTLAK savrulma tek basina yaniltici: sifira yapisik bir olcut
    # savrulamaz. Olcutun KENDI buyuklugune gore de bakilir.
    buyukluk = {"lambda": lam_buyukluk, "P(DOGRU | taahhut)": pD_buyukluk,
                "taahhut dogrulugu": dog_buyukluk, "kacinma orani": kac_buyukluk}
    e(f"  {'olcut':<30}{'aile':<10}{'ort |A-B|':>10}{'medyan':>9}"
      f"{'en buyuk':>10}{'olcut duzeyi':>14}{'goreli':>9}")
    for ad, aile, d in (("kacinma orani", "yanlilik", d_kac),
                        ("P(DOGRU | taahhut)", "yanlilik", d_pD),
                        ("taahhut dogrulugu", "yanlilik", d_dog),
                        ("lambda", "BILGI", d_lam)):
        if not d:
            continue
        duz = buyukluk.get(ad) or 0.0
        gor = (statistics.mean(d) / duz) if duz > 1e-9 else float("nan")
        e(f"  {ad:<30}{aile:<10}{statistics.mean(d):>10.3f}"
          f"{statistics.median(d):>9.3f}{max(d):>10.3f}{duz:>14.3f}"
          f"{gor:>9.2f}" if duz > 1e-9 else
          f"  {ad:<30}{aile:<10}{statistics.mean(d):>10.3f}"
          f"{statistics.median(d):>9.3f}{max(d):>10.3f}{duz:>14.3f}{'   -':>9}")
    e("  'olcut duzeyi' = olcutun iki varyanttaki ortalama BUYUKLUGU.")
    e("  'goreli' = ort |A-B| / olcut duzeyi. Sifira yapisik bir olcutun")
    e("  mutlak savrulmasi kucuk cikar; bu kararlilik DEGIL, yer olmamasidir.")

    if d_lam and d_pD:
        oran = statistics.mean(d_pD) / max(statistics.mean(d_lam), 1e-9)
        e()
        e(f"  P(DOGRU) savrulmasi / lambda savrulmasi = x{oran:.2f}")
        if len(d_pD) < 4:
            e()
            e("  ! HUCRE SAYISI < 4. Tek bir ozet hukmu VERILMEZ; sayilar")
            e("    yukaridaki tablodan okunmalidir. Bu kadar az hucrede oran")
            e("    tek bir modelin davranisini yansitir, bir desen degil.")
        elif oran > 3:
            e("  => YANLILIK OLCUTLERI SAVRULUYOR, LAMBDA GORELI OLARAK DAHA KARARLI.")
            e("     DIKKAT: lambda sifira yapisiksa mutlak savrulmasi zaten kucuk")
            e("     cikar. 'goreli' sutununa bakmadan kararlilik iddia etmeyin.")
        else:
            e("  => Yanlilik olcutleri lambda'dan daha kararli gorunuyor.")
            e("     Bu, yanliligin PROMPTA DUYARSIZ oldugu anlamina gelir ve")
            e("     zayif modellerdeki desenin TERSIDIR. Model duzeyleri arasi")
            e("     karsilastirma icin ayri kosulardaki bu sayiyi yan yana koyun.")

    e()
    e("NOT (EK-2 madde 3): iki prompt, prompt uzayindan alinmis IKI NOKTADIR.")
    e("Savrulmanin buyuklugu hakkinda ALT SINIR verir; dagilimi hakkinda bilgi")
    e("vermez. Varyant B yalnizca 6 modelde kosuldugu icin bulgu bu altkumeyle")
    e("sinirlidir.")

    if satirlar:
        os.makedirs(os.path.dirname(a.csv_out) or ".", exist_ok=True)
        with open(a.csv_out, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(satirlar[0].keys()))
            w.writeheader()
            w.writerows(satirlar)
        print(f"\nyazildi: {a.csv_out}")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.out}")


if __name__ == "__main__":
    main()
