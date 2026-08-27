# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F4 — PUANLAMA (ON KAYITA gore).

score_local.py neden yeniden yazildi
------------------------------------
  * Eski betik 'altin_etiket' ve 'probe_tipi' sutunlarini okuyordu; v6
    kumesinde bunlar 'gold' ve 'probe'. Oldugu gibi calistirilamaz.
  * [ON KAYIT 3] Asgari kapsam esigi yoktu. F3-a'da %1 ve %21 kapsamli
    hucreler diger hucrelerle ayni tabloda puanlanmisti; bu, cevap
    vermeyen bir modeli iyi gostermenin en kolay yoludur.
  * [ON KAYIT 6] Alt-tur kirilimi yoktu. P5 ve P6 tek satirda toplaniyordu.
  * Dengeli dogruluk, Youden J, d' ve ECE yoktu.
  * E1 vs E2 ESLESMIS karsilastirmasi yoktu — calismanin ASIL sorusu bu.

TEK SINIFLI TABAKA UYARISI
--------------------------
P1 hep DOGRU, P2/P4/P5 hep YANLIS. Bu tabakalarda "dogruluk", bilgi degil
CEVAP YANLILIGI olcer. Betik bunlari 'dogruluk' diye raporlamaz; yerine
    lambda = dogruluk(P1) + dogruluk(P5) - 1
endeksini verir. Yanliligi b olan bir model P1'de b, P5'te 1-b alir ve
lambda = 0 cikar; lambda'nin sifirdan sapmasi yanlilikla aciklanamaz.
Prob ICI dengeli dogruluk yalnizca P3 ve P6'da tanimlidir.

Kullanim:
    python scripts/f4_skor.py
    python scripts/f4_skor.py --varyant B --out sonuclar/f4_metrikler_B.csv
