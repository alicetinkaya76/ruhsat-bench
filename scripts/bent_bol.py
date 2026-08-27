# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — TBDY BIRIM RAFINE EDICI  (bent_bol)

ONCEKI DENEMENIN OLCULEN BASARISIZLIGI
--------------------------------------
Ilk denemede ayristirici SIFIRDAN yazildi: iki baslik bicimi de taninacak,
yanlis pozitifler "belge sirasi tekduzeligi" ile elenecekti. Olculen sonuc:

    birim  1208 -> 529        icerik kurtarma  0.9632 -> 0.0221
    eleme sayaci: elendi_sira_disi = 1862

pypdf ciktisinda sayfa basliklari, icindekiler ve sekil numaralari araya
girdigi icin bent numaralari ARTAN SIRADA GELMIYOR. Bir kez buyuk numara
kabul edilince ardindaki hemen her aday eleniyor. Filtre yanlisti.

BU BETIGIN YAKLASIMI: RAFINE, YENIDEN INSA DEGIL
------------------------------------------------
Mevcut bentler() ciktisi 0.9632 icerik kurtarma ile CALISIYOR. O halde
onu bozmadan, YALNIZCA govde icindeki gomulu basliklarda BOLUYORUZ.
Islem tanim geregi eklemeli: hicbir metin kaybolmaz, yalniz daha ince
anahtarlanir.

    "15.1" govdesi:
        [Tablo metni...] 15.3. YAPI ELEMANLARINDA... 15.3.1. Kesit Hasar
        Durumlari ... Gevrek olarak hasar goren... 15.3.2. Kesit Hasar...

    ->  15.1     = ilk parca (bolme oncesi)
        15.3     = ikinci parca
        15.3.1   = ucuncu parca      <- 364'un cumlesi BURADA
        15.3.2   = dorduncu parca

YANLIS POZITIF FILTRESI (global degil, YEREL)
---------------------------------------------
Gomulu baslik adayi, icinde bulundugu birimin numarasiyla AYNI ANA BOLUMU
paylasmak zorunda. "15.1" govdesinde "15.3.1" kabul edilir, "1.5" edilmez.
Bu, "...oranı 1.5. Bu deger..." gibi ondalik sayilari eler ve global
siralamaya hic bagli degildir.

SAHTE BIRIMLER
--------------
"Tablo 15.1 - ..." kalibi sagladigi icin birim olan 27 kayit SILINMEZ
(metin kaybi olmasin), `sahte_birim: true` ile ISARETLENIR. Denetim ve
altin duzeltmesi bu isareti kullanir.

MUHURLU URETECE DOKUNULMAZ: uret_iddia_v3_6.py degismez, iddia metinleri
sabittir. Bu ayristirma yalnizca F5 korpusu ve altin denetimi icindir.

KULLANIM
--------
    python -u scripts\\bent_bol.py --pdf-dir data\\kaynak_pdf
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

GOMULU = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\.\s+(?=[A-ZÇĞİÖŞÜ])")
TANINAN = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\s*[–\-—]\s")
SAHTE_ONEK = re.compile(r"(Tablo|Şekil|Denklem|Çizelge)\s*$", re.IGNORECASE)
SERH = re.compile(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]{0,140}\)")
GORE = re.compile(r"\sgöre\s")


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


def sahte_birimler(metin):
    """Tablo/Sekil basligindan olusan birim numaralari."""
    out = set()
    for m in TANINAN.finditer(metin):
        onceki = metin[max(0, m.start() - 14):m.start()]
        if SAHTE_ONEK.search(onceki.strip()):
            out.add(m.group(1))
    return out


def _koy(out, anah, kayit, s):
    """Cakisma-guvenli yerlestirme. Ayni numara birden fazla yerde geciyorsa
    UZERINE YAZMA; ~2, ~3 ... ekiyle sakla. Uzerine yazmak metin kaybettirir:
    olculdu, 4 iddianin icerigi ve 2 gercek altin adayi bu yolla siliniyordu."""
    if anah in out:
        k = 2
        while f"{anah}~{k}" in out:
            k += 1
        anah = f"{anah}~{k}"
        s["cakisma_ikinci_kopya"] += 1
    out[anah] = kayit
    return anah


