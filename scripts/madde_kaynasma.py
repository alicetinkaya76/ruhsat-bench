# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — MADDE SINIRI TARAMASI  (TBDY DISI BES BELGE)

TBDY'de olculen kusurun ayni belge sinifinda tekrarlanip tekrarlanmadigini
sinar. maddeler() tek kalip kullaniyor:

    (?=(?:Madde|MADDE)\\s+\\d+\\s*[–\\-—])        ->  "Madde 12 - " / "MADDE 12 –"

Turk mevzuat metinlerinde ayni sinir baska biciimlerde de yazilabilir:

    "Madde 12 -"    tire         <- TANINIYOR
    "Madde 12."     nokta        <- ?
    "MADDE 12 –"    en-dash      <- TANINIYOR
    "Ek Madde 3 -"  ek madde     <- TANINMIYOR (Madde ile baslamiyor)
    "Geçici Madde 5"             <- TANINMIYOR
    "Madde 12 —"    em-dash      <- TANINIYOR

Bu betik her belgede:
  1. Taninan / taninmayan sinir bicimlerini sayar
  2. Birim govdelerinde GOMULU madde basligi arar (kaynasma isareti)
  3. Kaynasma varsa etkilenen iddialari ve gercek maddeyi cikarir
  4. Etiket sonucunu TBDY ile ayni uc sinifa ayirir

TESPIT, KESMEYEN yontemle yapilir (icerik konumu gomulu basliga gore),
cunku TBDY'de olculdu: bolerek tespit, icerigi ikiye kesip gercek
adaylari GORUNMEZ yapabiliyor.

KULLANIM
--------
    python -u scripts\\madde_kaynasma.py
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

from atif_coz import atif                                    # noqa: E402

TANINAN = re.compile(r"(?:Madde|MADDE)\s+(\d+)\s*[–\-—]")
# taninmayan aday bicimler
ADAYLAR = {
    "nokta":        re.compile(r"(?:Madde|MADDE)\s+(\d+)\s*\.\s+(?=[A-ZÇĞİÖŞÜ])"),
    "bosluk":       re.compile(r"(?:Madde|MADDE)\s+(\d+)\s+(?=[A-ZÇĞİÖŞÜ][a-zçğıöşü])"),
    "ek_madde":     re.compile(r"Ek\s+(?:Madde|MADDE)\s+(\d+)"),
    "gecici_madde": re.compile(r"(?:Geçici|GEÇİCİ)\s+(?:Madde|MADDE)\s+(\d+)"),
}
GOMULU_TUM = re.compile(
    r"(?:(?:Ek|Geçici|EK|GEÇİCİ)\s+)?(?:Madde|MADDE)\s+(\d+)\s*(?:[–\-—]|\.\s+(?=[A-ZÇĞİÖŞÜ]))")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--csv", default="sonuclar/madde_kaynasma_adaylari.csv")
    a = ap.parse_args()

    import uret_iddia_v3_6 as UR

    with open(a.claims, encoding="utf-8-sig") as fh:
        C = list(csv.DictReader(fh))

    print("=" * 84)
    print("MADDE SINIRI TARAMASI — TBDY DISI BES BELGE")
    print("=" * 84)

    tum_aday = []
    for kod, meta in UR.LAWS.items():
        if meta["tur"] == "tbdy":
            continue
        t = UR.normalize(UR.pdf_metin(os.path.join(a.pdf_dir, meta["dosya"])))
        B = UR.maddeler(t)
        tan = {m.group(1) for m in TANINAN.finditer(t)}

        print(f"\n{'-'*84}\n{kod}  ({meta['ad'][:52]})")
        print(f"  birim: {len(B)}   taninan sinir eslesmesi: "
              f"{len(list(TANINAN.finditer(t)))}")
        for ad, kal in ADAYLAR.items():
            ms = list(kal.finditer(t))
            yeni = {m.group(1) for m in ms} - tan
            print(f"    {ad:<14}{len(ms):>4} eslesme   taninanlarda OLMAYAN numara: {len(yeni)}")

        # gomulu baslik
        kaynasmis = {}
        for no, d in B.items():
            g = [(m.start(), m.group(1)) for m in GOMULU_TUM.finditer(d["metin"])
                 if m.group(1) != str(no)]
            if g:
                kaynasmis[no] = g
        print(f"  KAYNASMIS BIRIM: {len(kaynasmis)}/{len(B)}"
              f"   gomulu baslik: {sum(len(v) for v in kaynasmis.values())}")

        # etkilenen iddialar
        bel = [x for x in C if x["kanun"] == kod]
        etk = 0
        for x in bel:
            if x["probe"] in ("P2_sayisal", "P3_anakronizm", "P4_uydurma"):
                continue
            d = B.get(int(x["madde"])) if str(x["madde"]).isdigit() else None
            if d is None:
                continue
            ic = anahtar(icerik(x["iddia"]))
            gov = anahtar(d["metin"])
            i = gov.find(ic) if ic else -1
            if i < 0:
                continue
            onceki = None
            for m in GOMULU_TUM.finditer(d["metin"]):
                k = len(anahtar(d["metin"][:m.end()]))
                if k <= i and m.group(1) != str(x["madde"]):
                    onceki = m.group(1)
            if onceki:
                etk += 1
                atk, atm = atif(x["iddia"])
                tum_aday.append({
                    "kanun": kod, "id": x["id"], "probe": x["probe"],
                    "uretim_sablonu": x["uretim_sablonu"], "gold": x["gold"],
                    "kayitli_madde": x["madde"], "iddia_atfi": atm or "(atifsiz)",
                    "gercek_madde": onceki,
                    "ETIKET_SONUCU": (
                        "ALTIN DOGRU->YANLIS"
                        if x["uretim_sablonu"] == "P1_madde_atifli"
                        else "ALTIN DEGISMEZ (kaynak kaydi duzelir)"
                        if x["probe"] == "P1_dogrudan"
                        else "ALTIN DEGISMEZ (zaten YANLIS)"),
                    "iddia": x["iddia"][:200],
                })
        print(f"  ETKILENEN IDDIA: {etk}/{len(bel)}")

    print("\n" + "=" * 84)
    print("TOPLAM SONUC")
    print("=" * 84)
    print(f"  bes belgede etkilenen iddia: {len(tum_aday)}")
    if tum_aday:
        print(f"  kanun dagilimi: "
              f"{dict(collections.Counter(x['kanun'] for x in tum_aday))}")
        for k, v in collections.Counter(x["ETIKET_SONUCU"] for x in tum_aday).items():
            print(f"    {v:>3}  {k}")
        print(f"\n  {'kanun':<9}{'id':<6}{'sablon':<20}{'kayitli':<9}"
              f"{'GERCEK':<9}{'altin'}")
        for x in tum_aday:
            print(f"  {x['kanun']:<9}{x['id']:<6}{x['uretim_sablonu'][:19]:<20}"
                  f"{x['kayitli_madde']:<9}{x['gercek_madde']:<9}{x['gold']}")
        os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(tum_aday[0].keys()))
            w.writeheader()
            w.writerows(tum_aday)
        print(f"\n  yazildi: {a.csv}")
    else:
        print("  Bes belgede kaynasma kaynakli yanlis atif BULUNAMADI.")
        print("  TBDY'deki kusur bu belge sinifina yayilmiyor.")


if __name__ == "__main__":
    main()
