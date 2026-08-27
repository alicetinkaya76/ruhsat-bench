# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — DUZELTILMIS TBDY BENT AYRISTIRICISI  (bentler2)

MEVCUT AYRISTIRICININ KUSURU
----------------------------
uret_iddia_v3_6.bentler() tek kalip kullaniyor:

    \\b(\\d{1,2}(?:\\.\\d{1,2}){1,3})\\s*[–\\-—]\\s      ->  "15.3.1 - Baslik"

Olculen sonuclar:
  * TBDY basliklarinin bir kismi "15.3.1. Baslik" biciminde -> gorunmuyor.
    Yalnizca bu bicimde gecen 456 benzersiz bent numarasi var.
  * "Tablo 15.1 - ..." / "Sekil 4.2 - ..." kalibi sagliyor ve BIRIM oluyor;
    27 sahte birim. Sahte birim, sonraki sinira kadar her seyi yutuyor.
  * 1208 birimin 311'i (%25.7) govdesinde gomulu baslik tasiyor.
  * TBDY iddialarinin 21'inde (155'te) icerik gomulu bir baslIktan sonra
    geliyor; yani kaydedilen bent cumlenin gercek yeri degil.

BU BETIK MUHURLU URETECE DOKUNMAZ
---------------------------------
uret_iddia_v3_6.py degistirilmez; iddia metinleri sabittir. Burada
uretilen ayristirma YALNIZCA (a) F5 dayanak korpusu ve (b) altin etiket
denetimi icin kullanilir.

DUZELTMELER
-----------
1. Iki bicim de taninir: "N.N - " ve "N.N. Baslik".
2. Tablo/Sekil/Denklem/Cizelge onekli eslesmeler ELENIR.
3. Metin ici referanslar elenir: "15.3.1'deki", "(Sekil 15.1)", "Bolum 4.2".
4. YANLIS POZITIF FILTRESI — belge sirasi tekdüzeligi:
   bent numaralari belge boyunca ARTAR. Aday numara, kabul edilen son
   numaradan buyuk degilse reddedilir. Bu, "...oranı 1.5. Bu deger..."
   gibi ondalik sayilari 15. bolumun icinde iken eler (1.5 < 15.x).
5. Govde kirpma 2500 -> 4000 (mevcut kirpma 25 bende dokunuyor).

Bu filtre kalibi degil KABUL KURALINI degistirir; yanlis pozitif riskini
sirali dogrulamayla dusurur. Dogrulama ciktida raporlanir.

KULLANIM
--------
    python -u scripts\\bentler2.py --pdf-dir data\\kaynak_pdf
