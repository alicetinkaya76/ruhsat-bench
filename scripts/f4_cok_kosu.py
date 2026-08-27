# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F4 — COK KOSULU BIRLESTIRME ve KARARSIZLIK ANALIZI.

NEDEN
-----
Frontier saglayicida `temperature` parametresi kabul edilmiyor, dolayisiyla
determinizm sabitlenemiyor. Tekrar sondasi bunu OLCTU:

    ayni model, ayni 40 madde, arka arkaya iki kosu
    karar ayni      : 68/80  (%85)
    ham cikti ayni  : 51/80  (%64)

Yerel modellerde ayni olcum 946/946 idi. Tek kosuluk frontier verisiyle
"cevap politikasi kaymasi" gibi ince farklar OLCULEMEZ, cunku kosu ici
gurultu (%15) olculecek etkinin buyuklugune yakin.

COZUM: ayni kosuyu N kez tekrarla, madde basina COGUNLUK OYU al. Ciktilar
f4_kos.py semasinda yazilir; f4_skor.py degistirilmeden puanlar.

BEDAVA GELEN ANALIZ
-------------------
Kosular arasi KARARSIZLIK, modelin kendi beyan ettigi guvenden BAGIMSIZ
bir belirsizlik sinyalidir. Yerel modellerde olculemezdi (deterministikler).
Burada olculebilir ve sorulacak soru sudur:

    Modelin kosular arasi fikir degistirdigi maddeler, hata yaptigi
    maddeler mi?

Karsilastirma dogrudan yapilir: hatayi ongormede KARARSIZLIK mi daha iyi,
modelin BEYAN ETTIGI GUVEN mi? Ikisi de AUROC ile olculur. Kararsizlik
kazanirsa bulgu sudur: model ne bilmedigini soyleyemiyor ama davranisi
ele veriyor.

Kullanim:
    python scripts/f4_cok_kosu.py --girdiler sonuclar/k1.jsonl,sonuclar/k2.jsonl,sonuclar/k3.jsonl
    python scripts/f4_skor.py --jsonl sonuclar/f4_frontier_cogunluk.jsonl
