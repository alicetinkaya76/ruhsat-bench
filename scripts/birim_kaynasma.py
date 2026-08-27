# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — BIRIM KAYNASMASI TARAMASI  (TBDY)

BULGU
-----
uret_iddia_v3_6.bentler() TBDY'yi su kalipla boluyor:

    \\b(\\d{1,2}(?:\\.\\d{1,2}){1,3})\\s*[–\\-—]\\s        ->  "15.3.1 - Baslik"

TBDY metninde iki sorun var:

  (1) TANINMAYAN BASLIK. Bentlerin bir kismi "15.3.1. Baslik" biciminde,
      yani numaradan sonra NOKTA ile yazilmis. Kalip bunu gormuyor;
      o bendin metni bir onceki taninan eslesmenin govdesine yigiliyor.
      Olcum: yalnizca nokta biciminde gecen 456 benzersiz numara var.

  (2) SAHTE BIRIM. "Tablo 15.1 - Binalar icin..." ve "Sekil 4.2 - ..."
      gibi tablo/sekil basliklari da kalibi saglar ve BIRIM olur.
      Bu sahte birim, bir sonraki eslesmeye kadar olan her seyi yutar.

SONUC ZINCIRI
-------------
    ayristirici bentleri kaynastirdi
      -> uretec metni YANLIS bende atfetti
        -> ALTIN ETIKET yanlis oldu

Uzlasi maddesi 364 bunun kanitli ornegi: "Gevrek olarak hasar goren
elemanlarda bu siniflandirma gecerli degildir" cumlesi korpusta
TBDY/15.1 biriminde gorunuyor, ama o birimin govdesi icinde
"15.3. YAPI ELEMANLARINDA... 15.3.1. Kesit Hasar Durumlari" basliklari
gomulu; cumle gercekte 15.3.1'e ait. Insaat muhendisi bunu elle yakaladi.

NEDEN POZITIF KONTROLLER GORMEDI
--------------------------------
Kontrol A alintiyi "dogru birimde" buldu, cunku YANLIS birim onu iceriyor.
Kontrol B atif yapilan birimin VAR OLDUGUNA bakiyor; kaynasmis birim var.
Iki kontrol de bu hata sinifina kordur. Bu tarama o bosluga bakar.

KULLANIM
--------
    python -u scripts\\birim_kaynasma.py
    python -u scripts\\birim_kaynasma.py --rapor sonuclar\\kaynasma_raporu.txt
