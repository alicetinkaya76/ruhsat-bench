# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — konsensus on-tarama yonteminin dogrulama benzetimi.

Soru: "Modellerin cogunlugu altina karsi cikiyorsa altin suphelidir" kurali gercekten
altin hatasini mi buluyor, yoksa modellerin yanit yanliligini mi olcuyor?

Yontem: gercek kosumdan (konsensus_tani.csv) her model x kosul hucresinin
  c   = kapsam
  p1  = P(DOGRU der | gercek etiket DOGRU)      [= acc_D]
  p0  = P(DOGRU der | gercek etiket YANLIS)     [= 1 - acc_Y]
parametreleri okunur. Bu parametreler yanliligi da kapsar: hep-YANLIS diyen bir
model p1=p0=0 olur. Ardindan bilinen sayida altin hatasi ENJEKTE edilmis sentetik
setler uretilir (enjekte edilen maddede kayitli altin yanlistir; bilgili modeller
dogru etiketi verdikleri icin kayitli altina karsi cikarlar) ve iki tarama
karsilastirilir:
  v1  naif esit-oy cogunlugu (E2 tercihli)
  v2  dejenere/bilgisiz hucreleri eleyen, Youden J agirlikli oylama

Rapor edilen: geri-cagirma (enjekte hatalarin ne kadari bayraklandi), kesinlik,
ve SINIF ASIMETRISI (DOGRU-altin ile YANLIS-altin bayrak orani farki). Asimetri
yontemin altin hatasi yerine yanlilik olctugunun dogrudan gostergesidir.

Kullanim:
    python scripts/konsensus_dogrulama.py
    python scripts/konsensus_dogrulama.py --tekrar 200 --hata-orani 0.03
