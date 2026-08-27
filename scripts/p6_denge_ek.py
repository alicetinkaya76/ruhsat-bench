# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — P6 2x2 DENGELEME (uretici YENIDEN CALISTIRILMAZ, id 1-486 korunur).

SORUN
-----
Uretecte P6 iki kalipla uretiliyor ve her kalip tek bir altin etikete bagli:

    "... N. maddesinde YYYY yilinda degisiklik yapilmistir."      -> hep DOGRU
    "... N. maddesi, ... bu yana hic degistirilmemistir."          -> hep YANLIS

Yani P6'da etiket cumle kalibindan okunabilir. 2x2'nin iki hucresi bos:

                          DOGRU        YANLIS
    "degisiklik yapildi"    68            0     <- bos
    "hic degismedi"          0           51     <- bos

Bu betik eksik iki hucreyi uretir:

  [H1] YANLIS YILLI "degisiklik yapilmistir"  -> gold = YANLIS
       Maddenin GERCEK degisiklik yillarinin HICBIRINE esit olmayan,
       kanunun kabul yili ile bugun arasinda bir yil secilir. EK KORUMA:
       secilen yil, madde blogunda 4 haneli bir sayi olarak HIC GECMEMELI.
       Gerekce olculmustur: iz taramasi, uretecin yil regex'inin bazi
       maddelerde kunyeyi kacirdigini gosterdi; kacirilan gercek bir
       degisiklik yilini "yanlis yil" diye secmek altin hatasi uretirdi.

  ORTAK SART (v2): madde blogu maddeler() tarafindan KESILMEMIS olmali
       (len < 4000). Kesilmis blokta hem yil listesi hem iz taramasi eksik
       calisir; iki hucre icin de guvenilmez.

  [H2] GERCEKTEN DEGISMEMIS madde icin "hic degistirilmemistir" -> gold = DOGRU
       Uc sart birden: (a) maddeler() bos degisiklik listesi dondurmus,
       (b) madde blogunda hicbir degisiklik izi yok, (c) BELGENIN KENDISI
       konsolide bir metin (en az bir degisiklik kunyesi tasiyor).

       (c) SARTI NEDEN VAR: ISGRISK PDF'inde belge genelinde SIFIR kunye var
       ve metin madde 19'da, konsolide metinlerin tasidigi "Yonetmeligin
       Yayimlandigi Resmi Gazete / Degisiklik Yapan Yonetmelikler" tablosu
       olmadan bitiyor. Yani o PDF konsolide degil; yonetmeligin degisip
       degismedigi hakkinda HICBIR SEY soylemiyor. Oradan uretilecek
       "hic degistirilmemistir DOGRU" iddiasinin altini kanitsizdir.

[H2] ICIN POZITIF KONTROLLU SUZGEC (kritik)
-------------------------------------------
uret_iddia_v3_6.maddeler() degisiklik yilini su desenle ariyor:

    \\((?:Değişik|Ek|Yeniden düzenleme)[^)]{0,80}?(\\d{1,2}/\\d{1,2}/(\\d{4}))[^)]*\\)

Bu desen "(Başlığı ile Birlikte Değişik:RG-29/12/2018-30640)" ile ESLESMEZ
(parantezden hemen sonra "Başlığı" geliyor) ve "(Mülga: ...)" ile de
eslesmez. Yani BOS degisiklik listesi "degismemis" anlamina GELMEYEBILIR;
"parser yakalayamadi" da olabilir. [H2]'yi bu haliyle uretmek ALTIN HATASI
uretir.

Onlem: bos listeli her madde blogu ayrica IZ TARAMASINDAN gecirilir
(Değişik / Ek: / Ek fıkra / Mülga / Yeniden düzenleme / RG- / md.). Iz
bulunursa madde [H2] icin KULLANILMAZ.

Pozitif kontrol: ayni iz taramasi, degisiklik yili KAYITLI maddelerde de
calistirilir. Orada isabet orani ~%100 cikmalidir; cikmazsa tarama
arizalidir ve betik [H2] uretmeden durur.

