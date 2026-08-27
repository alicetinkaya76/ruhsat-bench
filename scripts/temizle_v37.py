# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — cerrahi temizlik + P5 alt-bolunmesi (uretici YENIDEN CALISTIRILMAZ).

Neden yeniden uretmiyoruz: 486 iddianin uzerinde 5 model x 2 kosul konsensus
kosusu zaten yapildi ve id'ler o kosuya bagli. Yeni bir uretim tum id'leri
kaydirir ve saatlerce GPU zamanini cope atar. Kaynak-kimlik katmani da
(kaynak_dogrula_v2) temiz cikti: 453/453 koken eslesmesi, 0 kazara-dogru.
Geriye METIN KALITESI kaynakli birkac satir kaliyor; onlari kural bazli
(id bazli DEGIL) atiyoruz, boylece ayni kural v3.7 ureticisine de tasinabilir.

Kurallar (hepsi kaynak_alinti + iddia uzerinde calisir):
  R1 fikra-ici parcalanma : cumle ortasinda "(4)" tipi fikra isareti
                            -> cumle iki ayri fikrayi birbirine yapistirmis
  R2 capraz kanun atfi    : "2960 Sayılı ..." (uretecteki filtre KUCUK HARFE
                            duyarli yazilmis, "Sayılı" buyuk S ile kacmis)
  R3 bolum/kisim basligi  : "ALTINCI BÖLÜM ..." tipi baslik artigi
  R4 bolunmus ek          : "malzeme sinin" tipi, tek basina kelime olamayacak
                            ek parcasinin ayri yazilmis olmasi
  R5 ALL-CAPS baslik      : cumlenin bas tarafinda 2+ tamamen buyuk harfli kelime

Onemli: kural kaynak_alinti uzerinde caliistigi icin ayni bozuk cumleden
turetilmis TUM kardes iddialar (P1 + P2 + P5) birlikte dusuyor. Tek tek id
atmak altin dengesini sessizce bozardi.

Ayrica: uretim_sablonu'ndan probe_alt sutunu tureltilir
(P5_lawshuffle / P5_maddeshift ayrimi F4 raporlamasi icin bedava gelir).

Kullanim:
    python scripts/temizle_v37.py
    python scripts/temizle_v37.py --kuru   (hicbir sey yazmaz, yalniz rapor)
