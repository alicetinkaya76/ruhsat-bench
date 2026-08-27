# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — DAYANAK KORPUSU KURULUMU  v2   (F5 asamasi, adim 1)

v1'DEN FARKI — NEDEN GEREKTI
----------------------------
v1'in A kontrolu 0.9433 verdi ve "PDF ayristirma bozuk" dedi. YANLIS TESHIS.
Arsivdeki v5 (onarim oncesi) ve v6 (onarim sonrasi) iddia kumeleri
karsilastirildiginda:

    kaynak_alinti degisen satir: 31   (6331: 24, 4708: 7)
    bosluksuz karsilastirmada v5 ile ayni olan: 31/31

`kelime_onar.py` yalnizca kelime ICINDEKI boslugu duzeltmis
("yaz ili"->"yazili", "cevr esartlarini"->"cevre sartlarini"). Yani v6
alintilari ham PDF metniyle bit bit ESLESMEZ; bu bir bozukluk degil,
kasitli bir onarimdir. v1 onarilmis alintiyi onarilmamis metne karsi
ariyordu.

v2 UC DEGISIKLIK
----------------
1. KARSILASTIRMA ONARIMA BAGISIK. Kapi, tum bosluklar atilarak yapilan
   eslesmeye bakar (onarimin degistirdigi tek sey bosluktur). Katı
   (bosluga duyarli) oran da ayrica raporlanir; o bir metin-sadakati
   olcusudur, kapi degildir.

2. HATA SINIFLANDIRMASI. "bulunamadi" yerine NEREDE bulundugu yazilir:
       dogru birimde      -> sorun yok
       BASKA birimde      -> birim siniri hatasi. Dayanakli kolda model
                             YANLIS maddeyi gorur. TEHLIKELI kategori.
       belgede hic yok    -> gercek metin ayrismasi
   v1 bu ucunu ayirt edemiyordu.

3. KONTROL C — P6 DETERMINISTIK COZULEBILIRLIK.
   Degisiklik serhleri ("(Degisik:RG-29/12/2018-30640)") PDF cikariminda
   sag kaliyor. O halde P6, LLM'siz bir ayristiriciyla cozulebilir mi?
   Kural:
       "md X'te YYYY'de degisiklik yapilmistir" -> DOGRU  <=> YYYY in degisiklik_yillari
       "md X hic degistirilmemistir"            -> DOGRU  <=> degisiklik_yillari bos
   Bu kural 120 P6 maddesinde altina karsi olculur.

   DAIRESELLIK UYARISI: korpusun `degisiklik_yillari` alani ile CSV'nin
   `degisiklik_notu` alani AYNI regex'in AYNI PDF'lere uygulanmasindan
   gelir. Kontrol C, serhlerin HUKUKEN dogru oldugunu KANITLAMAZ; yalnizca
   (a) bilgi kanalinin korpusta var oldugunu ve (b) bu yeniden kurulumun
   ureticiyle ayni sonucu verdigini gosterir. Serhlerin hukuki dogrulugu
   ayri bir uzman denetimi isidir ve makalede oyle yazilmalidir.

KULLANIM
--------
    python -u scripts\\korpus_kur.py
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import collections
import statistics

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

try:
    import uret_iddia_v3_6 as UR          # __main__ korumasi var; uretim KOSMAZ
except Exception as exc:                                    # noqa: BLE001
    print(f"! uret_iddia_v3_6.py import edilemedi: {exc}")
    sys.exit(1)

try:
    from atif_coz import atif
except Exception as exc:                                    # noqa: BLE001
    print(f"! atif_coz.py import edilemedi: {exc}")
    sys.exit(1)

# Rafine ediciler ITHAL edilir, KOPYALANMAZ (EK-5 4: sifirdan yazma denendi,
# kurtarma 0.9632 -> 0.022 ile basarisiz oldu). Ithal basarisizsa --rafine
# sessizce ham ureticiye DUSMEZ; betik hata verir.
try:
    from bent_bol import bent_bol as _bent_bol
    from maddeler2 import maddeler2 as _maddeler2
    _RAFINE_VAR = True
