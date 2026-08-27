# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — KORPUS BIRIM INCELEME

Uc is yapar:
  --liste   : bir kanunun birimlerini (istege bagli onekle) uzunluklariyla sirala
  --birim   : bir birimin tam metnini bas
  --ara     : bir metin parcasinin hangi birimlerde gectigini bul

ACIL KULLANIM (uzlasi maddesi 364):
  Insaat muhendisi "cumle 15.1'de degil 15.3.1'de" diyor. Korpus aramasi
  cumleyi yalniz 15.1'de buldu. Fakat bu iki sekilde olabilir:
    (a) cumle gercekten 15.1'e ait  -> ISG uzmani hakli
    (b) bentler() 15.3.1'i AYRI BIRIM olarak tanimamis, metni 15.1'in
        icine dusmus -> olcum soruyu goremiyor, INS_MUH hakli olabilir
  Ayirt etmek icin 15.3 ile baslayan birimlerin VAR OLUP OLMADIGINA bakilir.

    python -u scripts\\birim_bak.py --kanun TBDY --liste --onek 15.
    python -u scripts\\birim_bak.py --kanun TBDY --birim 15.1
    python -u scripts\\birim_bak.py --ara "Gevrek olarak hasar goren"
"""
import argparse
import json
import os
import re
import sys
import unicodedata

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                       # noqa: BLE001
        pass

SERH = re.compile(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]{0,140}\)")


def anahtar(t):
    t = unicodedata.normalize("NFC", t)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"')):
        t = t.replace(a, b)
    t = SERH.sub(" ", t).lower().replace("\u0307", "")
    return re.sub(r"\s+", "", t)


def sirala(no):
    """15.10 > 15.9 olacak sekilde dogal sirala."""
    return [int(p) if p.isdigit() else p for p in str(no).split(".")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--korpus", default="data/korpus/korpus.jsonl")
    ap.add_argument("--kanun", default=None)
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("--onek", default="")
    ap.add_argument("--birim", default=None)
    ap.add_argument("--ara", default=None)
    ap.add_argument("--karakter", type=int, default=1200)
    a = ap.parse_args()

    if not os.path.exists(a.korpus):
        print(f"! bulunamadi: {a.korpus}")
        sys.exit(1)
    K = {}
    with open(a.korpus, encoding="utf-8-sig") as fh:
        for s in fh:
            if s.strip():
                v = json.loads(s)
                K[(v["kanun"], v["birim"])] = v
    print(f"korpus: {len(K)} birim\n")

    if a.liste:
        se = [v for (kk, _), v in K.items()
              if (a.kanun is None or kk == a.kanun) and v["birim"].startswith(a.onek)]
        se.sort(key=lambda v: sirala(v["birim"]))
        print(f"{a.kanun or 'TUM'} / onek '{a.onek}' -> {len(se)} birim")
        print(f"  {'birim':<14}{'karakter':>9}  ilk satir")
        for v in se:
            ilk = re.sub(r"\s+", " ", v["metin"])[:78]
            print(f"  {v['birim']:<14}{len(v['metin']):>9}  {ilk}")
        if not se:
            print("  (hicbir birim bu onekle baslamiyor)")
        print()

    if a.birim:
        v = K.get((a.kanun, a.birim))
        if v is None:
            print(f"! {a.kanun}/{a.birim} korpusta YOK")
            yakin = sorted((b for (kk, b) in K if kk == a.kanun
                            and b.startswith(a.birim.split(".")[0] + ".")),
                           key=sirala)[:25]
            print(f"  ayni ana bolumdeki birimler: {yakin}")
        else:
            print(f"=== {a.kanun}/{a.birim}  ({len(v['metin'])} karakter, "
                  f"degisiklik yillari={v.get('degisiklik_yillari')}) ===")
            print(v["metin"][:a.karakter])
            if len(v["metin"]) > a.karakter:
                print(f"\n... [{len(v['metin']) - a.karakter} karakter daha]")
        print()

    if a.ara:
        h = anahtar(a.ara)
        bul = [v for (kk, _), v in K.items()
               if (a.kanun is None or kk == a.kanun) and h in anahtar(v["metin"])]
        bul.sort(key=lambda v: (v["kanun"], sirala(v["birim"])))
        print(f"ARAMA: {a.ara!r}")
        print(f"  {len(bul)} birimde bulundu")
        for v in bul:
            i = anahtar(v["metin"]).find(h)
            oran = i / max(len(anahtar(v["metin"])), 1)
            print(f"    {v['kanun']}/{v['birim']:<14}"
                  f"birimin %{oran*100:.0f}'inde  (birim {len(v['metin'])} karakter)")
        if not bul:
            print("    Hicbir birimde yok. Ayristirma veya metin farki olabilir.")
        print()


if __name__ == "__main__":
    main()