"""
import argparse
import csv
import os
import re
from collections import Counter, defaultdict

FIKRA_ICI = re.compile(r"(?<!^)\(\s*\d{1,2}\s*\)")
KANUN_ATIF = re.compile(r"\b\d{3,4}\s*[Ss]ay[ıi]l[ıi]\b")
BOLUM = re.compile(
    r"\b(B[İI]R[İI]NC[İI]|[İI]K[İI]NC[İI]|[ÜU][ÇC][ÜU]NC[ÜU]|D[ÖO]RD[ÜU]NC[ÜU]|BE[ŞS][İI]NC[İI]|"
    r"ALTINCI|YED[İI]NC[İI]|SEK[İI]Z[İI]NC[İI]|DOKUZUNCU|ONUNCU|ON\s?B[İI]R[İI]NC[İI])\s+"
    r"(B[ÖO]L[ÜU]M|KISIM)\b")
EK_PARCA = re.compile(
    r"\s(sinin|sının|sunun|sünün|nin|nın|nun|nün|leri|ları|lerini|larını|"
    r"ndan|nden|ndaki|ndeki|sine|sına|lerde|larda)\b")
CAPS = re.compile(r"^(?:\W*)(?:[A-ZÇĞİÖŞÜ]{2,}\s+){2,}")

KURALLAR = [
    ("R1_fikra_ici_parcalanma", lambda a, i: bool(FIKRA_ICI.search(a))),
    ("R2_capraz_kanun_atfi",    lambda a, i: bool(KANUN_ATIF.search(a) or KANUN_ATIF.search(i))),
    ("R3_bolum_basligi",        lambda a, i: bool(BOLUM.search(a) or BOLUM.search(i))),
    ("R4_bolunmus_ek",          lambda a, i: bool(EK_PARCA.search(a))),
    ("R5_caps_basligi",         lambda a, i: bool(CAPS.match(a))),
]

VARYANT = re.compile(r"(P5_maddeshift|P5_lawshuffle|P2_swap|P1_\w+|P3_\w+|P4_\w+|P6_\w+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v1.csv")
    ap.add_argument("--out", default="data/iddialar/uretilen_iddialar_v2_temiz.csv")
    ap.add_argument("--rapor", default="sonuclar/temizlik_raporu.txt")
    ap.add_argument("--kuru", action="store_true")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))
        alanlar = list(satirlar[0].keys()) if satirlar else []

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — CERRAHI TEMIZLIK (v3.7 kurallari, uretici calistirilmadan)")
    e("=" * 78)
    e(f"girdi: {a.csv}  ({len(satirlar)} iddia)")

    # 1) hangi KAYNAK CUMLELER bozuk?
    bozuk_cumle = {}
    for s in satirlar:
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        iddia = " ".join((s.get("iddia") or "").split())
        for ad, f in KURALLAR:
            if f(alinti, iddia):
                bozuk_cumle.setdefault(alinti, []).append(ad)
                break

    e()
    e("[1] BOZUK KAYNAK CUMLELER")
    e(f"  {len(bozuk_cumle)} farkli kaynak cumle en az bir kurala takildi.")
    for c, kurallar in sorted(bozuk_cumle.items(), key=lambda x: -len(x[0]))[:20]:
        e(f"    [{kurallar[0]}] {c[:110]}")

    # 2) o cumleden turetilmis TUM kardesleri at
    atilan, kalan = [], []
    sebep_say = Counter()
    for s in satirlar:
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        if alinti in bozuk_cumle:
            sebep = bozuk_cumle[alinti][0]
            sebep_say[sebep] += 1
            atilan.append((s, sebep))
        else:
            kalan.append(s)

    e()
    e("[2] KURAL BASINA ATILAN IDDIA")
    for ad, _ in KURALLAR:
        e(f"    {ad:<28} {sebep_say.get(ad, 0)}")
    e(f"    {'TOPLAM':<28} {len(atilan)}")
    e()
    e("  atilan iddialar (id | probe | gold):")
    for s, sebep in atilan[:40]:
        e(f"    #{s.get('id',''):<5} {s.get('probe',''):<15} {s.get('gold',''):<8} {sebep}")
        e(f"           {' '.join((s.get('iddia') or '').split())[:100]}")

    # 3) probe_alt turet
    for s in kalan:
        m = VARYANT.search(s.get("uretim_sablonu") or "")
        s["probe_alt"] = m.group(1) if m else (s.get("probe") or "")

    e()
    e("[3] TEMIZ SETIN YAPISI")
    e(f"  {len(satirlar)} -> {len(kalan)} iddia  (-{len(atilan)}, %{100.0*len(atilan)/max(len(satirlar),1):.1f})")
    g = Counter(s.get("gold", "") for s in kalan)
    g0 = Counter(s.get("gold", "") for s in satirlar)
    for k in sorted(set(g) | set(g0)):
        e(f"    gold {k:<8} {g0.get(k,0):>4} -> {g.get(k,0):>4}  (%{100.0*g.get(k,0)/max(len(kalan),1):.1f})")
    e()
    e("  probe dagilimi (probe / probe_alt):")
    pr = Counter(s.get("probe", "") for s in kalan)
    pa = defaultdict(Counter)
    for s in kalan:
        pa[s.get("probe", "")][s["probe_alt"]] += 1
    for p in sorted(pr):
        e(f"    {p:<16} {pr[p]:>4}  (%{100.0*pr[p]/max(len(kalan),1):.1f})")
        if len(pa[p]) > 1:
            for alt, n in sorted(pa[p].items(), key=lambda x: -x[1]):
                e(f"        {alt:<20} {n:>4}")

    e()
    e("[4] DENGE NOTU")
    p5 = pa.get("P5_capraz", Counter())
    if p5:
        ms, ls = p5.get("P5_maddeshift", 0), p5.get("P5_lawshuffle", 0)
        e(f"  P5 alt-turleri: maddeshift {ms} / lawshuffle {ls}")
        if ms and ls and max(ms, ls) / max(min(ms, ls), 1) >= 2:
            e(f"  ! dengesiz ({max(ms,ls)/max(min(ms,ls),1):.1f}x). Ikisi F4'te AYRI raporlanacak;")
            e(f"    kucuk olan alt-tur ({min(ms,ls)} madde) dusuk guclu. 1500'e genisletirken")
            e(f"    lawshuffle payini artirin (uretecte random.random() < 0.5 esigini kaydirin).")
    az = [(p, n) for p, n in pr.items() if n < 40]
    if az:
        e(f"  40'in altinda kalan probe'lar: {', '.join(f'{p}={n}' for p, n in sorted(az))}")

    if a.kuru:
        e()
        e("  (--kuru) dosya yazilmadi.")
    else:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=alanlar + ["probe_alt"])
            w.writeheader()
            w.writerows(kalan)
        print(f"\nyazildi: {a.out}  ({len(kalan)} iddia)")

    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.rapor}")


if __name__ == "__main__":
    main()