"""
import argparse
import csv
import json
import math
import os
import statistics
from collections import Counter, defaultdict

KESIN = ("DOGRU", "YANLIS")


def auroc(cift):
    """cift: (skor, olay) listesi. Skor yuksekken olay olasi mi?"""
    poz = [s for s, y in cift if y]
    neg = [s for s, y in cift if not y]
    if not poz or not neg:
        return float("nan")
    return sum((1.0 if p > n else 0.5 if p == n else 0.0)
               for p in poz for n in neg) / (len(poz) * len(neg))


def fisher(a_, b_, c_, d_):
    n = a_ + b_ + c_ + d_
    if n == 0:
        return float("nan")

    def p(x):
        return math.comb(a_ + b_, x) * math.comb(c_ + d_, a_ + c_ - x) / math.comb(n, a_ + c_)
    p0 = p(a_)
    alt, ust = max(0, a_ + c_ - (c_ + d_)), min(a_ + b_, a_ + c_)
    return min(1.0, sum(p(x) for x in range(alt, ust + 1) if p(x) <= p0 + 1e-12))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--girdiler", required=True, help="virgulle ayrilmis jsonl yollari")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--out", default="sonuclar/f4_frontier_cogunluk.jsonl")
    ap.add_argument("--rapor", default="",
                    help="bos ise cikti adindan turetilir; sabit ad kullanmak "
                         "onceki kosunun raporunu EZER")
    a = ap.parse_args()

    if not a.rapor:
        kok = os.path.splitext(os.path.basename(a.out))[0]
        a.rapor = os.path.join(os.path.dirname(a.out) or "sonuclar",
                               f"kararsizlik_{kok}.txt")
    with open(a.claims, encoding="utf-8-sig") as fh:
        iddia = {r["id"]: r for r in csv.DictReader(fh)}

    yollar = [y.strip() for y in a.girdiler.split(",") if y.strip()]
    kosular = []
    for y in yollar:
        d = {}
        with open(y, encoding="utf-8-sig") as fh:
            for satir in fh:
                r = json.loads(satir)
                d[(r["model"], r["kosul"], r.get("varyant", "A"), str(r["id"]))] = r
        kosular.append(d)

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 96)
    e(f"RUHSAT-Bench F4 — COK KOSULU BIRLESTIRME  ({len(kosular)} kosu)")
    for y, d in zip(yollar, kosular):
        e(f"  {y}  ({len(d)} kayit)")
    e("=" * 96)

    anahtarlar = set(kosular[0])
    for d in kosular[1:]:
        anahtarlar &= set(d)
    e(f"her kosuda bulunan kayit: {len(anahtarlar)}")

    # ---------------------------------------------------------------- [1]
    e()
    e("[1] KOSULAR ARASI TEKRAR ORANI")
    e(f"  {'model / kosul':<34}{'n':>6}{'oybirligi':>11}{'ikili uyum':>12}{'ham ayni':>10}")
    hucre = defaultdict(list)
    for k in anahtarlar:
        hucre[(k[0], k[1])].append(k)
    for (m, ks) in sorted(hucre):
        ks_list = hucre[(m, ks)]
        oyb = ham = 0
        ikili = []
        for k in ks_list:
            oylar = [d[k].get("karar") for d in kosular]
            hamlar = [d[k].get("ham") for d in kosular]
            oyb += len(set(oylar)) == 1
            ham += len(set(hamlar)) == 1
            es = sum(1 for i in range(len(oylar)) for j in range(i + 1, len(oylar))
                     if oylar[i] == oylar[j])
            top = len(oylar) * (len(oylar) - 1) / 2
            ikili.append(es / top)
        n = len(ks_list)
        e(f"  {m + ' / ' + ks:<34}{n:>6}{oyb/n:>11.2f}{statistics.mean(ikili):>12.2f}{ham/n:>10.2f}")

    # ---------------------------------------------------------------- [2]
    yeni = []
    kararsiz = 0
    for k in sorted(anahtarlar):
        oylar = [d[k].get("karar") for d in kosular]
        say = Counter("YOK" if o is None else o for o in oylar)
        en, adet = say.most_common(1)[0]
        if adet * 2 <= len(oylar):
            karar, durum = None, "kosular_arasi_kararsiz"
            kararsiz += 1
        elif en == "YOK":
            karar = None
            durum = Counter(d[k].get("durum") for d in kosular).most_common(1)[0][0]
        else:
            karar, durum = en, "tamam"
        guvenler = [d[k].get("guven") for d in kosular
                    if isinstance(d[k].get("guven"), int)
                    and ("YOK" if d[k].get("karar") is None else d[k].get("karar")) == en]
        ornek = kosular[0][k]
        yeni.append({**ornek, "karar": karar, "durum": durum,
                     "guven": int(statistics.median(guvenler)) if guvenler else None,
                     "n_kosu": len(kosular), "oy_dagilimi": dict(say),
                     "kararsizlik": round(1 - adet / len(oylar), 4)})
    e()
    e(f"[2] COGUNLUK OYU: {len(yeni)} kayit | cogunluk olusmayan: {kararsiz}")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in yeni:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"yazildi: {a.out}")

    # ---------------------------------------------------------------- [3]
    e()
    e("[3] KARARSIZLIK HATAYI ONGORUYOR MU?")
    e("  Kosular arasi fikir degistirilen maddeler, hata yapilan maddeler mi?")
    e(f"  {'model / kosul':<34}{'oybirl.':>16}{'bolunmus':>16}{'fark':>8}{'Fisher p':>10}")
    for (m, ks) in sorted(hucre):
        ob = [0, 0]
        bl = [0, 0]
        for r in yeni:
            if r["model"] != m or r["kosul"] != ks or r.get("karar") not in KESIN:
                continue
            g = iddia.get(str(r["id"]), {}).get("gold")
            if not g:
                continue
            hedef = ob if r["kararsizlik"] == 0 else bl
            hedef[0] += 1
            hedef[1] += (r["karar"] == g)
        if ob[0] < 5 or bl[0] < 5:
            e(f"  {m + ' / ' + ks:<34}{ob[1]}/{ob[0]:<14}{bl[1]}/{bl[0]:<14}"
              f"{'  (bir taraf n<5)':>18}")
            continue
        p1, p2 = ob[1] / ob[0], bl[1] / bl[0]
        p = fisher(ob[1], ob[0] - ob[1], bl[1], bl[0] - bl[1])
        e(f"  {m + ' / ' + ks:<34}{ob[1]}/{ob[0]} = {p1:>5.2f}   {bl[1]}/{bl[0]} = {p2:>5.2f}"
          f"{p1-p2:>+8.2f}{p:>10.4f}{'  *' if p < 0.05 else ''}")
    e("  Oybirligi maddelerinde dogruluk daha yuksekse kararsizlik hata sinyalidir.")

    # ---------------------------------------------------------------- [4]
    e()
    e("[4] HANGI SINYAL DAHA IYI: KARARSIZLIK MI, BEYAN EDILEN GUVEN MI?")
    e("  Ikisi de HATAYI ongormede AUROC ile olculur (yuksek = daha iyi).")
    e(f"  {'model / kosul':<34}{'n':>6}{'kararsizlik':>13}{'1-guven':>10}{'fark':>8}")
    for (m, ks) in sorted(hucre):
        c_kar, c_guv = [], []
        for r in yeni:
            if r["model"] != m or r["kosul"] != ks or r.get("karar") not in KESIN:
                continue
            g = iddia.get(str(r["id"]), {}).get("gold")
            if not g:
                continue
            hata = (r["karar"] != g)
            c_kar.append((r["kararsizlik"], hata))
            if isinstance(r.get("guven"), int):
                c_guv.append((100 - r["guven"], hata))
        if len(c_kar) < 20:
            e(f"  {m + ' / ' + ks:<34}{len(c_kar):>6}   (n<20)")
            continue
        ak, ag = auroc(c_kar), auroc(c_guv) if c_guv else float("nan")
        e(f"  {m + ' / ' + ks:<34}{len(c_kar):>6}{ak:>13.3f}{ag:>10.3f}{ak-ag:>+8.3f}")
    e("  Kararsizlik kazaniyorsa: model ne bilmedigini SOYLEYEMIYOR ama")
    e("  DAVRANISI ele veriyor. Bu, kalibrasyon literaturu icin aktarilabilir")
    e("  bir sonuctur ve deterministik modellerde olculemez.")

    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.rapor}")


if __name__ == "__main__":
    main()
