# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — maddeler() RAFINE EDICISI (Ek / Gecici / Mukerrer maddeler)

SORUN (kusur kutugu #1, zemin olcumu sonuclar/gorev1_olcum_20260827.txt)
------------------------------------------------------------------------
uret_iddia_v3_6.py:96'daki bolme lookahead'inin basinda sinir yok:

    re.split(r"(?=(?:Madde|MADDE)\\s+\\d+\\s*[–\\-—])", t)

"Ek Madde 3 -" metninde lookahead "M" harfinde eslesir; bolme oradan yapilir,
"Ek " oneki ONCEKI parcada kalir, yeni parca "Madde 3 - ..." olarak okunur.
Sonra satir 101-102:

    if no in out:
        continue

3 zaten kayitli oldugu icin parca TAMAMEN ATILIR.

OLCULDU (5 belge, salt okuma):
    3194 37 parca / 50.144 kar · YDUY 18 / 11.300 · 6331 11 / 6.324
    4708  8 parca /  7.719 kar · ISGRISK 1 / 232
    TOPLAM 75 parca / 75.719 karakter
    onek dagilimi: Gecici 58 · Ek 16 · oneksiz 1

BU BETIK NE YAPAR
-----------------
maddeler() ciktisini ITHAL EDER ve BOZMADAN uzerine ekler (bent_bol.py deseni).
Ureteci KOPYALAMAZ; iddia metinleri ve id'ler mühürlüdür.

  * Mevcut birimler (int anahtarlar) AYNEN korunur — bayt-ayni, dogrulanir.
  * Dusen parcalar "Ek 3", "Gecici 5", "Mukerrer 7" gibi STRING anahtarlarla eklenir.
  * degisiklik_yillari MUHURLU KODLA hesaplanir: gövde sentetik bir
    "Madde 1 - <govde>" metnine sarilip UR.maddeler()'e verilir. Regex
    KOPYALANMAZ; ureticinin kendi mantigi calisir.

ANAHTAR BICIMI — NEDEN "~N" DEGIL
----------------------------------
bent_bol.py:109-111 cift anahtari "{anah}~{k}" ile saklar ve satir 238-240
atif cozerken tabana geri indirir:

    taban = {no.split("~")[0] for no in yer}
    # "~2" ayni bendin IKINCI KOPYASIDIR, yanlis atif DEGILDIR.

Yani "~N" semantigi: AYNI birimin ikinci gecisi. Gecici Madde 3, Madde 3'un
kopyasi DEGILDIR; yalnizca numarayi paylasan BASKA bir maddedir. "3~2"
kullanilirsa asagi akis bunu Madde 3 sanar ve R1/R2 "Madde 3" atfina
"Gecici Madde 3" metnini dondurebilir. Bu yuzden ayrim TASIYAN anahtar
kullanilir. Bicim kullanici karari: "Ek 3" / "Gecici 5" (okunabilir).

"~N" yine de kullanilir — ama YALNIZCA ayni turden ikinci gecis icin
(iki kez gecen "Ek Madde 3" gibi). Orada semantik dogrudur.

SINIR VAKA — OTOMATIK COZULMEZ (kusur kutugu #22)
--------------------------------------------------
Dusen 75 parcanin 1'inin oneki YOKTUR: 4708 "Madde 7". Bu, 4708'in kendi
maddesi DEGILDIR; 4708, 3458 sayili Muhendislik ve Mimarlik Hakkinda
Kanun'un 7. maddesini degistiriyor ve degistirilen metni ALINTILIYOR.
4708 birimi olarak eklenirse F5 getirimi BASKA BIR KANUNUN metnini 4708
diye dondurur. Bu yuzden EKLENMEZ; needs_human_review olarak raporlanir
(CLAUDE.md: borderline vakalar otomatik cozulmez).

KIRPMA (kusur kutugu #21) — BILINCLI OLARAK DOKUNULMUYOR
---------------------------------------------------------
maddeler() govdeyi [:4000] ile kirpiyor; 158 birimin 21'i kirpik,
71.748 karakter korpusta yok. Kabul kriteri "mevcut 158 birimin metni
bayt-ayni" oldugu icin bu pass'te duzeltilemez. Yeni birimler de AYNI
4000 sinirini kullanir — tutarlilik icin.

KOSU (bash)
-----------
    cd ~/Desktop/ruhsat-bench
    .venv/bin/python -u scripts/maddeler2.py --pdf-dir data/kaynak_pdf \\
        --rapor sonuclar/maddeler2_raporu.txt

    # kontrolun hatayi yakaladigini goster (pozitif kontrol):
    .venv/bin/python -u scripts/maddeler2.py --pdf-dir data/kaynak_pdf --oz-test
"""
import argparse
import os
import re
import sys

# ORTAM.md 2.2: betik basinda stdout/stderr UTF-8 reconfigure.
# Linux'ta zararsiz; dosya Windows'a donerse cp1252 borulama cokmesini onler.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import uret_iddia_v3_6 as UR          # MUHURLU — okunur, degistirilmez
except ImportError as exc:                # pragma: no cover
    print(f"! import hatasi: {exc}")
    sys.exit(1)

# uret_iddia_v3_6.py:96-97 ile AYNI kaliplar. Kopya degil, ayni metni ayni
# sekilde bolebilmek icin zorunlu; ureticinin ciktisiyla hizalanmazsa
# "dusen parca" tespiti anlamsiz olur.
BOL = re.compile(r"(?=(?:Madde|MADDE)\s+\d+\s*[–\-—])")
ESLE = re.compile(r"(?:Madde|MADDE)\s+(\d+)\s*[–\-—]\s*(.*)", re.S)

# Onek, dusen parcanin ONCESINDEKI parcanin SONUNDA kalir (bolme "M" harfinden
# yapildigi icin). Buyuk/kucuk harfli yazimlarin hepsi mevzuatta geciyor.
ONEK = re.compile(r"(Ek|EK|Geçici|GEÇİCİ|Mükerrer|MÜKERRER)\s*$")
# TUZAK (bu betigin oz-testi yakaladi): .lower() Turkce noktali I'yi BOZAR.
#   "GEÇİCİ".lower() -> 'geçi̇ci̇'   (İ -> i + U+0307 birlesen nokta)
# Bu yuzden buyuk/kucuk donusumu YOK; eslesen dizgi HARF BIREBIR haritalanir.
ONEK_ADI = {"Ek": "Ek", "EK": "Ek",
            "Geçici": "Geçici", "GEÇİCİ": "Geçici",
            "Mükerrer": "Mükerrer", "MÜKERRER": "Mükerrer"}

KIRPMA = 4000          # uret_iddia_v3_6.py:104 ile AYNI (kutuk #21: dokunulmuyor)


def _yillar(govde):
    """degisiklik_yillari'ni MUHURLU KODLA hesapla.

    Regex kopyalamak yerine govdeyi sentetik bir maddeye sarip UR.maddeler()'e
    veriyoruz; boylece ureticinin kendi mantigi calisir ve surum kaymasi olmaz.
    Govde icinde "Madde N -" gecerse sentetik metin birden fazla parcaya
    bolunur; yillar TUM parcalarin BIRLESIMIDIR (regex zaten parca parca
    uygulanir, parcalar da govdeyi bolusur).
    """
    d = UR.maddeler("Madde 1 – " + govde)
    yil = set()
    for v in d.values():
        yil.update(v.get("degisiklik_yillari", []))
    return sorted(yil), len(d)


def maddeler2(t):
    """maddeler() + dusen Ek/Gecici/Mukerrer maddeler.

    Doner: (birimler, rapor)
      birimler : maddeler()'in dondurdugu int anahtarlar AYNEN + yeni str anahtarlar
      rapor    : {'eklenen': [...], 'insan_incelemesi': [...], 'coklu_parca': n}
    """
    taban = UR.maddeler(t)
    out = dict(taban)                     # deger nesneleri PAYLASILIR, mutasyon YOK
    eklenen, insan, coklu = [], [], 0

    parcalar = BOL.split(t)
    gorulen = set()
    for i, p in enumerate(parcalar):
        m = ESLE.match(p)
        if not m:
            continue
        no, govde = int(m.group(1)), m.group(2).strip()
        if no not in gorulen:
            gorulen.add(no)               # bu parcayi taban zaten aldi
            continue

        onceki = parcalar[i - 1].rstrip() if i else ""
        mo = ONEK.search(onceki)
        if not mo:
            # ONEKSIZ dusen parca: numarayi paylasan ama Ek/Gecici OLMAYAN metin.
            # Olculdu: tek vaka 4708 "Madde 7" = 3458 sayili Kanun'dan ALINTI.
            # Otomatik cozulmez (CLAUDE.md); eklenmez, raporlanir.
            insan.append({
                "no": no, "uzunluk": len(govde),
                "onceki_son": onceki[-160:],
                "govde_bas": govde[:160],
                "sebep": "onek yok — numarayi paylasan farkli metin; "
                         "alintilanan baska kanun olabilir",
            })
            continue

        tur = ONEK_ADI[mo.group(1)]
        anah = f"{tur} {no}"
        if anah in out:
            # AYNI turden ikinci gecis. Burada "~N" semantigi DOGRUDUR:
            # gercekten ayni birimin ikinci kopyasi.
            k = 2
            while f"{anah}~{k}" in out:
                k += 1
            anah = f"{anah}~{k}"

        yillar, n_parca = _yillar(govde)
        if n_parca > 1:
            coklu += 1
        out[anah] = {"metin": govde[:KIRPMA], "degisiklik_yillari": yillar}
        eklenen.append({"anahtar": anah, "uzunluk": len(govde),
                        "kirpildi": len(govde) > KIRPMA})

    return out, {"eklenen": eklenen, "insan_incelemesi": insan, "coklu_parca": coklu}


# ----------------------------------------------------------------- DOGRULAMA
def _bayt_ayni(taban, yeni):
    """Mevcut birimlerin metni DEGISMEDI mi? Kabul kriteri: bayt-ayni."""
    bozuk = []
    for no, d in taban.items():
        y = yeni.get(no)
        if y is None:
            bozuk.append((no, "KAYIP"))
        elif y["metin"] != d["metin"]:
            bozuk.append((no, "METIN DEGISTI"))
        elif y.get("degisiklik_yillari") != d.get("degisiklik_yillari"):
            bozuk.append((no, "YIL DEGISTI"))
    return bozuk


def _oz_test(pdfdir):
    """POZITIF KONTROL: kontrollerin hatayi GERCEKTEN yakaladigini goster.

    Proje kurali (ORTAM.md 7): her yeni kontrol icin pozitif kontrol iste.
    Burada bayt-aynilik kontrolune bilerek bozuk bir girdi verilir; kontrol
    yakalamazsa betik HATA verir.
    """
    print("== POZITIF KONTROL ==")
    kod, meta = "6331", UR.LAWS["6331"]
    t = UR.normalize(UR.pdf_metin(os.path.join(pdfdir, meta["dosya"])))
    taban = UR.maddeler(t)
    yeni, _ = maddeler2(t)

    gecti = 0
    # 1) saglam durumda bozukluk BULUNMAMALI
    b = _bayt_ayni(taban, yeni)
    print(f"  [1] saglam girdi        -> bozuk {len(b)}  ({'TAMAM' if not b else 'HATA'})")
    gecti += not b

    # 2) metni bilerek boz -> kontrol YAKALAMALI
    bozuk = {k: dict(v) for k, v in yeni.items()}
    ilk = sorted(k for k in bozuk if isinstance(k, int))[0]
    bozuk[ilk]["metin"] = bozuk[ilk]["metin"] + " BOZULDU"
    b2 = _bayt_ayni(taban, bozuk)
    yakaladi = any(x[0] == ilk and x[1] == "METIN DEGISTI" for x in b2)
    print(f"  [2] metin bozuldu       -> yakalandi {yakaladi}  ({'TAMAM' if yakaladi else 'HATA'})")
    gecti += yakaladi

    # 3) birim sil -> kontrol YAKALAMALI
    eksik = {k: v for k, v in yeni.items() if k != ilk}
    b3 = _bayt_ayni(taban, eksik)
    yakaladi3 = any(x[0] == ilk and x[1] == "KAYIP" for x in b3)
    print(f"  [3] birim silindi       -> yakalandi {yakaladi3}  ({'TAMAM' if yakaladi3 else 'HATA'})")
    gecti += yakaladi3

    # 4) yeni birim GERCEKTEN eklendi mi
    yeniler = [k for k in yeni if isinstance(k, str)]
    var = len(yeniler) > 0
    print(f"  [4] yeni birim eklendi  -> {len(yeniler)} adet  ({'TAMAM' if var else 'HATA'})")
    gecti += var

    # 5) yeni anahtar mevcutlarla CAKISMIYOR
    cakisma = [k for k in yeniler if k in {str(x) for x in taban}]
    print(f"  [5] anahtar cakismasi   -> {len(cakisma)}  ({'TAMAM' if not cakisma else 'HATA'})")
    gecti += not cakisma

    print(f"\n  oz-test: {gecti}/5")
    return 0 if gecti == 5 else 1


def main():
    ap = argparse.ArgumentParser(description="maddeler() rafine edicisi (Ek/Gecici maddeler)")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--rapor", default="")
    ap.add_argument("--oz-test", action="store_true", help="pozitif kontrolleri kosur")
    a = ap.parse_args()

    if a.oz_test:
        sys.exit(_oz_test(a.pdf_dir))

    satirlar = []
    P = lambda s="": (print(s), satirlar.append(s))       # noqa: E731

    P("RUHSAT-Bench — maddeler2 DOGRULAMA")
    P(f"kirpma siniri : {KIRPMA} (uret_iddia_v3_6.py:104 ile ayni; kutuk #21 dokunulmadi)")
    P("")
    P(f"{'belge':<10}{'taban':>7}{'eklenen':>9}{'yeni_top':>10}{'insan':>7}{'kurtarilan_kar':>16}")
    P("-" * 59)

    t_taban = t_ek = t_ins = t_kar = 0
    tum_insan, tum_eklenen = [], []
    for kod, meta in UR.LAWS.items():
        if meta["tur"] == "tbdy":
            P(f"{kod:<10}{'—':>7}{'—':>9}{'—':>10}{'—':>7}{'(bent_bol.py isler)':>16}")
            continue
        yol = os.path.join(a.pdf_dir, meta["dosya"])
        if not os.path.exists(yol):
            P(f"! BULUNAMADI: {yol}")
            sys.exit(1)
        t = UR.normalize(UR.pdf_metin(yol))
        taban = UR.maddeler(t)
        yeni, rap = maddeler2(t)

        bozuk = _bayt_ayni(taban, yeni)
        if bozuk:
            P(f"! {kod}: BAYT-AYNILIK BOZULDU -> {bozuk[:5]}")
            sys.exit(1)

        kar = sum(e["uzunluk"] for e in rap["eklenen"])
        P(f"{kod:<10}{len(taban):>7}{len(rap['eklenen']):>9}{len(yeni):>10}"
          f"{len(rap['insan_incelemesi']):>7}{kar:>16}")
        t_taban += len(taban); t_ek += len(rap["eklenen"])
        t_ins += len(rap["insan_incelemesi"]); t_kar += kar
        for e in rap["insan_incelemesi"]:
            e["kanun"] = kod
        tum_insan += rap["insan_incelemesi"]
        for e in rap["eklenen"]:
            e["kanun"] = kod
        tum_eklenen += rap["eklenen"]

    P("-" * 59)
    P(f"{'TOPLAM':<10}{t_taban:>7}{t_ek:>9}{t_taban + t_ek:>10}{t_ins:>7}{t_kar:>16}")
    P("")
    P(f"  bayt-aynilik: {t_taban}/{t_taban} mevcut birim DEGISMEDI")
    P(f"  kurtarma    : {t_ek}/{t_ek + t_ins} dusen parca eklendi "
      f"({t_ek / (t_ek + t_ins):.4f})")
    P("")

    tur = {}
    for e in tum_eklenen:
        tur[e["anahtar"].split()[0]] = tur.get(e["anahtar"].split()[0], 0) + 1
    P(f"  tur dagilimi: {tur}")
    kirp = sum(1 for e in tum_eklenen if e["kirpildi"])
    P(f"  yeni birimlerden kirpilan: {kirp} (kutuk #21 ile ayni sinir)")
    P("")

    P("=== needs_human_review — OTOMATIK COZULMEDI ===")
    if not tum_insan:
        P("  (yok)")
    for e in tum_insan:
        P(f"  {e['kanun']} / Madde {e['no']}  ({e['uzunluk']} kar)")
        P(f"    sebep      : {e['sebep']}")
        P(f"    onceki son : ...{e['onceki_son']}")
        P(f"    govde bas  : {e['govde_bas']}...")
    P("")
    P("  Bu parcalar korpusa EKLENMEDI. Tarihciler karar verecek.")

    if a.rapor:
        os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
        with open(a.rapor, "w", encoding="utf-8-sig") as fh:
            fh.write("\n".join(satirlar) + "\n")
        print(f"\nrapor: {a.rapor}")


if __name__ == "__main__":
    main()
