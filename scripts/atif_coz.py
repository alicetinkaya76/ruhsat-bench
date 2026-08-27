# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — ATIF COZUMLEYICI ve POZITIF KONTROLU

NE ISE YARAR
------------
Dayanakli (retrieval) kollarin ve kural tabanli baseline'in TEMELIDIR.

KRITIK: CSV'deki `kanun` ve `madde` sutunlari iddianin ATIF YAPTIGI yeri degil,
metnin GERCEK KAYNAGINI tutar. P5'te bu ikisi kasten farklidir:

    P5_maddeshift(11.2.5 -> 9.3.1.2): csv madde = 11.2.5 (gercek kaynak)
                                       iddia    = "9.3.1.2 numarali bendine gore"
    P5_lawshuffle(3194 -> ISGRISK)  : csv kanun = 3194 (gercek kaynak)
                                       iddia    = "ISG Risk Deg. Yonetmeligi'ne gore"

Dayanak getirmede CSV sutunu kullanilirsa P5 CALISMAZ: modele iddianin
dogru alintiladigi pasaj verilir ve madde DOGRU gorunur. Atif MUTLAKA
iddia metninden cozulmelidir. Gercek is akisi da budur: muhendis, iddianin
gosterdigi maddeye bakar.

POZITIF KONTROL
---------------
`uretim_sablonu` sutunu hedefi acikca yazar; bu yuzden 473 maddenin
TAMAMI icin dogru atif bilinmektedir. Cozumleyici bu kumeye karsi
olculur; dogruluk esigin altindaysa betik HATA verir.
"""
import csv
import re
import sys
import argparse
import collections

# ------------------------------------------------------------------ KANUNLAR
# Sira onemli: uzun kaliplar once denenir.
KANUN_KALIP = [
    ("ISGRISK", r"(?:İş Sağlığı ve Güvenliği\s+)?Risk Değerlendirmesi Yönetmeliği"),
    ("ISGRISK", r"İSG Risk Değerlendirmesi Yönetmeliği"),
    ("YDUY",    r"Yapı Denetimi Uygulama Yönetmeliği"),
    ("TBDY",    r"TBDY\s*2018|Türkiye Bina Deprem Yönetmeliği"),
    ("3194",    r"3194\s*sayılı(?:\s+İmar)?\s*(?:Kanun|Kanunu)"),
    ("4708",    r"4708\s*sayılı(?:\s+Yapı Denetimi Hakkında)?\s*(?:Kanun|Kanunu)"),
    ("6331",    r"6331\s*sayılı(?:\s+İş Sağlığı ve Güvenliği)?\s*(?:Kanun|Kanunu)"),
]

# ------------------------------------------------------------------ MADDE
# Yalnizca ATIF BOLGESINDE aranir (kanun adindan hemen sonraki pencere).
# Boylece alinti govdesinde gecen "16 ncı maddenin birinci fikrasinda" gibi
# IC ATIFLAR yanlislikla yakalanmaz.
MADDE_KALIP = re.compile(
    r"(\d+(?:\.\d+)+)\s*(?:numaralı\s+)?bend"          # TBDY bendi: 9.3.1.2
    r"|(\d+)\s*(?:\.|’|'|inci|ıncı|nci|ncı|uncu|üncü)?\s*madde"   # 26. maddesine / 16 ncı maddenin
    , re.IGNORECASE)

ATIF_PENCERE = 60   # kanun adindan sonra kac karakter atif bolgesi sayilir


def kanun_coz(iddia):
    en_iyi = None
    for kod, kal in KANUN_KALIP:
        m = re.search(kal, iddia)
        if m and (en_iyi is None or m.start() < en_iyi[1]
                  or (m.start() == en_iyi[1] and m.end() > en_iyi[2])):
            en_iyi = (kod, m.start(), m.end())
    return (en_iyi[0], en_iyi[2]) if en_iyi else (None, 0)


def madde_coz(iddia, bitis):
    m = MADDE_KALIP.search(iddia, bitis, bitis + ATIF_PENCERE)
    if not m:
        return None
    # Gercek atifta madde referansi "gore"den ONCE gelir:
    #     "...Yonetmeligi'nin 26. maddesine gore ..."
    # "gore"den SONRA gelen madde referansi alinti govdesine ait bir IC ATIFTIR:
    #     "...Yonetmeligi'ne gore kanunun 8 inci maddesinin birinci fikrasi..."
    # Ikincisi atif degildir; belge duzeyinde dayanak getirilmelidir.
    g = iddia.find("göre", bitis)
    if 0 <= g < m.start():
        return None
    return m.group(1) or m.group(2)


def atif(iddia):
    """iddia metninden (kanun_kodu, madde_no) dondurur. madde None olabilir."""
    kod, bitis = kanun_coz(iddia)
    return kod, (madde_coz(iddia, bitis) if kod else None)


# ------------------------------------------------------------- ALTIN KONTROL
def beklenen(satir):
    """uretim_sablonu'ndan dogru atifi turetir (pozitif kontrol referansi)."""
    s, kanun, madde = satir["uretim_sablonu"], satir["kanun"], satir["madde"]
    m = re.match(r"P5_maddeshift\((.+?)→(.+?)\)", s)
    if m:
        return kanun, m.group(2)
    m = re.match(r"P5_lawshuffle\((.+?)→(.+?)\)", s)
    if m:
        return m.group(2), None
    if s in ("P1_madde_atifli",) or s.startswith("P6_"):
        return kanun, madde
    # P1_verbatim, P2_swap, P3_*, P4_*: yalnizca kanun adiyla atif
    return kanun, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--esik", type=float, default=0.98,
                    help="kabul edilebilir asgari cozumleme dogrulugu")
    ap.add_argument("--goster", type=int, default=15, help="basilacak hata sayisi")
    a = ap.parse_args()

    with open(a.claims, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    tam, k_ok, m_ok, hatalar = 0, 0, 0, []
    sablon_hata = collections.Counter()
    for r in rows:
        bk, bm = beklenen(r)
        ck, cm = atif(r["iddia"])
        if ck == bk:
            k_ok += 1
        if cm == bm:
            m_ok += 1
        if ck == bk and cm == bm:
            tam += 1
        else:
            hatalar.append((r, (bk, bm), (ck, cm)))
            sablon_hata[r["uretim_sablonu"].split("(")[0]] += 1

    n = len(rows)
    print("=" * 78)
    print("ATIF COZUMLEYICI — POZITIF KONTROL")
    print("=" * 78)
    print(f"  madde sayisi        : {n}")
    print(f"  kanun dogru         : {k_ok}/{n}  ({k_ok/n:.4f})")
    print(f"  madde dogru         : {m_ok}/{n}  ({m_ok/n:.4f})")
    print(f"  ikisi birden dogru  : {tam}/{n}  ({tam/n:.4f})")
    if sablon_hata:
        print(f"\n  hatalarin sablon dagilimi: {dict(sablon_hata)}")
    for r, b, c in hatalar[:a.goster]:
        print(f"\n  id={r['id']} sablon={r['uretim_sablonu']}")
        print(f"    beklenen={b}  cozulen={c}")
        print(f"    iddia: {r['iddia'][:110]}")

    print()
    if tam / n < a.esik:
        print(f"! DURDU: cozumleme dogrulugu {tam/n:.4f} < esik {a.esik}.")
        print("  Dayanakli kollari BU HALIYLE KOSMAYIN; atif yanlis pasaji getirir.")
        sys.exit(1)
    print(f"POZITIF KONTROL GECTI ({tam/n:.4f} >= {a.esik}).")
    # atif turu dagilimi — dayanak birimi planlamasi icin
    d = collections.Counter()
    for r in rows:
        ck, cm = atif(r["iddia"])
        d["madde duzeyinde" if cm else "belge duzeyinde"] += 1
    print(f"  dayanak birimi: {dict(d)}")


if __name__ == "__main__":
    main()