"""
import argparse
import collections
import csv
import os
import re
import sys
import unicodedata

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                       # noqa: BLE001
        pass

ADAY = re.compile(
    r"\b(\d{1,2}(?:\.\d{1,2}){1,3})"
    r"(?:\s*[–\-—]\s|\.\s+(?=[A-ZÇĞİÖŞÜ]))"
)
ONEK_ELE = re.compile(r"(Tablo|Şekil|Denklem|Çizelge|Bölüm|EK|Ek)\s*$", re.IGNORECASE)
SERH = re.compile(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]{0,140}\)")
GORE = re.compile(r"\sgöre\s")


def tup(no):
    return tuple(int(p) for p in no.split("."))


def anahtar(t):
    t = unicodedata.normalize("NFC", t)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"')):
        t = t.replace(a, b)
    return re.sub(r"\s+", "", SERH.sub(" ", t).lower().replace("\u0307", ""))


def icerik(iddia):
    m = GORE.search(iddia)
    return (iddia[m.end():] if m else iddia).strip().rstrip(".").strip()


def bentler2(t, kirp=4000, asgari=60, tani=None):
    """Duzeltilmis TBDY bent ayristiricisi. tani: dict, sayaclari doldurur."""
    tani = tani if tani is not None else {}
    sayac = collections.Counter()
    kabul = []
    son = None
    for m in ADAY.finditer(t):
        no = m.group(1)
        onceki = t[max(0, m.start() - 14):m.start()]
        if ONEK_ELE.search(onceki.strip()):
            sayac["elendi_tablo_sekil"] += 1
            continue
        sonrasi = t[m.end():m.end() + 2]
        if sonrasi[:1] in ("'", "’", ")"):
            sayac["elendi_metin_ici_referans"] += 1
            continue
        try:
            a = tup(no)
        except ValueError:
            sayac["elendi_ayristirilamadi"] += 1
            continue
        if son is not None and a <= son:
            sayac["elendi_sira_disi"] += 1
            continue
        if son is not None and a[0] > son[0] + 1:
            sayac["elendi_bolum_atlamasi"] += 1
            continue
        kabul.append((m.end(), no))
        son = a
        sayac["kabul"] += 1

    out = {}
    for i, (bas, no) in enumerate(kabul):
        bit = kabul[i + 1][0] if i + 1 < len(kabul) else len(t)
        # bir sonraki sinirin baslik oncesi kismini kirp
        govde = t[bas:bit].strip()
        govde = re.sub(r"\s*\d{1,2}(?:\.\d{1,2}){1,3}\s*[–\-—]?\s*$", "", govde)
        if len(govde) < asgari:
            sayac["kisa_atlandi"] += 1
            continue
        if no in out:
            sayac["tekrar_atlandi"] += 1
            continue
        out[no] = {"metin": govde[:kirp], "degisiklik_yillari": []}
    tani.update(sayac)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    a = ap.parse_args()

    import uret_iddia_v3_6 as UR

    t = UR.normalize(UR.pdf_metin(os.path.join(a.pdf_dir, UR.LAWS["TBDY"]["dosya"])))
    eski = UR.bentler(t)
    tani = {}
    yeni = bentler2(t, tani=tani)

    print("=" * 80)
    print("DUZELTILMIS AYRISTIRICI — DOGRULAMA")
    print("=" * 80)
    print(f"\n  eski birim sayisi : {len(eski)}")
    print(f"  yeni birim sayisi : {len(yeni)}   ({len(yeni)-len(eski):+d})")
    print(f"  eleme sayaclari   : {dict(tani)}")
    print(f"  yalniz yenide olan: {len(set(yeni)-set(eski))}")
    print(f"  yalniz eskide olan: {len(set(eski)-set(yeni))}")

    # --- K1: gomulu baslik kalmali mi
    GOM = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\.\s+(?=[A-ZÇĞİÖŞÜ])")
    def gomulu_sayisi(B):
        return sum(1 for no, d in B.items()
                   for m in GOM.finditer(d["metin"]) if m.group(1) != no)
    print(f"\n  K1 GOMULU BASLIK   eski {gomulu_sayisi(eski):>5}   yeni {gomulu_sayisi(yeni):>5}")

    # --- K2: 364 nerede  (insan uzmanin dogruladigi tek vaka)
    cum = "Gevrek olarak hasar gören elemanlarda bu sınıflandırma geçerli değildir"
    h = anahtar(cum)
    for ad, B in (("eski", eski), ("yeni", yeni)):
        nerede = [no for no, d in B.items() if h in anahtar(d["metin"])]
        print(f"  K2 364 CUMLESI     {ad:<5} -> {nerede}   "
              f"{'DOGRU (15.3.1 beklenir)' if nerede == ['15.3.1'] else ''}")

    # --- K3/K4: iddia kumesine karsi
    with open(a.claims, encoding="utf-8-sig") as fh:
        C = [x for x in csv.DictReader(fh) if x["kanun"] == "TBDY"]
    p2 = {x["id"] for x in C if x["probe"] == "P2_sayisal"}     # icerik kasten farkli

    for ad, B in (("eski", eski), ("yeni", yeni)):
        bulundu = kayip = 0
        for x in C:
            if x["id"] in p2:
                continue
            ic = anahtar(icerik(x["iddia"]))
            if any(ic in anahtar(d["metin"]) for d in B.values()):
                bulundu += 1
            else:
                kayip += 1
        n = bulundu + kayip
        print(f"  K3 ICERIK KORPUSTA {ad:<5} {bulundu}/{n} = {bulundu/n:.4f}")

    for ad, B in (("eski", eski), ("yeni", yeni)):
        var = sum(1 for x in C if str(x["madde"]) in B)
        print(f"  K4 CSV MADDESI VAR {ad:<5} {var}/{len(C)} = {var/len(C):.4f}")

    # --- 21 adayin yeni ayristirmadaki durumu
    print("\n" + "=" * 80)
    print("ADAYLARIN YENI AYRISTIRMADA DOGRULANMASI")
    print("=" * 80)
    print(f"  {'id':<6}{'sablon':<24}{'csv':<11}{'YENI KONUM':<26}{'karar'}")
    dogrulanan, dusen, belirsiz = [], [], []
    for x in sorted(C, key=lambda x: int(x["id"])):
        if x["id"] in p2:
            continue
        ic = anahtar(icerik(x["iddia"]))
        if not ic:
            continue
        yer = [no for no, d in yeni.items() if ic in anahtar(d["metin"])]
        csvm = str(x["madde"])
        if not yer or csvm in yer:
            continue
        kayit = (x["id"], x["uretim_sablonu"], csvm, yer, x["gold"], x["probe"])
        if len(yer) == 1:
            dogrulanan.append(kayit)
        else:
            belirsiz.append(kayit)
    for i, s, c, y, g, p in dogrulanan + belirsiz:
        karar = "ATIF YANLIS" if len(y) == 1 else "birden fazla yerde"
        print(f"  {i:<6}{s[:23]:<24}{c:<11}{', '.join(y)[:25]:<26}{karar}")
    print(f"\n  tek ve farkli yerde (atif yanlis)   : {len(dogrulanan)}")
    print(f"  birden fazla yerde (belirsiz)       : {len(belirsiz)}")
    p1d = [k for k in dogrulanan if k[5] == "P1_dogrudan"]
    print(f"  bunlardan P1 (altin DOGRU->YANLIS)  : {len(p1d)}  -> {[k[0] for k in p1d]}")


if __name__ == "__main__":
    main()