"""
import argparse
import csv
import json
import math
import os
from collections import Counter, defaultdict


def zinv(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    if p <= 0 or p >= 1:
        return 0.0
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - 0.02425:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def wilson(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    z, ph = 1.96, k / n
    d = 1 + z * z / n
    m = (ph + z * z / (2 * n)) / d
    r = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, m - r), min(1.0, m + r))


def mcnemar(b, c):
    """Eslesmis ikili fark. b,c uyusmazlik hucreleri. Iki yonlu p."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default="sonuclar/f4_sonuclar.jsonl")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--varyant", default="A")
    ap.add_argument("--yanit-esigi", type=float, default=0.80,
                    help="EK-1: esik YANIT oranina uygulanir, taahhut oranina degil")
    ap.add_argument("--min-taahhut", type=int, default=30,
                    help="EK-1 madde 2: dogruluk metrikleri icin asgari taahhut sayisi")
    # Cikti adlari VARSAYILAN BIRAKILIRSA girdi adindan turetilir.
    # Gerekce: --jsonl degistirilip --out unutuldugunda ana matrisin
    # metrikleri sessizce EZILIYORDU (det2.jsonl puanlamasi 18 modellik
    # f4_metrikler.csv'yi 2 hucrelik dosyayla degistirdi). Ham jsonl
    # duruyordu, yeniden uretildi; yine de kapiyi kapatiyoruz.
    ap.add_argument("--out", default="")
    ap.add_argument("--rapor", default="")
    a = ap.parse_args()
    kok = os.path.splitext(os.path.basename(a.jsonl))[0]
    dizin = os.path.dirname(a.jsonl) or "sonuclar"
    if not a.out:
        a.out = (os.path.join(dizin, "f4_metrikler.csv") if kok == "f4_sonuclar"
                 else os.path.join(dizin, f"metrikler_{kok}.csv"))
    if not a.rapor:
        a.rapor = (os.path.join(dizin, "f4_rapor.txt") if kok == "f4_sonuclar"
                   else os.path.join(dizin, f"rapor_{kok}.txt"))

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddia = {r["id"]: r for r in csv.DictReader(fh)}
    # PAYDA: kume buyuklugu degil, HUCREDE GERCEKTEN DENENEN madde sayisi.
    # Sinirli kosularda (--sinir ile alinan sondalar) CSV uzunlugunu payda
    # yapmak butun oranlari kucultur: 40 maddelik bir sondada 28 taahhut
    # %6 gibi gorunur, oysa %70'tir. N artik hucre basina hesaplanir.
    N_kume = len(iddia)

    hucre = defaultdict(dict)
    with open(a.jsonl, encoding="utf-8-sig") as fh:
        for satir in fh:
            r = json.loads(satir)
            if r.get("varyant", "A") != a.varyant:
                continue
            hucre[(r["model"], r["kosul"])][str(r["id"])] = r

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 118)
    e(f"RUHSAT-Bench F4 — PUANLAMA  (varyant {a.varyant}, kumede {N_kume} iddia)")
    e("Oranlar HUCREDE DENENEN madde sayisina gore; sinirli kosular dogru okunur.")
    e(f"EK-1 uyarinca: esik YANIT oranina uygulanir; KACINMA bir sonuctur, kapi degildir.")
    e(f"yanit esigi %{100*a.yanit_esigi:.0f} | dogruluk metrikleri icin asgari taahhut n={a.min_taahhut}")
    e("=" * 118)

    satirlar = []
    e()
    e(f"{'model / kosul':<34}{'yanit':>7}{'kacin':>7}{'taahh':>7}{'n_tah':>6}"
      f"{'dogr':>7}{'bacc':>7}{'J':>7}{'dprime':>8}{'ECE':>7}{'AUROC':>7}  durum")
    e("-" * 118)
    for (model, kosul), cevaplar in sorted(hucre.items()):
        N = len(cevaplar)
        commit = {k: v for k, v in cevaplar.items() if v.get("karar") in ("DOGRU", "YANLIS")}
        kapsam = len(commit) / N
        ayr = sum(1 for v in cevaplar.values() if v.get("durum") == "ayristirilamadi")
        kacin = sum(1 for v in cevaplar.values()
                    if v.get("karar") == "EMIN_DEGILIM" or v.get("durum") == "e2_kacinma")
        yanit = (N - ayr) / N
        uyum = yanit >= a.yanit_esigi
        yeterli = len(commit) >= a.min_taahhut
        hit = fa = pos = neg = dogru = 0
        kova = defaultdict(lambda: [0, 0])
        for cid, v in commit.items():
            g = iddia[cid]["gold"]
            k = v["karar"]
            dogru += (k == g)
            if g == "DOGRU":
                pos += 1
                hit += (k == "DOGRU")
            else:
                neg += 1
                fa += (k == "DOGRU")
            gv = v.get("guven")
            if isinstance(gv, int):
                b = min(9, max(0, gv // 10))
                kova[b][0] += 1
                kova[b][1] += (k == g)
        sens = hit / pos if pos else float("nan")
        spec = 1 - fa / neg if neg else float("nan")
        bacc = (sens + spec) / 2 if pos and neg else float("nan")
        J = sens + spec - 1 if pos and neg else float("nan")
        dp = (zinv(min(max(hit / pos, 1 / (2 * pos)), 1 - 1 / (2 * pos)))
              - zinv(min(max(fa / neg, 1 / (2 * neg)), 1 - 1 / (2 * neg)))) if pos and neg else float("nan")
        ece = sum(n_ * abs((d_ / n_) - (b * 10 + 5) / 100)
                  for b, (n_, d_) in kova.items() if n_) / max(sum(n_ for n_, _ in kova.values()), 1)
        taahhut = dogru / len(commit) if commit else float("nan")
        # guven skoru dogrulugu ayirt ediyor mu (AUROC, sira tabanli)
        cift = [(v.get("guven"), v["karar"] == iddia[cid]["gold"])
                for cid, v in commit.items() if isinstance(v.get("guven"), int)]
        auroc = float("nan")
        if cift and 0 < sum(1 for _, y in cift if y) < len(cift):
            poz = [g for g, y in cift if y]
            neg = [g for g, y in cift if not y]
            auroc = sum((1.0 if p > n_ else 0.5 if p == n_ else 0.0)
                        for p in poz for n_ in neg) / (len(poz) * len(neg))

        def f(x, bicim="{:>7.2f}"):
            return bicim.format(x) if yeterli and x == x else ("{:>7}".format("-"))
        e(f"{model + ' / ' + kosul:<34}{yanit:>7.2f}{kacin/N:>7.2f}{kapsam:>7.2f}"
          f"{len(commit):>6}{f(taahhut)}{f(bacc)}{f(J)}{f(dp, '{:>8.2f}')}"
          f"{f(ece, '{:>7.3f}')}{f(auroc)}  "
          f"{'gecerli' if uyum else 'YANIT ESIGI ALTI'}"
          f"{'' if yeterli else '  (n<' + str(a.min_taahhut) + ')'}")
        satirlar.append(dict(model=model, kosul=kosul, varyant=a.varyant,
                             yanit_orani=round(yanit, 4), kacinma_orani=round(kacin / N, 4),
                             taahhut_orani=round(kapsam, 4), n_taahhut=len(commit),
                             taahhut_dogrulugu=round(taahhut, 4) if yeterli else "",
                             dengeli_dogruluk=round(bacc, 4) if yeterli else "",
                             youden_J=round(J, 4) if yeterli else "",
                             d_prime=round(dp, 4) if yeterli else "",
                             ECE=round(ece, 4) if yeterli else "",
                             guven_AUROC=round(auroc, 4) if yeterli and auroc == auroc else "",
                             ayristirilamadi=ayr, puanlanabilir=int(uyum),
                             metrik_yeterli=int(yeterli)))

    gecerli = set()
    for (m, k) in hucre:
        n_h = len(hucre[(m, k)])
        ayr_h = sum(1 for v in hucre[(m, k)].values() if v.get("durum") == "ayristirilamadi")
        if n_h and (n_h - ayr_h) / n_h >= a.yanit_esigi:
            gecerli.add((m, k))
    modeller = sorted({m for m, _ in gecerli})
    bonf = 0.05 / max(len(modeller), 1)

    # ------------------------------------------------------------ DOGRULAYICI
    e()
    e("=" * 100)
    e(f"DOGRULAYICI ANALIZLER   (Bonferroni: {len(modeller)} model, alfa={bonf:.4f})")
    e("=" * 100)
    e()
    e("[1.1-1.2] E1 vs E2, ESLESMIS  (ayni maddeler, ayni model)")
    e("  UYARI: taahhut dogrulugu iki kosulda da cevaplanan ORTAK maddelerde")
    e("  hesaplanir. Cok kacinan modellerde bu kume kucuktur; n_ortak sutununa bakin.")
    e(f"  {'model':<32}{'kapsamE1':>9}{'kapsamE2':>9}{'fark':>7}"
      f"{'n_ortak':>8}{'taahE1':>8}{'taahE2':>8}{'fark':>7}{'McNemar p':>11}")
    for m in modeller:
        if (m, "E1") not in gecerli or (m, "E2") not in gecerli:
            continue
        c1, c2 = hucre[(m, "E1")], hucre[(m, "E2")]
        k1 = {i for i, v in c1.items() if v.get("karar") in ("DOGRU", "YANLIS")}
        k2 = {i for i, v in c2.items() if v.get("karar") in ("DOGRU", "YANLIS")}
        ort = k1 & k2
        d1 = sum(1 for i in ort if c1[i]["karar"] == iddia[i]["gold"])
        d2 = sum(1 for i in ort if c2[i]["karar"] == iddia[i]["gold"])
        b = sum(1 for i in ort if c1[i]["karar"] == iddia[i]["gold"] != c2[i]["karar"])
        c_ = sum(1 for i in ort if c2[i]["karar"] == iddia[i]["gold"] != c1[i]["karar"])
        p = mcnemar(b, c_)
        nn = max(len(c1), len(c2))
        e(f"  {m:<32}{len(k1)/nn:>9.2f}{len(k2)/nn:>9.2f}{(len(k2)-len(k1))/nn:>+7.2f}"
          f"{len(ort):>8}{d1/len(ort):>8.2f}{d2/len(ort):>8.2f}{(d2-d1)/len(ort):>+7.2f}"
          f"{p:>11.4f}{'  *' if p < bonf else ''}")
    e("  * = Bonferroni duzeltmeli esigin altinda")

    # ------------------------------------------------------------ [1.3b]
    e()
    e("[1.3b] CEVAP POLITIKASI KAYMASI   (EK-1 sonrasi eklendi — KESIFSEL)")
    e("  Dogruluk uzerinden McNemar YANILTICI olabilir: bir probda dususu baska")
    e("  probda yukselis dengeleyince toplam degismez ama YANLILIK degismistir.")
    e("  Bu yuzden dogrudan cevap dagilimina ve ortak maddedeki DONME oranina bakilir.")
    e(f"  {'model':<32}{'E1 P(D)':>9}{'E2 P(D)':>9}{'kayma':>8}{'n_ortak':>8}{'donen':>8}{'%':>7}")
    for m in modeller:
        if (m, "E1") not in gecerli or (m, "E2") not in gecerli:
            continue
        c1, c2 = hucre[(m, "E1")], hucre[(m, "E2")]
        k1 = {i for i, v in c1.items() if v.get("karar") in ("DOGRU", "YANLIS")}
        k2 = {i for i, v in c2.items() if v.get("karar") in ("DOGRU", "YANLIS")}
        if not k1 or not k2:
            continue
        p1 = sum(1 for i in k1 if c1[i]["karar"] == "DOGRU") / len(k1)
        p2 = sum(1 for i in k2 if c2[i]["karar"] == "DOGRU") / len(k2)
        ort = k1 & k2
        don = sum(1 for i in ort if c1[i]["karar"] != c2[i]["karar"])
        e(f"  {m:<32}{p1:>9.2f}{p2:>9.2f}{p2-p1:>+8.2f}{len(ort):>8}{don:>8}"
          f"{100*don/max(len(ort),1):>6.0f}%")
    e("  Yuksek donme orani: kacinma secenegi kaldirilinca model sadece CEVAP")
    e("  VERMIYOR, VERDIGI CEVABI da degistiriyor. Bu durumda E2 olcumu ayni")
    e("  bilginin zorunlu ifadesi degil, FARKLI bir cevap politikasidir.")

    e()
    e("[1.3c] DEJENERE HUCRELER  (taahhut edilenlerin >=%90'i tek etiket)")
    dej = 0
    for (m, k) in sorted(gecerli):
        com = [v["karar"] for v in hucre[(m, k)].values()
               if v.get("karar") in ("DOGRU", "YANLIS")]
        if len(com) < a.min_taahhut:
            continue
        en = Counter(com).most_common(1)[0]
        if en[1] / len(com) >= 0.90:
            dej += 1
            e(f"    {m:<32} {k}  {en[0]} %{100*en[1]/len(com):.0f}  (n={len(com)})")
    e(f"  dejenere hucre: {dej}. Bu hucrelerde dogruluk turu metrikler bilgi degil")
    e("  cevap yanliligi olcer; dengeli dogruluk tanim geregi 0.50'ye yakin cikar.")

    e()
    e("[1.4] lambda = dogruluk(P1) + dogruluk(P5) - 1   (yanlilikten arindirilmis bilgi)")
    e("  lambda ~ 0 : model yalnizca cevap yanliligiyla calisiyor")
    e(f"  {'model / kosul':<40}{'P1(D)':>8}{'P5(Y)':>8}{'lambda':>9}")
    for (m, k) in sorted(gecerli):
        cv = hucre[(m, k)]
        p1 = [i for i in cv if iddia[i]["probe"] == "P1_dogrudan"]
        p5 = [i for i in cv if iddia[i]["probe"] == "P5_capraz"]
        a1 = [cv[i]["karar"] == "DOGRU" for i in p1 if cv[i].get("karar") in ("DOGRU", "YANLIS")]
        a5 = [cv[i]["karar"] == "YANLIS" for i in p5 if cv[i].get("karar") in ("DOGRU", "YANLIS")]
        if not a1 or not a5:
            continue
        x, y = sum(a1)/len(a1), sum(a5)/len(a5)
        e(f"  {m + ' / ' + k:<40}{x:>8.2f}{y:>8.2f}{x+y-1:>+9.3f}")

    # ------------------------------------------------------------ [1.5]
    e()
    e("[1.5] KACINMANIN BILGI DEGERI   (EK-1 madde 3 — KESIFSEL, on kayitta yoktu)")
    e("  Modelin E1'de KACINDIGI maddelerde E2 dogrulugu ile TAAHHUT ETTIGI")
    e("  maddelerde E2 dogrulugunu karsilastirir. Delta>0 ise kacinma bilgi tasir.")
    e(f"  {'model':<32}{'n_tah':>6}{'A_tah':>8}{'n_kac':>7}{'A_kac':>8}{'Delta':>8}{'p':>9}")
    for m in sorted({m for m, _ in gecerli}):
        if (m, "E1") not in gecerli or (m, "E2") not in gecerli:
            continue
        c1, c2 = hucre[(m, "E1")], hucre[(m, "E2")]
        tah = [i for i, v in c1.items() if v.get("karar") in ("DOGRU", "YANLIS")]
        kac = [i for i, v in c1.items() if v.get("karar") == "EMIN_DEGILIM"]
        def dog(kume):
            g = [i for i in kume if c2.get(i, {}).get("karar") in ("DOGRU", "YANLIS")]
            return (sum(1 for i in g if c2[i]["karar"] == iddia[i]["gold"]), len(g))
        xt, nt = dog(tah)
        xk, nk = dog(kac)
        if nt < 10 or nk < 10:
            e(f"  {m:<32}{nt:>6}{'-':>8}{nk:>7}{'-':>8}   (bir taraf n<10)")
            continue
        pt, pk = xt / nt, xk / nk
        pb = (xt + xk) / (nt + nk)
        se = math.sqrt(pb * (1 - pb) * (1 / nt + 1 / nk))
        z = (pt - pk) / se if se else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        e(f"  {m:<32}{nt:>6}{pt:>8.2f}{nk:>7}{pk:>8.2f}{pt-pk:>+8.2f}{p:>9.4f}"
          f"{'  *' if p < 0.05 else ''}")
    e("  * p<0.05 (duzeltmesiz). Delta>0: model cevapladigi maddelerde daha basarili;")
    e("  yani kacinma ayirt edici. Delta~0: kacinma yalnizca genel cekingenlik.")

    # ------------------------------------------------------------ [1.6]
    e()
    e("[1.6] DUYARLILIK — ORIJINAL ON KAYIT KURALI (esik TAAHHUT oranina)")
    e("  Kural harfiyen uygulansaydi hangi hucreler elenirdi:")
    elenen = []
    for (m, k) in sorted(hucre):
        cm = sum(1 for v in hucre[(m, k)].values() if v.get("karar") in ("DOGRU", "YANLIS"))
        if cm / N < a.yanit_esigi:
            elenen.append(f"{m}/{k} ({cm/N:.2f})")
    e(f"  elenen hucre: {len(elenen)}")
    for x in elenen:
        e(f"    {x}")
    e("  Bunlarin cogu KACINDIGI icin elenirdi; EK-1'in duzelttigi hata budur.")

    # ------------------------------------------------------------ KESIFSEL
    e()
    e("=" * 100)
    e("KESIFSEL — PROB VE ALT-TUR KIRILIMI")
    e("  ON KAYIT 2: bunlar hipotez testi DEGILDIR; guven araliklariyla betimseldir.")
    e("  Tek sinifli tabakalarda gosterilen deger 'altin sinifi secme orani'dir,")
    e("  bilgi olcusu degildir. Prob ici dengeli dogruluk yalnizca P3 ve P6'da tanimli.")
    e("=" * 100)
    for (m, k) in sorted(gecerli):
        cv = hucre[(m, k)]
        e()
        e(f"  {m} / {k}")
        for alan in ("probe", "probe_alt"):
            gr = defaultdict(lambda: [0, 0])
            for i, v in cv.items():
                if v.get("karar") not in ("DOGRU", "YANLIS"):
                    continue
                gr[iddia[i].get(alan, "")][0] += 1
                gr[iddia[i].get(alan, "")][1] += (v["karar"] == iddia[i]["gold"])
            for ad, (n_, d_) in sorted(gr.items()):
                if not ad or (alan == "probe_alt" and n_ == 0):
                    continue
                lo, hi = wilson(d_, n_)
                tek = len({iddia[i]["gold"] for i in cv if iddia[i].get(alan) == ad}) == 1
                e(f"    {'' if alan=='probe' else '    '}{ad:<24}{d_:>4}/{n_:<4}"
                  f"{d_/n_:>7.2f}  [{lo:.2f}, {hi:.2f}]"
                  f"{'   (tek sinifli)' if tek else ''}")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    if satirlar:
        with open(a.out, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(satirlar[0].keys()))
            w.writeheader()
            w.writerows(satirlar)
        print(f"\nyazildi: {a.out}")
    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.rapor}")


if __name__ == "__main__":
    main()