"""
import argparse
import collections
import csv
import json
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

from atif_coz import atif                                    # noqa: E402

# taninan sinir (bentler ile ayni kalip)
TANINAN = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\s*[–\-—]\s")
# taninmayan baslik: "15.3.1. Kesit Hasar Durumlari"
GOMULU = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\.\s+(?=[A-ZÇĞİÖŞÜ])")
# sahte birim isareti: eslesmenin hemen oncesinde Tablo/Sekil/Denklem
SAHTE_ONEK = re.compile(r"(Tablo|Şekil|Denklem|Çizelge)\s*$", re.IGNORECASE)
GORE = re.compile(r"\sgöre\s")
SERH = re.compile(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]{0,140}\)")


def anahtar(t):
    t = unicodedata.normalize("NFC", t)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"')):
        t = t.replace(a, b)
    return re.sub(r"\s+", "", SERH.sub(" ", t).lower().replace("\u0307", ""))


def icerik(iddia):
    m = GORE.search(iddia)
    return (iddia[m.end():] if m else iddia).strip().rstrip(".").strip()


def sirala(no):
    return [int(p) if p.isdigit() else p for p in str(no).split(".")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--korpus", default="data/korpus/korpus.jsonl")
    ap.add_argument("--rapor", default="sonuclar/kaynasma_raporu.txt")
    ap.add_argument("--csv", default="sonuclar/kaynasma_etkilenen.csv")
    a = ap.parse_args()

    import uret_iddia_v3_6 as UR

    yol = os.path.join(a.pdf_dir, UR.LAWS["TBDY"]["dosya"])
    metin = UR.normalize(UR.pdf_metin(yol))
    birimler = UR.bentler(metin)

    R = []                                        # rapor satirlari
    def y(s=""):
        print(s)
        R.append(s)

    y("=" * 82)
    y("TBDY BIRIM KAYNASMASI TARAMASI")
    y("=" * 82)

    # ---------------------------------------------- 1) BASLIK BICIMLERI
    tire = list(TANINAN.finditer(metin))
    nokta = list(GOMULU.finditer(metin))
    tn = {m.group(1) for m in tire}
    nn = {m.group(1) for m in nokta}
    y(f"\n1) BASLIK BICIMLERI")
    y(f"    'N.N.N - Baslik' (taninan)   : {len(tire):>5} eslesme, {len(tn)} benzersiz numara")
    y(f"    'N.N.N. Baslik'  (taninmayan): {len(nokta):>5} eslesme, {len(nn)} benzersiz numara")
    y(f"    YALNIZCA taninmayan bicimde olan numara: {len(nn - tn)}")
    y(f"    korpusta olusan birim sayisi: {len(birimler)}")

    # ---------------------------------------------- 2) SAHTE BIRIMLER
    sahte = []
    for m in tire:
        onceki = metin[max(0, m.start() - 14):m.start()]
        if SAHTE_ONEK.search(onceki.strip()):
            sahte.append((m.group(1), onceki.strip()[-10:]))
    sahte_no = {s[0] for s in sahte} & set(birimler)
    y(f"\n2) SAHTE BIRIM (tablo/sekil basligindan olusan)")
    y(f"    tablo/sekil onekli eslesme: {len(sahte)}")
    y(f"    bunlardan KORPUSTA BIRIM olan: {len(sahte_no)}")
    y(f"    ornekler: {sorted(sahte_no, key=sirala)[:16]}")

    # ---------------------------------------------- 3) KAYNASMIS BIRIMLER
    kaynasmis = {}
    for no, d in birimler.items():
        g = [(m.start(), m.group(1)) for m in GOMULU.finditer(d["metin"])
             if m.group(1) != no]
        if g:
            kaynasmis[no] = g
    y(f"\n3) KAYNASMIS BIRIM (govdesinde gomulu baslik tasiyan)")
    y(f"    {len(kaynasmis)}/{len(birimler)} birim  ({len(kaynasmis)/len(birimler):.3f})")
    y(f"    yutulan bent sayisi (toplam gomulu baslik): "
      f"{sum(len(v) for v in kaynasmis.values())}")

    # ---------------------------------------------- 4) ETKILENEN IDDIALAR
    with open(a.claims, encoding="utf-8-sig") as fh:
        C = list(csv.DictReader(fh))
    tbdy = [x for x in C if x["kanun"] == "TBDY"]

    etkilenen, temiz, bulunamadi = [], 0, []
    for x in tbdy:
        no = str(x["madde"])
        d = birimler.get(no)
        if d is None:
            bulunamadi.append(x)
            continue
        ic = anahtar(icerik(x["iddia"]))
        gov = anahtar(d["metin"])
        i = gov.find(ic) if ic else -1
        if i < 0:
            bulunamadi.append(x)
            continue
        # gomulu basliklarin ANAHTAR uzayindaki konumunu bul
        onceki_baslik = None
        for m in GOMULU.finditer(d["metin"]):
            konum = len(anahtar(d["metin"][:m.end()]))
            if konum <= i and m.group(1) != no:
                onceki_baslik = m.group(1)
        if onceki_baslik:
            atifli_kanun, atifli_madde = atif(x["iddia"])
            etkilenen.append({
                "id": x["id"], "probe": x["probe"],
                "uretim_sablonu": x["uretim_sablonu"], "gold": x["gold"],
                "csv_madde": no, "iddia_atfi": atifli_madde or "(atifsiz)",
                "GERCEK_BENT": onceki_baslik,
                "iddia": x["iddia"][:150],
            })
        else:
            temiz += 1

    y(f"\n4) ETKILENEN IDDIALAR (TBDY, n={len(tbdy)})")
    y(f"    icerigi gomulu bir baslIktan SONRA gelen : {len(etkilenen)}")
    y(f"    birimin basinda, temiz                   : {temiz}")
    y(f"    icerik birimde bulunamadi                : {len(bulunamadi)}")
    if tbdy:
        y(f"    ETKILENME ORANI: {len(etkilenen)/len(tbdy):.4f}")

    y(f"\n    prob dagilimi: "
      f"{dict(collections.Counter(e['probe'] for e in etkilenen))}")
    y(f"    altin dagilimi: "
      f"{dict(collections.Counter(e['gold'] for e in etkilenen))}")

    # P1: atif yanlis bende -> ALTIN HATASI adayi
    p1 = [e for e in etkilenen if e["probe"] == "P1_dogrudan"]
    y(f"\n5) ALTIN HATASI ADAYLARI  (P1, altin=DOGRU ama atif yanlis bende)")
    y(f"    {len(p1)} madde. Bunlarda iddia bir bende atif yapiyor ya da")
    y(f"    kaynak olarak o bendi gosteriyor, fakat cumle GERCEKTE baska")
    y(f"    bir bende ait. Bu, P5_maddeshift ile ayni hata sinifidir ve")
    y(f"    altin DOGRU yerine YANLIS olmalidir.")
    y(f"\n    {'id':<6}{'sablon':<22}{'csv':<12}{'iddia atfi':<12}{'GERCEK':<12}")
    for e in sorted(p1, key=lambda e: sirala(e["csv_madde"]))[:40]:
        y(f"    {e['id']:<6}{e['uretim_sablonu'][:21]:<22}{e['csv_madde']:<12}"
          f"{str(e['iddia_atfi']):<12}{e['GERCEK_BENT']:<12}")
    if len(p1) > 40:
        y(f"    ... {len(p1)-40} madde daha (CSV'de tamami)")

    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(R) + "\n")
    if etkilenen:
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(etkilenen[0].keys()))
            w.writeheader()
            w.writerows(etkilenen)
    print(f"\nyazildi: {a.rapor}")
    print(f"yazildi: {a.csv}")


if __name__ == "__main__":
    main()