"""
import argparse
import csv
import os
import random
from collections import Counter

# konsensus_tani.csv yoksa kullanilacak varsayilan profiller (pilot gozlemi)
VARSAYILAN = [
    ("gemma3:4b", "E2", 1.00, 0.65, 0.37),
    ("gemma3:4b", "E1", 0.76, 0.58, 0.42),
    ("llama3.2:3b-q5", "E2", 1.00, 0.00, 0.00),
    ("llama3.2:3b-q5", "E1", 0.18, 0.00, 0.00),
    ("gemma3:12b", "E2", 1.00, 0.14, 0.12),
    ("gemma3:12b", "E1", 0.71, 0.68, 0.30),
    ("qwen2.5:14b", "E2", 1.00, 0.69, 0.22),
    ("qwen2.5:14b", "E1", 0.09, 0.74, 0.32),
    ("qwen2.5:7b-q4", "E2", 1.00, 0.81, 0.80),
    ("qwen2.5:7b-q4", "E1", 0.53, 0.60, 0.44),
]


def profil_yukle(path):
    if not path or not os.path.exists(path):
        return VARSAYILAN, "varsayilan (pilot gozlemi)"
    out = []
    with open(path, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            try:
                c = float(r["kapsam"])
                ad = float(r["acc_DOGRU"])
                ay = float(r["acc_YANLIS"])
            except (ValueError, KeyError):
                continue
            out.append((r["model"], r["kosul"], c, ad, 1.0 - ay))
    return (out, path) if out else (VARSAYILAN, "varsayilan (pilot gozlemi)")


def oyla_v1(oylar, kayitli_gold, esik):
    """naif: model basina E2 tercihli tek oy, esit agirlik."""
    bayrak = set()
    for cid, g in kayitli_gold.items():
        kararlar = []
        for m in {m for (m, _) in oylar}:
            karar = oylar.get((m, "E2"), {}).get(cid) or oylar.get((m, "E1"), {}).get(cid)
            if karar:
                kararlar.append(karar)
        if len(kararlar) >= 3:
            if sum(1 for x in kararlar if x != g) / len(kararlar) >= esik:
                bayrak.add(cid)
    return bayrak


def oyla_v2(oylar, kayitli_gold, esik, dejenere, min_kapsam, min_j, min_oy, n):
    """elemeli + J agirlikli."""
    tani = {}
    for anahtar, d in oylar.items():
        if not d:
            continue
        dag = Counter(d.values())
        baskin = max(dag.values()) / len(d)
        dt = sum(1 for i in d if kayitli_gold[i] == "DOGRU")
        yt = sum(1 for i in d if kayitli_gold[i] == "YANLIS")
        if not dt or not yt:
            continue
        ad = sum(1 for i, k in d.items() if kayitli_gold[i] == "DOGRU" and k == "DOGRU") / dt
        ay = sum(1 for i, k in d.items() if kayitli_gold[i] == "YANLIS" and k == "YANLIS") / yt
        j = 2 * ((ad + ay) / 2) - 1
        gecerli = (len(d) / n >= min_kapsam) and (baskin < dejenere) and (j >= min_j)
        tani[anahtar] = (j, gecerli)
    en_iyi = {}
    for (m, k), (j, gecerli) in tani.items():
        if gecerli and (m not in en_iyi or j > tani[(m, en_iyi[m])][0]):
            en_iyi[m] = k
    secili = [(m, k) for m, k in en_iyi.items()]
    esnek_min = min_oy if len(secili) >= min_oy else max(2, len(secili))
    bayrak = set()
    for cid, g in kayitli_gold.items():
        tw, kw, ns = 0.0, 0.0, 0
        for m, k in secili:
            karar = oylar[(m, k)].get(cid)
            if not karar:
                continue
            w = max(tani[(m, k)][0], 0.01)
            tw += w
            ns += 1
            if karar != g:
                kw += w
        if ns >= esnek_min and tw > 0 and kw / tw >= esik:
            bayrak.add(cid)
    return bayrak, len(secili)


def tur(profiller, n, hata_orani, esik, rnd, **kw):
    kayitli, gercek = {}, {}
    for i in range(1, n + 1):
        g = "DOGRU" if i % 2 else "YANLIS"
        kayitli[str(i)] = g
        gercek[str(i)] = g
    hatali = set()
    d_ids = [i for i in kayitli if kayitli[i] == "DOGRU"]
    y_ids = [i for i in kayitli if kayitli[i] == "YANLIS"]
    k = max(1, int(n * hata_orani / 2))
    for havuz in (d_ids, y_ids):
        for i in rnd.sample(havuz, k):
            hatali.add(i)
            gercek[i] = "YANLIS" if kayitli[i] == "DOGRU" else "DOGRU"

    oylar = {}
    for (m, ks, c, p1, p0) in profiller:
        d = {}
        for cid in kayitli:
            if rnd.random() > c:
                continue
            p = p1 if gercek[cid] == "DOGRU" else p0
            d[cid] = "DOGRU" if rnd.random() < p else "YANLIS"
        oylar[(m, ks)] = d

    b1 = oyla_v1(oylar, kayitli, esik)
    b2, n_sec = oyla_v2(oylar, kayitli, esik, n=n, **kw)
    br = set(rnd.sample(sorted(kayitli), min(len(b2), n)))  # ayni buyuklukte rastgele secim

    def olc(b):
        tp = b & hatali
        d_tp = sum(1 for i in tp if kayitli[i] == "DOGRU")
        y_tp = sum(1 for i in tp if kayitli[i] == "YANLIS")
        d_b = sum(1 for i in b if kayitli[i] == "DOGRU")
        y_b = sum(1 for i in b if kayitli[i] == "YANLIS")
        asim = abs(d_b / (n / 2) - y_b / (n / 2)) * 100
        return dict(bayrak=len(b), geri=len(tp) / len(hatali) * 100,
                    geri_d=d_tp / k * 100, geri_y=y_tp / k * 100,
                    kesinlik=len(tp) / max(len(b), 1) * 100, asimetri=asim)

    return olc(b1), olc(b2), olc(br), n_sec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tani", default="sonuclar/konsensus_tani.csv")
    ap.add_argument("--n", type=int, default=486)
    ap.add_argument("--hata-orani", type=float, default=0.03)
    ap.add_argument("--tekrar", type=int, default=200)
    ap.add_argument("--esik", type=float, default=0.7)
    ap.add_argument("--dejenere", type=float, default=0.85)
    ap.add_argument("--min-kapsam", type=float, default=0.30)
    ap.add_argument("--min-j", type=float, default=0.10)
    ap.add_argument("--min-oy", type=int, default=3)
    ap.add_argument("--tohum", type=int, default=20260727)
    ap.add_argument("--out", default="sonuclar/konsensus_dogrulama.txt")
    a = ap.parse_args()

    profiller, kaynak = profil_yukle(a.tani)
    rnd = random.Random(a.tohum)
    s1, s2, sr, secler = [], [], [], []
    for _ in range(a.tekrar):
        r1, r2, rr, ns = tur(profiller, a.n, a.hata_orani, a.esik, rnd,
                             dejenere=a.dejenere, min_kapsam=a.min_kapsam,
                             min_j=a.min_j, min_oy=a.min_oy)
        s1.append(r1)
        s2.append(r2)
        sr.append(rr)
        secler.append(ns)
    sec_sirali = sorted(secler)
    n_sec_ort = sum(secler) / max(len(secler), 1)
    n_sec_med = sec_sirali[len(sec_sirali) // 2] if sec_sirali else 0

    def ort(s, k):
        v = [x[k] for x in s]
        m = sum(v) / len(v)
        sd = (sum((x - m) ** 2 for x in v) / max(len(v) - 1, 1)) ** 0.5
        return m, sd

    L = []
    e = L.append
    e("=" * 74)
    e("KONSENSUS ON-TARAMA DOGRULAMA BENZETIMI")
    e("=" * 74)
    e(f"oyveren profil kaynagi : {kaynak}")
    e(f"model x kosul hucresi  : {len(profiller)}")
    e(f"v2'nin bilgili buldugu : ortalama {n_sec_ort:.2f}  medyan {n_sec_med}  "
      f"aralik {min(secler) if secler else 0}-{max(secler) if secler else 0}")
    if secler and (max(secler) - min(secler)) >= 2:
        e(f"  ! Oy veren kadrosu tekrarlar arasinda KARARSIZ: ayni gercek profil,")
        e(f"    farkli orneklemede farkli sayida hucreyi 'bilgili' buluyor. J degerleri")
        e(f"    esige ({a.min_j}) cok yakin oldugu icin secim gurultuye tabi; asagidaki")
        e(f"    v2 standart sapmalarinin buyuklugu bundandir.")
    e(f"iddia/tur={a.n}  enjekte altin hatasi=%{a.hata_orani*100:.1f} (yari DOGRU-altin, yari YANLIS-altin)")
    e(f"tekrar={a.tekrar}  esik=%{a.esik*100:.0f}  tohum={a.tohum}")
    e("")
    e(f"{'olcut':<34}{'v1 naif':>17}{'v2 duzeltmeli':>17}{'rastgele':>17}")
    satirlar = [
        ("secilen madde", "bayrak", "{:.1f}"),
        ("geri-cagirma (tum hatalar) %", "geri", "{:.1f}"),
        ("  ... DOGRU-altin hatalarinda %", "geri_d", "{:.1f}"),
        ("  ... YANLIS-altin hatalarinda %", "geri_y", "{:.1f}"),
        ("kesinlik %", "kesinlik", "{:.1f}"),
        ("sinif asimetrisi (puan)", "asimetri", "{:.1f}"),
    ]
    for ad, k, fmt in satirlar:
        m1, d1 = ort(s1, k)
        m2, d2 = ort(s2, k)
        mr, dr = ort(sr, k)
        e(f"{ad:<34}{fmt.format(m1)+' ±'+fmt.format(d1):>17}"
          f"{fmt.format(m2)+' ±'+fmt.format(d2):>17}{fmt.format(mr)+' ±'+fmt.format(dr):>17}")
    e("")
    k1, _ = ort(s1, "kesinlik")
    k2, _ = ort(s2, "kesinlik")
    kr, _ = ort(sr, "kesinlik")
    b2m, _ = ort(s2, "bayrak")
    g1d, _ = ort(s1, "geri_d")
    g1y, _ = ort(s1, "geri_y")
    g2d, _ = ort(s2, "geri_d")
    g2y, _ = ort(s2, "geri_y")
    a1, _ = ort(s1, "asimetri")
    a2, _ = ort(s2, "asimetri")
    kaldirac1 = k1 / max(kr, 1e-9)
    kaldirac2 = k2 / max(kr, 1e-9)
    e("YORUM (sayilardan turetilmistir, sabit metin degildir)")
    e(f"  Rastgele ayni sayida satir secmek %{kr:.1f} kesinlik verir; bu taban cizgisidir.")
    e(f"  v1 kaldiraci: x{kaldirac1:.2f}   |   v2 kaldiraci: x{kaldirac2:.2f}")
    if g1y > 0 and g1d / max(g1y, 1e-9) >= 1.8:
        e(f"  Naif tarama sinif korlugu gosteriyor: DOGRU-altin %{g1d:.0f} / YANLIS-altin %{g1y:.0f}.")
    else:
        e(f"  Naif taramada belirgin sinif korlugu YOK (DOGRU-altin %{g1d:.0f} / YANLIS-altin %{g1y:.0f});")
        e(f"  bu koşumda oy verenlerin yanliliklari birbirini buyuk olcude gotururmus.")
    if g2y > g1y * 1.4 and a2 <= a1:
        e(f"  Duzeltme YANLIS-altin geri-cagirmasini %{g1y:.0f} -> %{g2y:.0f} yukseltmis ve asimetriyi")
        e(f"  {a1:.1f} -> {a2:.1f} puana indirmis: duzeltme v1'e GORE dengeyi iyilestiriyor.")
        e(f"  Dikkat: bu GORECE bir kazanctir. Mutlak kullanilabilirlik icin KARAR blokuna bakin.")
    else:
        e(f"  Duzeltme dengeyi iyilestirmedi (asimetri {a1:.1f} -> {a2:.1f} puan);")
        e(f"  eleme sonrasi kalan oy verenlerin ARTIK yanliligi yeni bir asimetri uretiyor.")
    e("")
    e("KARAR")
    if kaldirac2 < 1.5 or k2 < 10:
        e(f"  ! BU OY VEREN KADROSUYLA TARAMA UZMAN TRIYAJI ICIN KULLANILMAMALIDIR.")
        e(f"  {b2m:.0f} satirlik uzman emegi ~{b2m*k2/100:.1f} gercek hata getirir; ayni emegi rastgele")
        e(f"  harcamak ~{b2m*kr/100:.1f} hata getirirdi. Fark istatistiksel olarak anlamsiza yakin.")
        e(f"  Sorun toplama kuralinda degil oy verenlerde: hicbir hucre yeterince bilgili degil.")
        e(f"  Dogru yol: bayrakli satirlar yerine TABAKALI RASTGELE ORNEK uzerinden uzman denetimi.")
    else:
        e(f"  Tarama kullanilabilir: v2 kaldiraci x{kaldirac2:.2f}, beklenen verim")
        e(f"  {b2m:.0f} satirda ~{b2m*k2/100:.1f} gercek hata (rastgelede ~{b2m*kr/100:.1f}).")
    rapor = "\n".join(L)
    print(rapor)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(rapor + "\n")
    print(f"\nyazildi: {a.out}")


if __name__ == "__main__":
    main()