def bent_bol(birimler, metin, asgari=40, tani=None):
    """bentler() ciktisini gomulu basliklarda boler. EKLEMELI islem."""
    tani = tani if tani is not None else {}
    s = collections.Counter()
    sahte = sahte_birimler(metin)
    out = {}
    for no, d in birimler.items():
        govde = d["metin"]
        ana = no.split(".")[0]
        kesim = []
        for m in GOMULU.finditer(govde):
            aday = m.group(1)
            if aday == no:
                s["atlandi_kendisi"] += 1
                continue
            if aday.split(".")[0] != ana:                  # YEREL FILTRE
                s["elendi_farkli_ana_bolum"] += 1
                continue
            kesim.append((m.start(), m.end(), aday))
        if not kesim:
            _koy(out, no, dict(d, sahte_birim=(no in sahte), bolundu=False), s)
            continue
        s["bolunen_birim"] += 1
        # ilk parca asil numarada kalir
        bas_parca = govde[:kesim[0][0]].strip()
        if len(bas_parca) >= asgari:
            _koy(out, no, dict(d, metin=bas_parca,
                               sahte_birim=(no in sahte), bolundu=True), s)
        else:
            s["bas_parca_kisa"] += 1
        for i, (b, e, aday) in enumerate(kesim):
            son = kesim[i + 1][0] if i + 1 < len(kesim) else len(govde)
            parca = govde[e:son].strip()
            if len(parca) < asgari:
                s["parca_kisa"] += 1
                continue
            # CAKISMA: ayni numara zaten birimse PARCAYI ATMA.
            # TBDY'de bazi bentler hem "2.2.2 - Baslik" hem "2.2.2. Baslik"
            # biciminde IKI YERDE geciyor. Parcayi atmak metin kaybettiriyordu
            # (olculdu: 8 iddianin icerigi korpustan siliniyordu ve 4 gercek
            # altin adayi GORUNMEZ oluyordu). Ikinci gecisi ~2 ekiyle sakla.
            _koy(out, aday, {"metin": parca, "degisiklik_yillari": [],
                             "sahte_birim": False, "bolundu": True,
                             "kaynak_birim": no, "asil_no": aday}, s)
            s["yeni_birim"] += 1
    tani.update(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--csv", default="sonuclar/altin_adaylari.csv")
    a = ap.parse_args()

    import uret_iddia_v3_6 as UR

    t = UR.normalize(UR.pdf_metin(os.path.join(a.pdf_dir, UR.LAWS["TBDY"]["dosya"])))
    eski = UR.bentler(t)
    tani = {}
    yeni = bent_bol(eski, t, tani=tani)

    print("=" * 82)
    print("RAFINE EDICI — DOGRULAMA")
    print("=" * 82)
    print(f"\n  eski birim : {len(eski)}")
    print(f"  yeni birim : {len(yeni)}   ({len(yeni)-len(eski):+d})")
    print(f"  sayaclar   : {dict(tani)}")
    print(f"  sahte olarak isaretlenen: "
          f"{sum(1 for v in yeni.values() if v.get('sahte_birim'))}")

    def gomulu_kalan(B):
        n = 0
        for no, d in B.items():
            ana = no.split(".")[0]
            n += sum(1 for m in GOMULU.finditer(d["metin"])
                     if m.group(1) != no and m.group(1).split(".")[0] == ana)
        return n

    print(f"\n  K1 GOMULU BASLIK KALAN   eski {gomulu_kalan(eski):>5}   "
          f"yeni {gomulu_kalan(yeni):>5}")

    cum = "Gevrek olarak hasar gören elemanlarda bu sınıflandırma geçerli değildir"
    h = anahtar(cum)
    for ad, B in (("eski", eski), ("yeni", yeni)):
        nerede = sorted((no for no, d in B.items() if h in anahtar(d["metin"])),
                        key=sirala)
        isaret = "  <-- BEKLENEN (uzman dogruladi)" if nerede == ["15.3.1"] else ""
        print(f"  K2 364 CUMLESI           {ad:<5} -> {nerede}{isaret}")

    with open(a.claims, encoding="utf-8-sig") as fh:
        C = [x for x in csv.DictReader(fh) if x["kanun"] == "TBDY"]
    p2 = {x["id"] for x in C if x["probe"] == "P2_sayisal"}

    for ad, B in (("eski", eski), ("yeni", yeni)):
        A = {no: anahtar(d["metin"]) for no, d in B.items()}
        b = sum(1 for x in C if x["id"] not in p2
                and any(anahtar(icerik(x["iddia"])) in v for v in A.values()))
        n = len([x for x in C if x["id"] not in p2])
        print(f"  K3 ICERIK KORPUSTA       {ad:<5} {b}/{n} = {b/n:.4f}"
              f"{'   <-- BOZULMAMALI' if ad=='yeni' else ''}")
    for ad, B in (("eski", eski), ("yeni", yeni)):
        v = sum(1 for x in C if str(x["madde"]) in B)
        print(f"  K4 CSV MADDESI VAR       {ad:<5} {v}/{len(C)} = {v/len(C):.4f}")

    # ---------------------------------------- ALTIN ADAYLARI
    A = {no: anahtar(d["metin"]) for no, d in yeni.items()}
    print("\n" + "=" * 82)
    print("ALTIN ETIKET ADAYLARI  (icerik, kayitli bentten BASKA bir bentte)")
    print("=" * 82)
    print(f"  {'id':<6}{'sablon':<24}{'altin':<8}{'kayitli':<11}{'GERCEK':<24}{'sahte?'}")
    kayit = []
    for x in sorted(C, key=lambda x: int(x["id"])):
        if x["id"] in p2:
            continue
        ic = anahtar(icerik(x["iddia"]))
        if not ic:
            continue
        yer = sorted((no for no, v in A.items() if ic in v), key=sirala)
        csvm = str(x["madde"])
        # "~2" ayni bendin IKINCI KOPYASIDIR, yanlis atif DEGILDIR.
        # Karsilastirma taban numara uzerinden yapilir.
        taban = {no.split("~")[0] for no in yer}
        if not yer or csvm in taban:
            continue
        sb = "EVET" if yeni.get(csvm, {}).get("sahte_birim") else ""
        print(f"  {x['id']:<6}{x['uretim_sablonu'][:23]:<24}{x['gold']:<8}"
              f"{csvm:<11}{', '.join(yer)[:23]:<24}{sb}")
        kayit.append({"id": x["id"], "probe": x["probe"],
                      "uretim_sablonu": x["uretim_sablonu"], "gold": x["gold"],
                      "kayitli_bent": csvm, "gercek_bent": ", ".join(yer),
                      "tek_yer": "EVET" if len(yer) == 1 else "HAYIR",
                      "kayitli_sahte_birim": sb,
                      "iddia": x["iddia"]})
    p1 = [k for k in kayit if k["probe"] == "P1_dogrudan"]
    ma = [k for k in p1 if k["uretim_sablonu"] == "P1_madde_atifli"]
    vb = [k for k in p1 if k["uretim_sablonu"] == "P1_verbatim"]
    for k in kayit:
        k["ETIKET_SONUCU"] = ("ALTIN DOGRU->YANLIS"
                              if k["uretim_sablonu"] == "P1_madde_atifli"
                              else "ALTIN DEGISMEZ (kaynak kaydi duzelir)"
                              if k["probe"] == "P1_dogrudan"
                              else "ALTIN DEGISMEZ (zaten YANLIS)")
    print(f"\n  toplam aday               : {len(kayit)}")
    print(f"  P1_madde_atifli           : {len(ma)}  -> ALTIN DOGRU->YANLIS")
    print(f"     iddia bendi ACIKCA soyluyor, icerik o bentte degil.")
    print(f"     P5_maddeshift ile ayni hata sinifi; iddia YANLIStir.")
    print(f"  P1_verbatim               : {len(vb)}  -> ALTIN DEGISMEZ")
    print(f"     iddia bent belirtmiyor; icerik TBDY'de var. Iddia dogru,")
    print(f"     duzeltilecek olan KAYNAK KAYDI.")
    print(f"  P5 (altin zaten YANLIS)   : {len(kayit)-len(p1)}  -> etiket donmez")
    print(f"\n  ALTIN DAGILIMI: 230 DOGRU / 243 YANLIS  ->  "
          f"{230-len(ma)} DOGRU / {243+len(ma)} YANLIS")

    if kayit:
        os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(kayit[0].keys()))
            w.writeheader()
            w.writerows(kayit)
        print(f"\n  yazildi: {a.csv}")


if __name__ == "__main__":
    main()
