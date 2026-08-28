# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — ANALIZ KATMANI  (HANDOVER Gorev 4)

f4_skor.py'YE DOKUNULMAZ. O dosya arsivle karsilastirilabilirlik icin
DONDURULDU (HANDOVER 6). Duzeltmeler burada yasar.

NE DUZELTIR / NE EKLER
----------------------
1. STANDART ECE (kutuk #6, denetim 1.10).
   f4_skor.py:172 kova ORTA NOKTASINI kullaniyor:
       ece = sum(n * abs(acc_b - (b*10+5)/100) ...) / N
   R3 hep guven=100 ve hep dogru -> kova b=9, orta nokta 0.95,
   dogruluk 1.00 -> |1.00-0.95| = 0.05 basiyor. DOGRU DEGER 0'dir.
   Burada kovadaki ORTALAMA GUVEN kullanilir:
       ECE = sum_b (n_b/N) * |acc_b - conf_ort_b|
   POZITIF KONTROL: --pozitif-kontrol R3'e ECE=0.000 vermeli.

2. Brier skoru: mean((guven/100 - dogru)^2). f4_skor.py'de yoktu.

3. KUMELI BOOTSTRAP. Iddialar bagimsiz DEGIL: ayni (kanun, madde)
   kumesinden birden cok iddia uretilmis. Iddia duzeyinde bootstrap
   CI'yi DAR gosterir. Yeniden orneklenen birim KUMEDIR.

4. P6 icin prob ICI BAcc. Tek sinifli tabakalarda BAcc tanimsizdir;
   bu tabakalar "altin sinifi secme orani" diye ETIKETLENIR (HANDOVER 3:
   negatif kontrolde P2/P4 karistirilmis eslemede bile 1.00 kalmisti).

5. RISK-KAPSAM egrisi: E1'de guven esigi taranir; her esikte kapsam ve
   taahhut edilenlerdeki hata orani. Kacinmanin SECICI olup olmadigini
   gosterir.

6. B KOLUNUN KOL ICI BANDI (kutuk #8). frontCB2 k1/k2/k3 ikili
   uyusmalari B'nin KENDI tekrar bandini verir. sonda_karsilastir.py'nin
   hukmu bu band olmadan verilemezdi.

7. UC ALTIN TEK TABLODA: v7a birincil, v6 + v7b duyarlilik
   (etki_analizi.py deseni).

KOSU (bash)
-----------
    cd ~/Desktop/ruhsat-bench
    .venv/bin/python -u scripts/f4_analiz.py --pozitif-kontrol

    .venv/bin/python -u scripts/f4_analiz.py \\
      --sonuclar "sonuclar/f4_frontier_cogunluk.jsonl:claude-sonnet-5,\\
sonuclar/f4_haiku_cogunluk.jsonl:claude-haiku-4.5,sonuclar/r3_kural.jsonl" \\
      --rapor sonuclar/f4_analiz_raporu.txt --csv sonuclar/f4_analiz.csv
"""
import argparse
import collections
import csv
import json
import math
import os
import random
import sys

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROBLAR = ["P1_dogrudan", "P2_sayisal", "P3_anakronizm",
           "P4_uydurma", "P5_capraz", "P6_guncellik"]


# ------------------------------------------------------------------ YUKLEME
def altin_yukle(yol):
    d = {}
    for r in csv.DictReader(open(yol, encoding="utf-8-sig")):
        d[r["id"]] = {"gold": r["gold"], "probe": r["probe"],
                      "kume": (r["kanun"], r["madde"])}
    return d


def kayit_yukle(tanim):
    """'yol' ya da 'yol:model_etiketi' (etki_analizi.py deseni)."""
    out = []
    for parca in tanim.split(","):
        parca = parca.strip()
        if not parca:
            continue
        yol, _, etiket = parca.partition(":")
        for s in open(yol, encoding="utf-8"):
            r = json.loads(s)
            if etiket:
                r["model"] = etiket
            r["_dosya"] = os.path.basename(yol)
            out.append(r)
    return out


# ------------------------------------------------------------------ OLCULER
def hucre_olc(kayitlar, altin):
    """Bir (model, kosul, varyant) hucresinin butun olculeri."""
    N = len(kayitlar)
    commit = [r for r in kayitlar if r.get("karar") in ("DOGRU", "YANLIS")]
    ayr = sum(1 for r in kayitlar if r.get("durum") == "ayristirilamadi")
    kacin = sum(1 for r in kayitlar
                if r.get("karar") == "EMIN_DEGILIM" or r.get("durum") == "e2_kacinma")
    hit = fa = pos = neg = dogru = 0
    for r in commit:
        g = altin[r["id"]]["gold"]
        k = r["karar"]
        dogru += (k == g)
        if g == "DOGRU":
            pos += 1
            hit += (k == "DOGRU")
        else:
            neg += 1
            fa += (k == "DOGRU")
    sens = hit / pos if pos else float("nan")
    spec = 1 - fa / neg if neg else float("nan")
    bacc = (sens + spec) / 2 if pos and neg else float("nan")

    # --- STANDART ECE: kovadaki ORTALAMA GUVEN (kutuk #6)
    kova = collections.defaultdict(lambda: [0, 0, 0.0])   # n, dogru, guven_top
    for r in commit:
        gv = r.get("guven")
        if not isinstance(gv, (int, float)):
            continue
        b = min(9, max(0, int(gv) // 10))
        kova[b][0] += 1
        kova[b][1] += (r["karar"] == altin[r["id"]]["gold"])
        kova[b][2] += gv / 100.0
    n_kal = sum(v[0] for v in kova.values())
    ece = (sum(v[0] * abs(v[1] / v[0] - v[2] / v[0]) for v in kova.values() if v[0])
           / n_kal) if n_kal else float("nan")

    # --- Brier
    brier = (sum((r["guven"] / 100.0 - (r["karar"] == altin[r["id"]]["gold"])) ** 2
                 for r in commit if isinstance(r.get("guven"), (int, float)))
             / n_kal) if n_kal else float("nan")

    # --- lambda = dogruluk(P1) + dogruluk(P5) - 1
    def prob_dogruluk(p):
        alt = [r for r in commit if altin[r["id"]]["probe"] == p]
        return (sum(1 for r in alt if r["karar"] == altin[r["id"]]["gold"]) / len(alt)
                if alt else float("nan"))
    lam = prob_dogruluk("P1_dogrudan") + prob_dogruluk("P5_capraz") - 1

    return dict(n=N, taahhut=len(commit), kapsam=len(commit) / N if N else float("nan"),
                ayristirilamadi=ayr, kacinma=kacin,
                dogruluk=dogru / len(commit) if commit else float("nan"),
                bacc=bacc, sens=sens, spec=spec, lam=lam, ece=ece, brier=brier,
                ece_kayit=n_kal)


def kumeli_bootstrap(kayitlar, altin, olcu, n=10000, tohum=42):
    """Yeniden orneklenen birim KUMEDIR (kanun, madde), iddia DEGIL.

    Gerekce: ayni maddeden birden cok iddia uretilmistir; bunlar bagimsiz
    degildir. Iddia duzeyinde bootstrap CI'yi yapay olarak DARALTIR.
    """
    kume = collections.defaultdict(list)
    for r in kayitlar:
        kume[altin[r["id"]]["kume"]].append(r)
    anahtarlar = list(kume)
    if len(anahtarlar) < 2:
        return (float("nan"), float("nan"))
    rnd = random.Random(tohum)
    ornek = []
    for _ in range(n):
        secim = [kume[anahtarlar[rnd.randrange(len(anahtarlar))]]
                 for _ in range(len(anahtarlar))]
        duz = [r for grup in secim for r in grup]
        try:
            v = olcu(hucre_olc(duz, altin))
        except Exception:                                   # noqa: BLE001
            v = float("nan")
        if v == v:
            ornek.append(v)
    if not ornek:
        return (float("nan"), float("nan"))
    ornek.sort()
    return (ornek[int(0.025 * len(ornek))], ornek[min(len(ornek) - 1, int(0.975 * len(ornek)))])


def risk_kapsam(kayitlar, altin, esikler=range(0, 101, 10)):
    """E1'de guven esigi taranir. Kacinma SECICI mi?"""
    out = []
    for e in esikler:
        alt = [r for r in kayitlar
               if r.get("karar") in ("DOGRU", "YANLIS")
               and isinstance(r.get("guven"), (int, float)) and r["guven"] >= e]
        if not alt:
            out.append((e, 0.0, float("nan")))
            continue
        hata = sum(1 for r in alt if r["karar"] != altin[r["id"]]["gold"]) / len(alt)
        out.append((e, len(alt) / len(kayitlar), hata))
    return out


def prob_ici(kayitlar, altin):
    """Prob ICI BAcc. Tek sinifli tabaka -> 'altin sinifi secme orani'."""
    out = []
    for p in PROBLAR:
        alt = [r for r in kayitlar if altin[r["id"]]["probe"] == p
               and r.get("karar") in ("DOGRU", "YANLIS")]
        if not alt:
            continue
        siniflar = {altin[r["id"]]["gold"] for r in alt}
        dogru = sum(1 for r in alt if r["karar"] == altin[r["id"]]["gold"])
        if len(siniflar) < 2:
            out.append((p, len(alt), float("nan"), dogru / len(alt),
                        f"TEK SINIF ({siniflar.pop()}) — altin sinifi secme orani"))
        else:
            m = hucre_olc(alt, altin)
            out.append((p, len(alt), m["bacc"], m["dogruluk"], ""))
    return out


def kol_ici_band(dosyalar):
    """B kolunun KENDI tekrar bandi (kutuk #8): k1/k2/k3 ikili uyusmalari."""
    kosular = []
    for y in dosyalar:
        d = {}
        for s in open(y, encoding="utf-8"):
            r = json.loads(s)
            d[(r["id"], r["kosul"])] = r.get("karar")
        kosular.append((os.path.basename(y), d))
    ciftler = []
    for i in range(len(kosular)):
        for j in range(i + 1, len(kosular)):
            a, b = kosular[i][1], kosular[j][1]
            ortak = set(a) & set(b)
            if not ortak:
                continue
            ciftler.append((kosular[i][0], kosular[j][0],
                            sum(1 for k in ortak if a[k] == b[k]) / len(ortak), len(ortak)))
    return ciftler


# ------------------------------------------------------------------ POZ. KONTROL
def pozitif_kontrol(ciftler):
    """R3'e ECE=0 vermeli. f4_skor.py orta-nokta formulu 0.05 basiyordu (kutuk #6).

    ONKOSUL — ilk denemede ATLANMISTI ve kontrol dustu (kayda geciyor):
    "ECE=0 beklenir" ancak model KUSURSUZ ve guveni SABIT ise gecerlidir.
    Arsiv r3_kural.jsonl, v6 altinina karsi 473/473'tur ama v7a'ya karsi
    466/473'tur; v7a ile ECE=0.0148 cikar ve bu DOGRU davranistir, kusur
    degil. Bu yuzden kontrol artik onkosulu ONCE dogrular, sonra hukum verir.
    """
    print("== POZITIF KONTROL (kutuk #6: standart ECE) ==")
    tum_gecti = True
    for ad, r3_yolu, altin_yolu in ciftler:
        if not (os.path.exists(r3_yolu) and os.path.exists(altin_yolu)):
            print(f"\n  [{ad}] ATLANDI — dosya yok")
            continue
        altin = altin_yukle(altin_yolu)
        kay = [r for r in kayit_yukle(r3_yolu) if r["id"] in altin]
        m = hucre_olc(kay, altin)
        guvenler = {r.get("guven") for r in kay if r.get("karar") in ("DOGRU", "YANLIS")}
        onkosul = abs(m["dogruluk"] - 1.0) < 1e-9 and guvenler == {100}
        print(f"\n  [{ad}]")
        print(f"    kayit {m['n']} · dogruluk {m['dogruluk']:.4f} · guven kumesi {sorted(guvenler)}")
        print(f"    ONKOSUL (dogruluk=1.0 ve guven sabit 100): {'SAGLANDI' if onkosul else 'SAGLANMADI'}")

        # f4_skor.py'nin orta-nokta formulunu YENIDEN URET (o dosyaya DOKUNMADAN)
        kova = collections.defaultdict(lambda: [0, 0])
        for r in kay:
            if r.get("karar") not in ("DOGRU", "YANLIS"):
                continue
            gv = r.get("guven")
            if not isinstance(gv, (int, float)):
                continue
            b = min(9, max(0, int(gv) // 10))
            kova[b][0] += 1
            kova[b][1] += (r["karar"] == altin[r["id"]]["gold"])
        n = sum(v[0] for v in kova.values())
        eski = sum(v[0] * abs(v[1] / v[0] - (b * 10 + 5) / 100)
                   for b, v in kova.items() if v[0]) / max(n, 1)
        print(f"    standart ECE (bu betik)   : {m['ece']:.4f}")
        print(f"    orta nokta ECE (arsiv)    : {eski:.4f}")
        if onkosul:
            gecti = abs(m["ece"]) < 1e-9 and eski > 0.001
            print(f"    HUKUM: standart 0 olmali -> {'TAMAM' if abs(m['ece'])<1e-9 else 'HATA'}"
                  f" · arsiv >0 olmali -> {'kusur DOGRULANDI' if eski>0.001 else 'beklenmedik'}")
            tum_gecti &= gecti
        else:
            print("    HUKUM: onkosul saglanmadigi icin ECE=0 BEKLENMEZ; bu cift")
            print("           yalnizca iki formulun FARKINI gosterir (fark "
                  f"{eski - m['ece']:+.4f}).")
    print(f"\n  SONUC: {'GECTI' if tum_gecti else 'DUSTU'}")
    return 0 if tum_gecti else 1


# ------------------------------------------------------------------ MAIN
def main():
    ap = argparse.ArgumentParser(description="RUHSAT-Bench analiz katmani")
    ap.add_argument("--sonuclar", default="sonuclar/r3_kural.jsonl")
    ap.add_argument("--altin", default="data/iddialar/uretilen_iddialar_v7a.csv")
    ap.add_argument("--altin-duyarlilik", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv,"
                                                  "data/iddialar/uretilen_iddialar_v7b.csv")
    ap.add_argument("--bootstrap", type=int, default=10000)
    # ECE/Brier ancak YETERI KADAR guven tasiyan kayit varsa anlamlidir.
    # OLCULDU: llama3.2:3b-instruct-fp16/E1/B hucresinde 410 taahhutten
    # YALNIZ 1'i guven tasiyor; esik olmadan tablo "ECE 0.000" basiyor ve
    # sansa yakin bir modeli kusursuz kalibre gosteriyordu.
    # 50 esigi DISSAL OLARAK GEREKCELENDIRILMIS DEGILDIR; raporda boyle yazilir.
    ap.add_argument("--min-guven-n", type=int, default=50,
                    help="ECE/Brier icin asgari guven tasiyan kayit (varsayilan 50)")
    ap.add_argument("--tohum", type=int, default=42)
    ap.add_argument("--band-dosyalari", default="sonuclar/frontCB2_k1.jsonl,"
                                                "sonuclar/frontCB2_k2.jsonl,"
                                                "sonuclar/frontCB2_k3.jsonl")
    ap.add_argument("--rapor", default="")
    ap.add_argument("--csv", default="")
    ap.add_argument("--pozitif-kontrol", action="store_true")
    a = ap.parse_args()

    if a.pozitif_kontrol:
        # Onkosulu SAGLAYAN cift once; arsiv cifti karsilastirma icin yaninda.
        sys.exit(pozitif_kontrol([
            ("korpus_v2 R3 + v7a  (onkosulu saglar)",
             "sonuclar/gorev2/r3_korpus_v2_v7a.jsonl",
             "data/iddialar/uretilen_iddialar_v7a.csv"),
            ("arsiv R3 + v6       (onkosulu saglar)",
             "sonuclar/r3_kural.jsonl",
             "data/iddialar/uretilen_iddialar_v6_onarilmis.csv"),
            ("arsiv R3 + v7a      (onkosulu SAGLAMAZ — kontrol bunu ayirt etmeli)",
             "sonuclar/r3_kural.jsonl",
             "data/iddialar/uretilen_iddialar_v7a.csv"),
        ]))

    satir = []
    P = lambda s="": (print(s), satir.append(s))            # noqa: E731

    altin = altin_yukle(a.altin)
    kayitlar = [r for r in kayit_yukle(a.sonuclar) if r["id"] in altin]
    P("RUHSAT-Bench — ANALIZ KATMANI (f4_analiz.py)")
    P(f"altin (birincil) : {a.altin}   n={len(altin)}")
    P(f"kayit            : {len(kayitlar)}")
    P(f"bootstrap        : {a.bootstrap} yeniden orneklem, KUME=(kanun, madde), tohum={a.tohum}")
    P("")

    # --- hucreler
    hucre = collections.defaultdict(list)
    for r in kayitlar:
        hucre[(r.get("model"), r.get("kosul"), r.get("varyant", "-"))].append(r)

    P("=" * 100)
    P("1. HUCRE OLCULERI  (ECE = STANDART; kova ortalama guveni — kutuk #6 duzeltildi)")
    P("=" * 100)
    P(f"{'model':<28}{'ko':<4}{'v':<3}{'n':>5}{'kapsam':>8}{'dogr':>7}"
      f"{'BAcc':>7}{'BAcc %95 GA':>18}{'lambda':>8}{'gvn_n':>7}{'ECE':>7}{'Brier':>7}")
    P("-" * 100)
    csv_satir = []
    for k in sorted(hucre, key=lambda z: (str(z[0]), str(z[1]), str(z[2]))):
        model, kosul, var = k
        m = hucre_olc(hucre[k], altin)
        alt, ust = kumeli_bootstrap(hucre[k], altin, lambda d: d["bacc"],
                                    n=a.bootstrap, tohum=a.tohum)
        ga = f"[{alt:.3f}, {ust:.3f}]" if alt == alt else "—"
        f = lambda x, b="{:>7.3f}": (b.format(x) if x == x else f"{'—':>7}")   # noqa: E731
        # ECE/Brier esik altinda BASTIRILIR — tek kayittan "ECE 0.000" cikiyordu.
        yeter = m["ece_kayit"] >= a.min_guven_n
        e_s = f(m["ece"]) if yeter else f"{'az-n':>7}"
        b_s = f(m["brier"]) if yeter else f"{'az-n':>7}"
        P(f"{str(model)[:27]:<28}{str(kosul):<4}{str(var):<3}{m['n']:>5}"
          f"{f(m['kapsam'], '{:>8.3f}')}{f(m['dogruluk'])}{f(m['bacc'])}{ga:>18}"
          f"{f(m['lam'], '{:>8.3f}')}{m['ece_kayit']:>7}{e_s}{b_s}")
        cs = dict(model=model, kosul=kosul, varyant=var, **{
            kk: (round(vv, 4) if isinstance(vv, float) and vv == vv else vv)
            for kk, vv in m.items()}, bacc_alt=round(alt, 4) if alt == alt else "",
            bacc_ust=round(ust, 4) if ust == ust else "",
            ece_gecerli=yeter)
        if not yeter:
            cs["ece"], cs["brier"] = "", ""      # anlamsiz degeri CSV'ye de yazma
        csv_satir.append(cs)
    az = sum(1 for c in csv_satir if not c["ece_gecerli"])
    P("-" * 100)
    P(f"  gvn_n = guven degeri TASIYAN taahhut sayisi. {az}/{len(csv_satir)} hucrede")
    P(f"  gvn_n < {a.min_guven_n}; o hucrelerde ECE/Brier 'az-n' diye BASTIRILDI.")
    P("  Gerekce (olculdu): llama3.2:3b-instruct-fp16/E1/B hucresinde 410")
    P("  taahhutten yalniz 1'i guven tasiyor; esik olmadan tablo 'ECE 0.000'")
    P("  basiyor ve sansa yakin bir modeli KUSURSUZ KALIBRE gosteriyordu.")
    P(f"  {a.min_guven_n} esigi DISSAL OLARAK GEREKCELENDIRILMIS DEGILDIR.")
    P("")

    # --- prob ici
    P("=" * 100)
    P("2. PROB ICI BAcc  (tek sinifli tabakalar ETIKETLENIR — HANDOVER 3)")
    P("=" * 100)
    for k in sorted(hucre, key=lambda z: (str(z[0]), str(z[1]))):
        sonuc = prob_ici(hucre[k], altin)
        if not sonuc:
            continue
        P(f"  {k[0]} / {k[1]} / {k[2]}")
        for p, n, bacc, dog, not_ in sonuc:
            b = f"{bacc:.3f}" if bacc == bacc else "tanimsiz"
            P(f"    {p:<16}{n:>5}  BAcc {b:>9}  dogruluk {dog:.3f}   {not_}")
    P("")

    # --- risk-kapsam
    P("=" * 100)
    P("3. RISK-KAPSAM (E1; guven esigi taranir)")
    P("=" * 100)
    for k in sorted(hucre, key=lambda z: str(z[0])):
        if k[1] != "E1":
            continue
        P(f"  {k[0]} / {k[2]}")
        P(f"    {'esik':>6}{'kapsam':>9}{'hata':>9}")
        for e, kap, hata in risk_kapsam(hucre[k], altin):
            h = f"{hata:.3f}" if hata == hata else "—"
            P(f"    {e:>6}{kap:>9.3f}{h:>9}")
    P("")

    # --- B kol ici bandi
    P("=" * 100)
    P("4. B KOLU — KOL ICI TEKRAR BANDI (kutuk #8)")
    P("=" * 100)
    dosyalar = [x.strip() for x in a.band_dosyalari.split(",") if x.strip()]
    var = [d for d in dosyalar if os.path.exists(d)]
    if len(var) < 2:
        P(f"  ATLANDI — en az iki koşu gerekli, bulunan: {var}")
    else:
        ciftler = kol_ici_band(var)
        for x, y, u, n in ciftler:
            P(f"    {x:<22}{y:<22}uyusma {u:.4f}   (n={n})")
        deg = [c[2] for c in ciftler]
        P(f"\n  KOL ICI BAND: [{min(deg):.4f}, {max(deg):.4f}]   ortalama {sum(deg)/len(deg):.4f}")
        P("  sonda_karsilastir.py'nin hukmu bu bandla verilir; band olmadan")
        P("  'kollar arasi uyusma dusuk' hukmu VERILEMEZ (kutuk #8).")
    P("")

    # --- uc altin
    P("=" * 100)
    P("5. UC ALTIN TEK TABLODA (v7a birincil · v6 ve v7b duyarlilik)")
    P("=" * 100)
    altinlar = [("v7a (birincil)", altin)]
    for y in [x.strip() for x in a.altin_duyarlilik.split(",") if x.strip()]:
        if os.path.exists(y):
            altinlar.append((os.path.basename(y).replace("uretilen_iddialar_", "")
                             .replace(".csv", ""), altin_yukle(y)))
    P(f"{'model':<28}{'ko':<4}" + "".join(f"{ad:>18}" for ad, _ in altinlar))
    P("-" * (32 + 18 * len(altinlar)))
    for k in sorted(hucre, key=lambda z: (str(z[0]), str(z[1]))):
        hucreler = []
        for ad, g in altinlar:
            alt = [r for r in hucre[k] if r["id"] in g]
            hucreler.append(hucre_olc(alt, g)["bacc"] if alt else float("nan"))
        P(f"{str(k[0])[:27]:<28}{str(k[1]):<4}"
          + "".join(f"{(f'{v:.4f}' if v == v else '—'):>18}" for v in hucreler))
    P("")
    P("  NOT: v7a ile v6 arasindaki fark 7 iddiadan gelir (EK-5 uzman duzeltmesi);")
    P("  etki testi 32 hucrede |dBAcc| ort 0.0046, maks 0.0347 olcmustu.")

    if a.rapor:
        os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
        open(a.rapor, "w", encoding="utf-8-sig").write("\n".join(satir) + "\n")
        print(f"\nrapor: {a.rapor}")
    if a.csv and csv_satir:
        os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(csv_satir[0]))
            w.writeheader()
            w.writerows(csv_satir)
        print(f"csv  : {a.csv}")


if __name__ == "__main__":
    main()