CIKTI
-----
Yeni satirlar id 501'den baslar; 1-486 araligina DOKUNULMAZ, dolayisiyla
mevcut konsensus kosusu gecerliligini korur. Yeni satirlarda
durum = YENI_EK (uzman denetiminde ek ornek cekilebilsin diye).

Varsayilan hedef: her hucre --hedef-hucre kadar, yani P6 toplam butcesi
degismeden (4 x 30 = 120 ~ mevcut 119) kompozisyon dengelenir. Mevcut
P6 satirlari hedefe gore ASAGI ORNEKLENIR; atilanlar dosyadan cikarilir
ama id'leri korunur (baska bir dosyada durmaya devam eder).

Kullanim:
    python scripts/p6_denge_ek.py --kuru
    python scripts/p6_denge_ek.py --hedef-hucre 30
"""
import argparse
import csv
import os
import random
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uret_iddia_v3_6 import LAWS, maddeler, normalize, pdf_metin  # noqa: E402

IZ = re.compile(r"Değişik|Ek\s*:|Ek\s+fıkra|Mülga|Yeniden düzenleme|RG-|\bmd\.\)")
DORT_HANE = re.compile(r"\b(\d{4})\b")
BU_YIL = 2026
# maddeler() her madde blogunu govde[:4000] ile KESIYOR. Kesilen kismin
# icindeki bir degisiklik kunyesi ne yil listesine ne de iz taramasina girer;
# o madde yanlislikla "hic degismemis" sayilabilir ya da eksik yil listesi
# yuzunden "yanlis yil" olarak gercek bir degisiklik yili secilebilir.
# Olculdu: 2 madde bu durumda. Kesilmis bloklar iki hucreden de dislanir.
BLOK_KESIK = 4000
# Belge duzeyinde konsolidasyon esigi: mevzuat.gov.tr konsolide metinleri
# degisiklik kunyelerini metne isler. Hic kunye tasimayan bir belge ya hic
# degismemistir ya da KONSOLIDE DEGILDIR; ikisi ayirt edilemez. Boyle bir
# belgeden "hic degistirilmemistir" (gold=DOGRU) iddiasi URETILEMEZ.
BELGE_IZ_ESIGI = 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v4_temiz.csv")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--out", default="data/iddialar/uretilen_iddialar_v5_p6dengeli.csv")
    ap.add_argument("--rapor", default="sonuclar/p6_denge_raporu.txt")
    ap.add_argument("--hedef-hucre", type=int, default=30)
    ap.add_argument("--ilk-id", type=int, default=501)
    ap.add_argument("--tohum", type=int, default=20260728)
    ap.add_argument("--kuru", action="store_true")
    a = ap.parse_args()

    rnd = random.Random(a.tohum)
    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))
        alanlar = list(satirlar[0].keys())

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — P6 2x2 DENGELEME")
    e("=" * 78)
    e(f"girdi: {a.csv}  ({len(satirlar)} iddia)")

    mevcut = defaultdict(list)
    for s in satirlar:
        if s.get("probe") == "P6_guncellik":
            mevcut[s.get("probe_alt", "")].append(s)
    e(f"mevcut P6: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(mevcut.items())))

    # ---------------------------------------------------------------- [1]
    e()
    e("[1] KAYNAK TARAMASI")
    bloklar, belge_iz = {}, {}
    for kod, meta in LAWS.items():
        if meta["tur"] == "tbdy":
            continue
        yol = os.path.join(a.pdf_dir, meta["dosya"])
        if not os.path.exists(yol):
            e(f"  ! {yol} yok, atlaniyor")
            continue
        ham = normalize(pdf_metin(yol))
        bloklar[kod] = maddeler(ham)
        belge_iz[kod] = len(IZ.findall(ham))
        yil_var = sum(1 for m in bloklar[kod].values() if m["degisiklik_yillari"])
        uygun = "konsolide" if belge_iz[kod] >= BELGE_IZ_ESIGI else "KONSOLIDE DEGIL"
        e(f"  {kod:<9} {len(bloklar[kod]):>4} madde | yil kayitli {yil_var:>4} | "
          f"belge kunyesi {belge_iz[kod]:>4} | {uygun}")

    # ---------------------------------------------------------------- [2]
    e()
    e("[2] IZ TARAMASI — POZITIF KONTROL")
    e("  Kontrol: yil KAYITLI maddelerde iz bulunmali (beklenti ~%100).")
    poz_n = poz_iz = 0
    for kod, mds in bloklar.items():
        for no, md in mds.items():
            if md["degisiklik_yillari"]:
                poz_n += 1
                poz_iz += bool(IZ.search(md["metin"]))
    oran = poz_iz / poz_n if poz_n else 0.0
    e(f"  yil kayitli madde: {poz_n} | iz bulunan: {poz_iz}  (%{100*oran:.1f})")
    disi = [k for k, v in belge_iz.items() if v < BELGE_IZ_ESIGI]
    if disi:
        e(f"  ! [H2] DISI BIRAKILAN BELGE: {', '.join(disi)}")
        e("    Belge genelinde tek bir degisiklik kunyesi yok -> konsolide metin")
        e("    degil. 'Hic degistirilmemistir' iddiasinin altini bu belgeyle")
        e("    kanitlanamaz. Bu belgelerden [H2] URETILMIYOR.")
    if oran < 0.95:
        e("  ! IZ TARAMASI ARIZALI (<%95). [H2] uretilmiyor, cikiliyor.")
        _yaz_rapor(a, L)
        return
    e("  => tarama saglam.")

    # ---------------------------------------------------------------- [3]
    e()
    e("[3] ADAY URETIMI")
    h1, h2, iz_yakalanan, h1_yil_yok, h2_belge_disi, kesik = [], [], 0, 0, 0, 0
    for kod, mds in bloklar.items():
        meta = LAWS[kod]
        for no, md in sorted(mds.items()):
            yillar = set(md["degisiklik_yillari"])
            if len(md["metin"]) >= BLOK_KESIK:
                kesik += 1
                continue
            blok_sayilari = {int(x) for x in DORT_HANE.findall(md["metin"])}
            if yillar:
                aday = [y for y in range(meta["kabul"] + 1, BU_YIL + 1)
                        if y not in yillar and y not in blok_sayilari]
                if not aday:
                    h1_yil_yok += 1
                    continue
                yil = rnd.choice(aday)
                h1.append({
                    "kanun": kod, "madde": no, "probe": "P6_guncellik",
                    "iddia": f"{meta['kisa']}{meta['iyelik']} {no}. maddesinde "
                             f"{yil} yılında değişiklik yapılmıştır.",
                    "gold": "YANLIS", "kaynak_alinti": md["metin"][:220],
                    "degisiklik_notu": f"gerçek: {sorted(yillar)} | iddia: {yil}",
                    "uretim_sablonu": "P6_yil_yanlis", "durum": "YENI_EK",
                    "probe_alt": "P6_yil_yanlis"})
            else:
                if belge_iz.get(kod, 0) < BELGE_IZ_ESIGI:
                    h2_belge_disi += 1
                    continue
                if IZ.search(md["metin"]):
                    iz_yakalanan += 1
                    continue
                h2.append({
                    "kanun": kod, "madde": no, "probe": "P6_guncellik",
                    "iddia": f"{meta['kisa']}{meta['iyelik']} {no}. maddesi, ilk yayımlandığı "
                             f"{meta['kabul']} yılından bu yana hiç değiştirilmemiştir.",
                    "gold": "DOGRU", "kaynak_alinti": md["metin"][:220],
                    "degisiklik_notu": "değişiklik izi bulunamadı",
                    "uretim_sablonu": "P6_degismedi_dogru", "durum": "YENI_EK",
                    "probe_alt": "P6_degismedi_dogru"})
    e(f"  [H1] yanlis yilli 'degisiklik yapilmistir' (gold=YANLIS) aday: {len(h1)}")
    e(f"  [H2] gercekten degismemis 'hic degistirilmemistir' (gold=DOGRU) aday: {len(h2)}")
    e(f"  kesilmis blok ({BLOK_KESIK}+ karakter) yuzunden elenen madde: {kesik}")
    e(f"  [H1] uygun yil bulunamadigi icin elenen madde: {h1_yil_yok}")
    e(f"  [H2] iz taramasinin ELEDIGI madde: {iz_yakalanan}")
    e(f"  [H2] konsolide olmayan belge yuzunden elenen madde: {h2_belge_disi}")
    e("  Not: elenen bu maddeler, uretecin yil regex'inin kacirdigi degisiklik")
    e("  bicimleridir ('(Başlığı ile ... Değişik:...)', '(Mülga:...)'). v3.7")
    e("  ureteci yazilirken regex bunlari da kapsamali.")

    # ---------------------------------------------------------------- [4]
    hedef = a.hedef_hucre
    e()
    e("[4] HEDEF 2x2")
    if len(h1) < hedef or len(h2) < hedef:
        e(f"  ! aday yetersiz (hedef {hedef}); ulasilabilen: "
          f"H1={min(len(h1), hedef)}, H2={min(len(h2), hedef)}")
        hedef = min(hedef, len(h1), len(h2))
        e(f"  hedef {hedef}'e dusuruldu (dort hucre esit tutuluyor).")
    rnd.shuffle(h1)
    rnd.shuffle(h2)
    sec_h1, sec_h2 = h1[:hedef], h2[:hedef]
    sec_yil = rnd.sample(mevcut.get("P6_yil", []), min(hedef, len(mevcut.get("P6_yil", []))))
    sec_deg = rnd.sample(mevcut.get("P6_degismedi", []),
                         min(hedef, len(mevcut.get("P6_degismedi", []))))

    e(f"    {'kalip':<28} {'DOGRU':>7} {'YANLIS':>7}")
    e(f"    {'degisiklik yapilmistir':<28} {len(sec_yil):>7} {len(sec_h1):>7}")
    e(f"    {'hic degistirilmemistir':<28} {len(sec_h2):>7} {len(sec_deg):>7}")
    e("  Kalip artik etiketi belirlemiyor: her iki kalipta da iki sinif var.")

    # ---------------------------------------------------------------- [5]
    yeni = []
    for i, k in enumerate(sec_h1 + sec_h2, a.ilk_id):
        k["id"] = str(i)
        yeni.append(k)
    tut = {s["id"] for s in sec_yil + sec_deg}
    cikti = [s for s in satirlar
             if s.get("probe") != "P6_guncellik" or s["id"] in tut] + yeni

    e()
    e("[5] YENI KUME")
    e(f"  {len(satirlar)} -> {len(cikti)} iddia "
      f"(P6 disi {len(cikti)-4*hedef}, P6 {4*hedef})")
    g = Counter(s["gold"] for s in cikti)
    e(f"  gold: DOGRU {g['DOGRU']} / YANLIS {g['YANLIS']}  "
      f"(%{100*g['DOGRU']/len(cikti):.1f} / %{100*g['YANLIS']/len(cikti):.1f})")
    e(f"  P6 payi: %{100*4*hedef/len(cikti):.1f}")
    e(f"  yeni id araligi: {a.ilk_id}-{a.ilk_id+len(yeni)-1}  (1-486 DOKUNULMADI)")
    e()
    e("  ornek [H1]: " + " ".join(sec_h1[0]["iddia"].split())[:100] if sec_h1 else "")
    e("       not  : " + sec_h1[0]["degisiklik_notu"] if sec_h1 else "")
    e("  ornek [H2]: " + " ".join(sec_h2[0]["iddia"].split())[:100] if sec_h2 else "")

    if a.kuru:
        e()
        e("  (--kuru) dosya yazilmadi.")
    else:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=alanlar)
            w.writeheader()
            w.writerows(cikti)
        print(f"\nyazildi: {a.out}  ({len(cikti)} iddia)")

    _yaz_rapor(a, L)


def _yaz_rapor(a, L):
    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.rapor}")


if __name__ == "__main__":
    main()
