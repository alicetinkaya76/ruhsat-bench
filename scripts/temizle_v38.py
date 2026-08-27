# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — CERRAHI TEMIZLIK v3.8 (uretici YENIDEN CALISTIRILMAZ).

v3.7'YE GORE NE DEGISTI VE NEDEN
--------------------------------
v3.7'de R2 ve R3 kurallari hem kaynak_alinti hem de IDDIA metni uzerinde
calisiyordu:

    ("R2_capraz_kanun_atfi", lambda a, i: KANUN_ATIF.search(a) or KANUN_ATIF.search(i))

Ama iddia metni, ureticinin KALIP CERCEVESINI icerir:
    "3194 sayılı Kanun'un 23. maddesine göre ..."
    "6331 sayılı Kanun'a göre ..."
Yani numarayla anilan her belgeden (3194 / 4708 / 6331) turetilmis hemen her
iddia, tasarim geregi "NNNN sayılı" dizesini tasir. R2 bunlarin hepsine
takildi. Dahasi bozuk_cumle sozlugu kaynak_alinti ile ANAHTARLANDIGI icin,
tek bir kardesin cercevesi kurala takildiginda ayni cumleden turetilmis butun
kardesler birlikte dusuyordu (yayilma etkisi).

Sonuc: 486 -> 239 (-%50.8). Beklenti ~478 idi. Kaybin buyuk kismi metin
kalitesi degil CERCEVE kaynakliydi ve secici bir kayipti: numarayla anilan
belgeler (3194/4708/6331) neredeyse tamamen silinirken basligiyla anilan
belgeler (TBDY/YDUY/ISGRISK) ayakta kaldi. Yani temiz kume KAYNAK BELGE ile
karisti; uzerinde yapilacak model karsilastirmasi prob degil belge olcerdi.

v3.8 duzeltmesi:
  * R1-R5 YALNIZCA kaynak_alinti uzerinde calisir (v3.7 dokumanin kendi
    tarif ettigi davranis buydu; kod dokumanla celisiyordu).
  * Iddia tarafindaki "NNNN sayılı" isabetleri ATILMAZ, yalnizca RAPORLANIR
    ve cerceve-kaynakli olup olmadigi ayristirilir.
  * Bos kaynak_alinti artik ortak anahtar degildir (id bazinda ayrilir);
    v3.7'de bos alintili satirlarin hepsi tek bir kova olarak birlikte
    dusebiliyordu.
  * R6 (TANI AMACLI, ATMAZ): kaynak_alinti icinde coklu bosluk. Ureticideki
    cumleler() "(Değişik:...)" etiketlerini tek bosluga cevirdigi icin
    etiketin sokuldugu yer cumlede 2+ bosluk olarak kaliyor. Bu, [B2]'deki
    0.44-0.50 kapsanma imzasinin kaynagidir. R1 ile birlikte gorulurse
    gercek kusur (iki fikra yapismis), tek basina gorulurse zararsiz artik.
  * POZITIF/NEGATIF KONTROL: betik, dusmesi gereken bilinen id'leri ve
    yasamasi gereken id'leri kendisi sinar ve sonucu basar. Pozitif kontrol
    duserse dosya YAZILMAZ.
  * Kaynak belge kirilimi once/sonra raporlanir (karisim testi).
  * v3.7 ciktisi varsa fark alinir: hangi id'ler geri geliyor.

Cikti dosyasi v2'yi EZMEZ; ayri isimle yazilir (uretilen_iddialar_v3_temiz.csv).

Kullanim:
    python scripts/temizle_v38.py --kuru
    python scripts/temizle_v38.py