except Exception as _exc:                                   # noqa: BLE001
    _RAFINE_VAR, _RAFINE_HATA = False, _exc

TIRNAK = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}


def _tirnak(t):
    for a, b in TIRNAK.items():
        t = t.replace(a, b)
    return t


def anahtar_kati(t):
    """Bosluga DUYARLI karsilastirma anahtari. Metin sadakati olcusu."""
    return re.sub(r"\s+", " ", _tirnak(t)).strip().lower()


def anahtar_gevsek(t):
    """Bosluga BAGISIK anahtar. kelime_onar.py yalnizca bosluk oynattigi
    icin kapi bunu kullanir."""
    return re.sub(r"\s+", "", _tirnak(t)).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--out", default="data/korpus")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--parca", type=int, default=110,
                    help="alintinin karsilastirilacak ilk N karakteri")
    ap.add_argument("--esik-butunluk", type=float, default=0.98)
    ap.add_argument("--esik-atif", type=float, default=0.98)
    ap.add_argument("--esik-p6", type=float, default=0.95)
    ap.add_argument("--goster", type=int, default=12)
    # --rafine: RAFINE ayristiricilar (HANDOVER 4, Gorev 1).
    #   TBDY  -> bent_bol.py    (1208 -> 1523 birim, kutuk #2)
    #   diger -> maddeler2.py   (158 -> 232 birim, kutuk #1)
    # VARSAYILAN KAPALI ve bu BILINCLI: scripts/dogrula_linux.sh kabul kapisi
    # "1366 birim / Kontrol A 440-441" degerlerini SABIT tutuyor. Varsayilani
    # degistirmek 17/17 kapisini bozardi. Rafine korpus AYRI bir --out dizinine
    # uretilir; kapinin guncellenmesi ayri ve BEYAN EDILEN bir adimdir.
    # Ayristirici bazinda ayri: Gorev 1'in (maddeler2) katkisini bent_bol'un
    # TBDY bolmesinden IZOLE edebilmek icin. Kontrol A'nin dusmesi hangisinden
    # geliyor, ancak boyle olculur.
    ap.add_argument("--rafine", default="yok",
                    choices=["yok", "madde", "bent", "hepsi"],
                    help="yok=ham uretici · madde=maddeler2 (5 belge) · "
                         "bent=bent_bol (TBDY) · hepsi=ikisi")
    a = ap.parse_args()

    if a.rafine != "yok" and not _RAFINE_VAR:
        print(f"! --rafine={a.rafine} istendi ama rafine ediciler import edilemedi: {_RAFINE_HATA}")
        sys.exit(1)
    _AD = {"yok": "HAM uretici (rafine YOK)",
           "madde": "maddeler2 (5 belge) + HAM bentler (TBDY)",
           "bent": "HAM maddeler (5 belge) + bent_bol (TBDY)",
           "hepsi": "maddeler2 (5 belge) + bent_bol (TBDY)"}
    print(f"  ayristirici: {_AD[a.rafine]}")

    os.makedirs(a.out, exist_ok=True)

    # ------------------------------------------------------------ KORPUS
    korpus, manifest, belge_metin = {}, [], {}
    for kod, meta in UR.LAWS.items():
        yol = os.path.join(a.pdf_dir, meta["dosya"])
        if not os.path.exists(yol):
            print(f"! BULUNAMADI: {yol}")
            sys.exit(1)
        ham = open(yol, "rb").read()
        metin = UR.normalize(UR.pdf_metin(yol))
        belge_metin[kod] = metin
        if meta["tur"] == "tbdy":
            birimler = (_bent_bol(UR.bentler(metin), metin)
                        if a.rafine in ("bent", "hepsi") else UR.bentler(metin))
        else:
            birimler = (_maddeler2(metin)[0]
                        if a.rafine in ("madde", "hepsi") else UR.maddeler(metin))
        for no, d in birimler.items():
            korpus[(kod, str(no))] = {
                "kanun": kod, "belge_adi": meta["ad"], "birim": str(no),
                "tur": meta["tur"], "kabul_yili": meta["kabul"],
                "metin": d["metin"],
                "degisiklik_yillari": d.get("degisiklik_yillari", []),
            }
        manifest.append({
            "kanun": kod, "dosya": meta["dosya"],
            "pdf_sha256": hashlib.sha256(ham).hexdigest(),
            "metin_sha256": hashlib.sha256(metin.encode("utf-8")).hexdigest(),
            "karakter": len(metin), "birim_sayisi": len(birimler),
            "degisiklik_yili_olan_birim":
                sum(1 for d in birimler.values() if d.get("degisiklik_yillari")),
        })

    kj = os.path.join(a.out, "korpus.jsonl")
    with open(kj, "w", encoding="utf-8") as fh:
        for v in korpus.values():
            fh.write(json.dumps(v, ensure_ascii=False) + "\n")
    bj = os.path.join(a.out, "belge_tam.jsonl")
    with open(bj, "w", encoding="utf-8") as fh:
        for kod, m in belge_metin.items():
            fh.write(json.dumps({"kanun": kod, "metin": m}, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "belge_manifest.txt"), "w", encoding="utf-8-sig") as fh:
        fh.write("RUHSAT-Bench — donmus kaynak belge manifesti (denetim maddesi 1.18)\n\n")
        for m in manifest:
            for k, v in m.items():
                fh.write(f"{k}: {v}\n")
            fh.write("\n")

    print("=" * 84)
    print("KORPUS KURULDU")
    print("=" * 84)
    print(f"{'kanun':<10}{'birim':>7}{'degis.yili olan':>17}{'karakter':>11}  pdf sha256")
    for m in manifest:
        print(f"{m['kanun']:<10}{m['birim_sayisi']:>7}{m['degisiklik_yili_olan_birim']:>17}"
              f"{m['karakter']:>11}  {m['pdf_sha256'][:16]}...")
    print(f"\ntoplam birim: {len(korpus)}")

    # -------------------------------------------- BIRIM UZUNLUK DAGILIMI
    print("\n--- birim uzunlugu (karakter) — istem tasarimi icin ---")
    print(f"{'kanun':<10}{'medyan':>9}{'p90':>9}{'maks':>9}{'>3000':>8}")
    for kod in UR.LAWS:
        L = sorted(len(v["metin"]) for k, v in korpus.items() if k[0] == kod)
        if not L:
            continue
        p90 = L[int(0.9 * (len(L) - 1))]
        print(f"{kod:<10}{statistics.median(L):>9.0f}{p90:>9}{max(L):>9}"
              f"{sum(1 for x in L if x > 3000):>8}")

    # ------------------------------------------------------- KONTROLLER
    with open(a.claims, encoding="utf-8-sig") as fh:
        iddialar = list(csv.DictReader(fh))

    kat_birim = {k: anahtar_kati(v["metin"]) for k, v in korpus.items()}
    gev_birim = {k: anahtar_gevsek(v["metin"]) for k, v in korpus.items()}
    kat_belge = {k: anahtar_kati(v) for k, v in belge_metin.items()}
    gev_belge = {k: anahtar_gevsek(v) for k, v in belge_metin.items()}
    birim_ind = collections.defaultdict(list)
    for (kod, no) in korpus:
        birim_ind[kod].append(no)

    a_gev = collections.Counter(); a_kat = collections.Counter()
    a_top = collections.Counter(); tani = collections.Counter(); hatalar = []

    for x in iddialar:
        if x["probe"] in ("P3_anakronizm", "P4_uydurma"):
            continue                                   # alinti sentetik isaret
        kod, no = x["kanun"], str(x["madde"])
        pk = anahtar_kati(x["kaynak_alinti"])[:a.parca]
        pg = anahtar_gevsek(x["kaynak_alinti"])[:a.parca]
        if not pg:
            continue
        a_top[x["probe"]] += 1
        a_kat[x["probe"]] += bool(pk and pk in kat_birim.get((kod, no), ""))
        bulundu = pg in gev_birim.get((kod, no), "")
        a_gev[x["probe"]] += bulundu
        if bulundu:
            tani["dogru birimde"] += 1
            continue
        nerede = next((o for o in birim_ind[kod] if pg in gev_birim[(kod, o)]), None)
        if nerede is not None:
            tani[f"BASKA birimde"] += 1
            # BIRIM-ESNEK TANI (yalniz RAPORLANIR, kapiyi DEGISTIRMEZ).
            # bent_bol.py:238-240 kendi kuralini soyle ilan ediyor:
            #     taban = {no.split("~")[0] for no in yer}
            #     # "~2" ayni bendin IKINCI KOPYASIDIR, yanlis atif DEGILDIR.
            # Rafine korpusta alinti, CSV biriminin "~N kopyasi"na ya da ALT
            # birimine dusebilir; ikisi de birim siniri HATASI degildir.
            # Katı sayi oldugu gibi kalir (makale ona atif yapabilir); bu satir
            # yalnizca "dususun ne kadari gercek hata" sorusunu ayirmak icindir.
            tb_n, tb_c = str(nerede).split("~")[0], str(no).split("~")[0]
            if tb_n == tb_c:
                tani["  (esnek) ayni birim ~N kopyasi"] += 1
            elif tb_n.startswith(tb_c + "."):
                tani["  (esnek) CSV ust birimi, alinti alt birimde"] += 1
            elif tb_c.startswith(tb_n + "."):
                tani["  (esnek) CSV alt birimi, alinti ust birimde"] += 1
            else:
                tani["  (esnek) ILISKISIZ birim — gercek sinir hatasi"] += 1
            hatalar.append((x, f"BASKA birimde: {kod}/{nerede} (beklenen {no})"))
        elif pg in gev_belge.get(kod, ""):
            tani["belgede var, birime girmemis"] += 1
            hatalar.append((x, "belgede var ama hicbir birime girmemis"))
        else:
            tani["belgede hic yok"] += 1
            hatalar.append((x, "belgede HIC YOK"))

    b_ok = collections.Counter(); b_top = collections.Counter(); b_hata = []
    for x in iddialar:
        kanun, madde = atif(x["iddia"])
        b_top[x["probe"]] += 1
        var = (kanun in belge_metin) if madde is None else ((kanun, madde) in korpus)
        b_ok[x["probe"]] += var
        if not var:
            b_hata.append((x, kanun, madde))

    def tablo(baslik, ok, top, ikinci=None, ad2=""):
        print(f"\n{baslik}")
        basl = f"    {'prob':<18}{'gecen':>10}{'oran':>9}"
        if ikinci is not None:
            basl += f"{ad2:>12}"
        print(basl)
        t_ok = t_n = t2 = 0
        for p in sorted(top):
            s = f"    {p:<18}{f'{ok[p]}/{top[p]}':>10}{ok[p]/top[p]:>9.4f}"
            if ikinci is not None:
                s += f"{ikinci[p]/top[p]:>12.4f}"; t2 += ikinci[p]
            print(s)
            t_ok += ok[p]; t_n += top[p]
        s = f"    {'TOPLAM':<18}{f'{t_ok}/{t_n}':>10}{t_ok/t_n:>9.4f}"
        if ikinci is not None:
            s += f"{t2/t_n:>12.4f}"
        print(s)
        return t_ok / t_n

    print("\n" + "=" * 84)
    print("POZITIF KONTROLLER")
    print("=" * 84)
    oran_a = tablo(
        "A) KORPUS BUTUNLUGU — kaynak_alinti gercek kaynak biriminde bulunuyor mu"
        "\n   kapi = GEVSEK (bosluga bagisik). 'kati' yalnizca metin sadakati olcusudur;"
        "\n   kelime_onar.py 31 alintida kelime ici boslugu duzelttigi icin kati oran dusuktur.",
        a_gev, a_top, a_kat, "kati")
    print(f"\n    teshis: {dict(tani)}")

    oran_b = tablo("B) ATIF KARSILANABILIRLIGI — iddianin atif yaptigi birim korpusta var mi",
                   b_ok, b_top)

    # ------------------------------------------ KONTROL C — P6 DETERMINISTIK
    p6 = [x for x in iddialar if x["probe"] == "P6_guncellik"]
    c_ok = collections.Counter(); c_top = collections.Counter(); c_hata = []
    YIL = re.compile(r"(\d{4})\s*yılında değişiklik yapılmıştır")
    for x in p6:
        kanun, madde = atif(x["iddia"])
        yillar = korpus.get((kanun, madde), {}).get("degisiklik_yillari", None)
        m = YIL.search(x["iddia"])
        if yillar is None:
            karar = None
        elif m:
            karar = "DOGRU" if int(m.group(1)) in yillar else "YANLIS"
        else:                                          # "hic degistirilmemistir"
            karar = "DOGRU" if not yillar else "YANLIS"
        alt = x["uretim_sablonu"]
        c_top[alt] += 1
        c_ok[alt] += (karar == x["gold"])
        if karar != x["gold"]:
            c_hata.append((x, karar, yillar))

    print("\nC) P6 DETERMINISTIK COZULEBILIRLIK — LLM'siz kural, altina karsi")
    print("   DAIRESELLIK: korpus serhleri ile CSV notlari ayni regex'ten gelir;")
    print("   bu kontrol serhlerin HUKUKI dogrulugunu degil, bilgi kanalinin")
    print("   korpusta VAR oldugunu ve yeniden kurulumun ureticiyle uyustugunu gosterir.")
    print(f"    {'alt aile':<24}{'gecen':>10}{'oran':>9}")
    for alt in sorted(c_top):
        print(f"    {alt:<24}{f'{c_ok[alt]}/{c_top[alt]}':>10}{c_ok[alt]/c_top[alt]:>9.4f}")
    oran_c = sum(c_ok.values()) / sum(c_top.values())
    print(f"    {'TOPLAM':<24}{f'{sum(c_ok.values())}/{sum(c_top.values())}':>10}{oran_c:>9.4f}")
    print("    Kiyas: kapali kitapta P6 dengeli dogrulugu yerelde 0.380-0.570,")
    print("           Sonnet E2'de 0.508, ve Sonnet E1'de 60/60 yil maddesinde kacinma.")

    for x, n in hatalar[:a.goster]:
        print(f"\n  [A] id={x['id']} {x['kanun']}/{x['madde']} {x['uretim_sablonu']} -> {n}")
        print(f"      {x['kaynak_alinti'][:95]}")
    for x, k, m in b_hata[:5]:
        print(f"\n  [B] id={x['id']} {x['uretim_sablonu']} -> atif ({k}, {m}) korpusta yok")
    for x, karar, yillar in c_hata[:8]:
        print(f"\n  [C] id={x['id']} {x['uretim_sablonu']} altin={x['gold']} kural={karar}")
        print(f"      korpus yillari={yillar} | not={x['degisiklik_notu']}")
        print(f"      {x['iddia'][:95]}")

    print()
    durdu = False
    if oran_a < a.esik_butunluk:
        print(f"! korpus butunlugu {oran_a:.4f} < {a.esik_butunluk}")
        durdu = True
    if tani.get("BASKA birimde", 0):
        print(f"! {tani['BASKA birimde']} alinti BASKA birimde bulundu — birim siniri hatasi.")
        print("  Bu maddelerde dayanakli kol modele YANLIS maddeyi gosterir.")
        durdu = True
    if oran_b < a.esik_atif:
        print(f"! atif karsilanabilirligi {oran_b:.4f} < {a.esik_atif}")
        durdu = True
    if oran_c < a.esik_p6:
        print(f"! P6 deterministik oran {oran_c:.4f} < {a.esik_p6} — serh cikarimi ureticiyle uyusmuyor.")
        durdu = True
    if durdu:
        print("\n  Korpus dosyalari yazildi, ama yukaridakiler cozulmeden dayanakli kol kosulmaz.")
        sys.exit(2)

    print("UC KONTROL DE GECTI. Dayanakli kol icin korpus kullanilabilir.")
    print(f"  {kj}\n  {bj}\n  {os.path.join(a.out, 'belge_manifest.txt')}")


if __name__ == "__main__":
    main()