"""
import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# Kurallar — HEPSI YALNIZCA kaynak_alinti uzerinde calisir.
# --------------------------------------------------------------------------
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
    ("R1_fikra_ici_parcalanma", lambda a: bool(FIKRA_ICI.search(a))),
    ("R2_capraz_kanun_atfi",    lambda a: bool(KANUN_ATIF.search(a))),
    ("R3_bolum_basligi",        lambda a: bool(BOLUM.search(a))),
    ("R4_bolunmus_ek",          lambda a: bool(EK_PARCA.search(a))),
    ("R5_caps_basligi",         lambda a: bool(CAPS.match(a))),
]

# R6: tani amacli, ATMAZ. Ham (daraltilmamis) alinti uzerinde bakilir.
BOSLUK_IZI = re.compile(r"\S\s{2,}\S")

VARYANT = re.compile(r"(P5_maddeshift|P5_lawshuffle|P2_swap|P1_\w+|P3_\w+|P4_\w+|P6_\w+)")

# --------------------------------------------------------------------------
# Kontroller
# --------------------------------------------------------------------------
# Pozitif kontrol: bunlarin DUSMESI zorunlu (gerekce kaynak_dogrula_v2 + [B2]).
#   378 -> alintida "2960 Sayılı" + "ALTINCI BÖLÜM"  (R2 ve R3)
#   134,202,254,255,272,282 -> alinti ortasinda "(4)" fikra isareti (R1)
POZITIF_KONTROL = {
    "378": "alintida 2960 Sayılı / ALTINCI BÖLÜM",
    "134": "alinti ortasinda (4)",
    "202": "alinti ortasinda (4)",
    "254": "alinti ortasinda (4)",
    "255": "alinti ortasinda (4)",
    "272": "alinti ortasinda (4)",
    "282": "alinti ortasinda (4)",
}
# Negatif kontrol: bunlarin YASAMASI beklenir (v3.7'de yalnizca cerceve
# yuzunden dusmuslerdi). Beklenti tutmazsa rapor edilir, betik durdurulmaz.
NEGATIF_KONTROL = ["5", "6", "10", "16", "48", "66", "391"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v1.csv")
    ap.add_argument("--out", default="data/iddialar/uretilen_iddialar_v3_temiz.csv")
    ap.add_argument("--v37", default="data/iddialar/uretilen_iddialar_v2_temiz.csv",
                    help="karsilastirma icin v3.7 ciktisi (varsa)")
    ap.add_argument("--rapor", default="sonuclar/temizlik_raporu_v38.txt")
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
    e("RUHSAT-Bench — CERRAHI TEMIZLIK v3.8  (kural kapsami duzeltildi)")
    e("=" * 78)
    e(f"girdi: {a.csv}  ({len(satirlar)} iddia)")
    e("kural kapsami: R1-R5 YALNIZCA kaynak_alinti. iddia metni atma gerekcesi degil.")

    # ---------------------------------------------------------------- [0]
    # Iddia tarafindaki "NNNN sayılı" isabetleri: neden atmiyoruz.
    cerceve, cerceve_disi = [], []
    for s in satirlar:
        iddia = " ".join((s.get("iddia") or "").split())
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        vurus = list(re.finditer(r"\b\d{3,4}\s*[Ss]ay[ıi]l[ıi]\b", iddia))
        if not vurus:
            continue
        if KANUN_ATIF.search(alinti):
            continue  # zaten alintidan dusuyor, burada iki kez sayma
        # Uretim kalibi kanun numarasini iddianin EN BASINA koyar
        # ("3194 sayılı Kanun'un 23. maddesine göre ..."). Cumle icinde,
        # kalip disinda gecen bir numara sizinti adayidir.
        (cerceve if all(m.start() < 40 for m in vurus) else cerceve_disi).append(s)

    e()
    e("[0] IDDIA METNINDEKI 'NNNN sayılı' ISABETLERI  (v3.7'nin atma sebebi)")
    e(f"  iddia cercevesinde kanun numarasi gecen ve alintisi TEMIZ olan satir: "
      f"{len(cerceve) + len(cerceve_disi)}")
    e(f"    uretici kalibindan gelen (zararsiz)            : {len(cerceve)}")
    e(f"    kaliba uymayan / incelenmeli                   : {len(cerceve_disi)}")
    for s in cerceve_disi[:15]:
        e(f"      #{s.get('id',''):<5} {s.get('probe',''):<15} "
          f"{' '.join((s.get('iddia') or '').split())[:90]}")
    e("  KARAR: bunlar v3.8'de ATILMIYOR. 'NNNN sayılı' iddia metninde uretim")
    e("  kalibinin parcasidir; kaynak cumlenin kusuru degildir.")

    # ---------------------------------------------------------------- [1]
    # Bozuk kaynak cumleleri. Bos alinti ortak anahtar OLMAZ.
    bozuk_cumle = {}
    anahtar = {}
    for s in satirlar:
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        k = alinti if alinti else f"<<BOS:{s.get('id','')}>>"
        anahtar[s.get("id", "")] = k
        if not alinti:
            continue
        for ad, f in KURALLAR:
            if f(alinti):
                bozuk_cumle.setdefault(k, []).append(ad)
                break

    e()
    e("[1] BOZUK KAYNAK CUMLELER  (yalnizca alinti uzerinden)")
    e(f"  {len(bozuk_cumle)} farkli kaynak cumle en az bir kurala takildi.")
    for c, kurallar in sorted(bozuk_cumle.items(), key=lambda x: -len(x[0]))[:20]:
        e(f"    [{kurallar[0]}] {c[:110]}")

    # ---------------------------------------------------------------- [2]
    atilan, kalan = [], []
    sebep_say = Counter()
    for s in satirlar:
        k = anahtar[s.get("id", "")]
        if k in bozuk_cumle:
            sebep = bozuk_cumle[k][0]
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
    e("  atilan iddialar (id | probe | gold | sebep):")
    for s, sebep in atilan[:60]:
        e(f"    #{s.get('id',''):<5} {s.get('probe',''):<15} {s.get('gold',''):<8} {sebep}")
        e(f"           {' '.join((s.get('iddia') or '').split())[:100]}")
    if len(atilan) > 60:
        e(f"    ... (+{len(atilan) - 60})")

    # ---------------------------------------------------------------- [3]
    for s in kalan:
        m = VARYANT.search(s.get("uretim_sablonu") or "")
        s["probe_alt"] = m.group(1) if m else (s.get("probe") or "")

    e()
    e("[3] TEMIZ SETIN YAPISI")
    e(f"  {len(satirlar)} -> {len(kalan)} iddia  "
      f"(-{len(atilan)}, %{100.0*len(atilan)/max(len(satirlar),1):.1f})")
    g = Counter(s.get("gold", "") for s in kalan)
    g0 = Counter(s.get("gold", "") for s in satirlar)
    for k in sorted(set(g) | set(g0)):
        e(f"    gold {k:<8} {g0.get(k,0):>4} -> {g.get(k,0):>4}  "
          f"(%{100.0*g.get(k,0)/max(len(kalan),1):.1f})")
    e()
    e("  probe dagilimi (probe / probe_alt):")
    pr = Counter(s.get("probe", "") for s in kalan)
    pr0 = Counter(s.get("probe", "") for s in satirlar)
    pa = defaultdict(Counter)
    for s in kalan:
        pa[s.get("probe", "")][s["probe_alt"]] += 1
    for p in sorted(pr0):
        e(f"    {p:<16} {pr0[p]:>4} -> {pr.get(p,0):>4}  "
          f"(%{100.0*pr.get(p,0)/max(len(kalan),1):.1f})")
        if len(pa[p]) > 1:
            for alt, n in sorted(pa[p].items(), key=lambda x: -x[1]):
                e(f"        {alt:<20} {n:>4}")

    # ---------------------------------------------------------------- [4]
    e()
    e("[4] KAYNAK BELGE KIRILIMI  (karisim testi — v3.7'nin sessiz hasari buradaydi)")
    kn = Counter(s.get("kanun", "") for s in kalan)
    kn0 = Counter(s.get("kanun", "") for s in satirlar)
    for k in sorted(kn0, key=lambda x: -kn0[x]):
        oran = 100.0 * kn.get(k, 0) / max(kn0[k], 1)
        isaret = "   <-- neredeyse silinmis" if oran < 25 else ""
        e(f"    {k:<10} {kn0[k]:>4} -> {kn.get(k,0):>4}  (hayatta %{oran:.0f}){isaret}")
    oranlar = [100.0 * kn.get(k, 0) / max(kn0[k], 1) for k in kn0]
    if oranlar and (max(oranlar) - min(oranlar)) > 40:
        e("  ! UYARI: belgeler arasi hayatta kalma orani 40 puandan fazla ayrisiyor.")
        e("    Temiz kume kaynak belge ile karisir; F4'te prob etkisi belge etkisinden")
        e("    ayrilamaz. Kural kapsami gozden gecirilmeli.")
    else:
        e("  temiz: hayatta kalma orani belgeler arasinda dengeli.")

    # ---------------------------------------------------------------- [5]
    e()
    e("[5] R6 TANI (ATMAZ) — alinti icinde coklu bosluk = sokulmus (Değişik:...) etiketi")
    r6, r6_r1, r6_yalniz = [], [], []
    for s in satirlar:
        ham = s.get("kaynak_alinti") or ""
        if not BOSLUK_IZI.search(ham):
            continue
        r6.append(s)
        (r6_r1 if FIKRA_ICI.search(" ".join(ham.split())) else r6_yalniz).append(s)
    e(f"  bosluk izi tasiyan iddia: {len(r6)}  "
      f"(farkli cumle: {len({' '.join((s.get('kaynak_alinti') or '').split()) for s in r6})})")
    e(f"    + fikra isareti de var (GERCEK KUSUR, R1 zaten atiyor): {len(r6_r1)}")
    e(f"    yalniz etiket bosluğu (ZARARSIZ, kalir)               : {len(r6_yalniz)}")
    e("  Yorum: [B2]'deki 0.44-0.50 kapsanma bu bosluklardan gelir; n-gram")
    e("  bosluk uzerinden atlayamadigi icin kapsanma duser. Kapsanmanin dusuk")
    e("  olmasi tek basina altin hatasi DEGILDIR.")
    for s in r6_yalniz[:10]:
        e(f"      #{s.get('id',''):<5} {s.get('probe',''):<15} gold={s.get('gold',''):<7} "
          f"{' '.join((s.get('kaynak_alinti') or '').split())[:80]}")

    # ---------------------------------------------------------------- [6]
    e()
    e("[6] KONTROLLER")
    atilan_id = {s.get("id", "") for s, _ in atilan}
    kalan_id = {s.get("id", "") for s in kalan}
    tum_id = atilan_id | kalan_id
    pk_hata = []
    e("  pozitif kontrol (DUSMESI zorunlu):")
    for i, gerekce in sorted(POZITIF_KONTROL.items(), key=lambda x: int(x[0])):
        if i not in tum_id:
            e(f"    #{i:<5} ATLANDI (sette yok)")
            continue
        ok = i in atilan_id
        e(f"    #{i:<5} {'GECTI' if ok else 'KALDI  <-- BASARISIZ'}   ({gerekce})")
        if not ok:
            pk_hata.append(i)
    e("  negatif kontrol (YASAMASI beklenir):")
    for i in NEGATIF_KONTROL:
        if i not in tum_id:
            e(f"    #{i:<5} ATLANDI (sette yok)")
            continue
        e(f"    #{i:<5} {'YASIYOR' if i in kalan_id else 'dustu (gerekce yukarida)'}")

    # ---------------------------------------------------------------- [7]
    if os.path.exists(a.v37):
        with open(a.v37, encoding="utf-8-sig") as fh:
            eski = {r["id"] for r in csv.DictReader(fh)}
        geri = kalan_id - eski
        yeni_dusen = eski - kalan_id
        e()
        e("[7] v3.7 ILE FARK")
        e(f"  v3.7 temiz: {len(eski)} | v3.8 temiz: {len(kalan_id)}")
        e(f"  v3.8'de GERI GELEN iddia: {len(geri)}")
        e(f"  v3.8'de yeni dusen       : {len(yeni_dusen)}")
        if geri:
            gp = Counter(s.get("probe", "") for s in kalan if s.get("id") in geri)
            gk = Counter(s.get("kanun", "") for s in kalan if s.get("id") in geri)
            e("    geri gelenlerin probe dagilimi : "
              + ", ".join(f"{k}={v}" for k, v in sorted(gp.items())))
            e("    geri gelenlerin kaynak dagilimi: "
              + ", ".join(f"{k}={v}" for k, v in sorted(gk.items())))
        if yeni_dusen:
            e(f"    yeni dusen id: {', '.join(sorted(yeni_dusen, key=int)[:40])}")

    # ---------------------------------------------------------------- [8]
    e()
    e("[8] DENGE NOTU")
    p5 = pa.get("P5_capraz", Counter())
    if p5:
        ms, ls = p5.get("P5_maddeshift", 0), p5.get("P5_lawshuffle", 0)
        e(f"  P5 alt-turleri: maddeshift {ms} / lawshuffle {ls}")
        if ms and ls and max(ms, ls) / max(min(ms, ls), 1) >= 2:
            e(f"  ! dengesiz ({max(ms,ls)/max(min(ms,ls),1):.1f}x). F4'te AYRI raporlanacak.")
    az = [(p, n) for p, n in pr.items() if n < 40]
    if az:
        e(f"  40'in altinda kalan probe'lar: "
          + ", ".join(f"{p}={n}" for p, n in sorted(az)))

    # ---------------------------------------------------------------- yaz
    if pk_hata:
        e()
        e(f"  ! POZITIF KONTROL BASARISIZ ({', '.join(pk_hata)}). CIKTI YAZILMADI.")
    elif a.kuru:
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
    if pk_hata:
        sys.exit(2)


if __name__ == "__main__":
    main()
