# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — BELGE GUNCELLIK DENETIMI.

SORU
----
Korpustaki kaynak belgeler bugunku resmi metinle ayni mi? Uzunluk
karsilastirmasi bu soruyu CEVAPLAMAZ: korpus kopyalari Word ciktisi,
taze indirmeler wkhtmltopdf; iki uretici bosluk, tire, ustbilgi/altbilgi
ve tirnak karakterlerini farkli isliyor. Olculen fark (-119 / -58 / +87
karakter, binde bir duzeyinde, isaretleri bile farkli) hem bicimlendirme
gurultusu hem de kucuk bir degisiklik olabilir.

DOGRU OLCUT
-----------
Benchmark icin onemli olan belgenin karakteri karakterine ayni olmasi
degil, IDDIALARIN DAYANDIGI CUMLELERIN hala orada olmasidir. Bu yuzden
her iddianin kaynak_alinti'sinin taze metindeki 6-gram kapsanmasi
olculur ve korpustaki kapsanmasiyla karsilastirilir.

    kapsanma_taze ~ kapsanma_korpus   -> iddianin dayanagi duruyor
    kapsanma_taze << kapsanma_korpus  -> dayanak kaybolmus, INCELE

POZITIF KONTROL (zorunlu)
-------------------------
Ayni test once KORPUS metnine uygulanir. Alintlar oradan uretildigi icin
kapsanmanin medyani 1.00 olmali. Olmuyorsa test ariza demektir ve
taze metin sonuclari okunmaz; betik orada durur.

Bilinen istisna: sokulmus "(Değişik:...)" etiketi tasiyan birkac alinti
korpusta da 0.44-0.50 verir (bkz. temizlik raporu R6). Bunlar medyani
bozmaz ve karsilastirma zaten korpusa GORE yapildigi icin sorun cikarmaz.

BICIM MI ICERIK MI
------------------
Ayrica iki metnin cumle kumeleri farki basilir. Farklar ustbilgi/altbilgi
ya da parca cumleyse bicimlendirmedir; "(Değişik:RG-...)" iceren normatif
cumlelerse gercek degisikliktir.

Kullanim:
    python scripts/belge_guncellik.py
    python scripts/belge_guncellik.py --csv data/iddialar/uretilen_iddialar_v5_p6dengeli.csv
"""
import argparse
import csv
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uret_iddia_v3_6 import LAWS, normalize, pdf_metin  # noqa: E402

TOKEN = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü]+")
KUNYE = re.compile(r"Değişik|Mülga|Yeniden düzenleme|RG-|\bmd\.\)")
CUMLE = re.compile(r"(?<=[.:;])\s+")
TARIH = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{4})\b")
PDF_TARIH = re.compile(r"D:(\d{4})(\d{2})(\d{2})")


def alinma_yili(yol):
    """Korpus PDF'inin uretim tarihi = pratikte indirilme tarihi."""
    try:
        from pypdf import PdfReader
        m = PDF_TARIH.search(str((PdfReader(yol).metadata or {}).get("/CreationDate", "")))
        return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    except Exception:
        return None
K = 6


def token_kumesi(t):
    return {kucuk(m.group(0)) for m in TOKEN.finditer(t)}


def kirik_kelimeler(q, taze_tokenlar):
    """Alintida, tazede TEK PARCA olarak bulunan ama korpusta bolunmus kelimeler."""
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(q)]
    bulgu = []
    for i in range(len(toks) - 1):
        if toks[i] in taze_tokenlar:
            continue
        if (toks[i] + toks[i + 1]) in taze_tokenlar:
            bulgu.append(f"{toks[i]}|{toks[i+1]} -> {toks[i]+toks[i+1]}")
    return bulgu


def kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def ngram_kumesi(t):
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(t)]
    return {tuple(toks[i:i + K]) for i in range(len(toks) - K + 1)}


def kapsanma(q, kume):
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(q)]
    if len(toks) < K:
        return None
    top = len(toks) - K + 1
    return sum(1 for i in range(top) if tuple(toks[i:i + K]) in kume) / top


def taze_bul(kod, pdf_dir):
    for ad in (f"_{kod}_taze.pdf", f"_{kod.lower()}_taze.pdf",
               f"_{kod}_konsolide.pdf", f"_{kod.lower()}_konsolide.pdf"):
        y = os.path.join(pdf_dir, ad)
        if os.path.exists(y):
            return y
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v5_p6dengeli.csv")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--esik", type=float, default=0.15,
                    help="kapsanma dususu bu kadari asarsa dayanak kaybi sayilir")
    ap.add_argument("--ornek", type=int, default=6, help="basilacak fark cumlesi sayisi")
    ap.add_argument("--out", default="sonuclar/belge_guncellik.txt")
    ap.add_argument("--kayip", default="sonuclar/dayanak_kaybi.csv")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))

    L, kayiplar = [], []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — BELGE GUNCELLIK DENETIMI")
    e("=" * 78)
    e(f"iddia kumesi: {a.csv}  ({len(satirlar)} iddia)")
    e(f"olcut: kaynak_alinti'nin {K}-gram kapsanmasi; korpus vs taze metin")

    for kod, meta in LAWS.items():
        korpus_y = os.path.join(a.pdf_dir, meta["dosya"])
        taze_y = taze_bul(kod, a.pdf_dir)
        e()
        e("-" * 78)
        e(f"### {kod}   ({meta['kisa']})")
        if not os.path.exists(korpus_y):
            e(f"  ! korpus dosyasi yok: {korpus_y}")
            continue
        if not taze_y:
            e(f"  taze kopya yok -> karsilastirilamadi. Kaynak: {os.path.basename(korpus_y)}")
            e("  Bu belge icin makalede 'alinma tarihindeki haliyle' notu gerekir.")
            continue

        A = normalize(pdf_metin(korpus_y))
        B = normalize(pdf_metin(taze_y))
        e(f"  korpus: {os.path.basename(korpus_y):<32} {len(A):>8} kr  "
          f"kunye {len(KUNYE.findall(A)):>4}")
        e(f"  taze  : {os.path.basename(taze_y):<32} {len(B):>8} kr  "
          f"kunye {len(KUNYE.findall(B)):>4}")
        e(f"  fark  : {len(B)-len(A):+d} kr  (%{100*abs(len(B)-len(A))/max(len(A),1):.3f})")
        if A == B:
            e("  => METINLER BIREBIR AYNI. Bu belge icin guncellik sorusu kapali.")
            continue

        na, nb = ngram_kumesi(A), ngram_kumesi(B)
        ilgili = [s for s in satirlar
                  if s.get("kanun") == kod and (s.get("kaynak_alinti") or "").strip()]
        ka, kb, cift = [], [], []
        for s in ilgili:
            q = " ".join(s["kaynak_alinti"].split())
            x, y = kapsanma(q, na), kapsanma(q, nb)
            if x is None or y is None:
                continue
            ka.append(x)
            kb.append(y)
            cift.append((s, x, y))

        if not cift:
            e("  bu belgeden alintili iddia yok; kapsanma testi uygulanmadi.")
        else:
            med_a, med_b = statistics.median(ka), statistics.median(kb)
            e(f"  alintili iddia: {len(cift)}")
            e(f"  POZITIF KONTROL — korpustaki kapsanma medyani: {med_a:.2f} "
              + ("(beklenen 1.00, GECTI)" if med_a >= 0.95 else "  <-- KALDI, test guvenilmez"))
            if med_a < 0.95:
                e("  ! Kapsanma testi korpusta bile calismiyor; taze sonuc okunmuyor.")
                continue
            e(f"  taze metindeki kapsanma medyani     : {med_b:.2f}")
            dus = [(s, x, y) for s, x, y in cift if x - y > a.esik]
            tb = token_kumesi(B)
            bozuk, incele = [], []
            for s, x, y in dus:
                kir = kirik_kelimeler(s["kaynak_alinti"], tb)
                (bozuk if kir else incele).append((s, x, y, kir))
            e(f"  kapsanmasi dusen iddia (dusus > {a.esik:.2f}): {len(dus)}")
            e(f"    sebep BOZUK KELIME (korpus artigi, taze metin saglam): {len(bozuk)}")
            e(f"    sebep BELIRSIZ (gercek degisiklik adayi)             : {len(incele)}")
            for etiket, grup in (("BOZUK_KELIME", bozuk), ("INCELE", incele)):
                for s, x, y, kir in grup[:10]:
                    e(f"      [{etiket}] #{s['id']:<5} {s.get('probe',''):<15} "
                      f"korpus={x:.2f} taze={y:.2f}"
                      + (f"   kirik: {', '.join(kir[:4])}" if kir else ""))
                    e(f"               {' '.join(s['kaynak_alinti'].split())[:84]}")
                if len(grup) > 10:
                    e(f"      ... (+{len(grup)-10} {etiket})")
            for s, x, y, kir in bozuk + incele:
                kayiplar.append({"id": s["id"], "kanun": kod, "probe": s.get("probe", ""),
                                 "gold": s.get("gold", ""),
                                 "sebep": "BOZUK_KELIME" if kir else "INCELE",
                                 "kirik_parcalar": " | ".join(kir),
                                 "kapsanma_korpus": f"{x:.3f}", "kapsanma_taze": f"{y:.3f}",
                                 "kaynak_alinti": " ".join(s["kaynak_alinti"].split())})
            if not dus:
                e("  => Butun iddialarin dayanagi taze metinde de duruyor.")

        ta = set(TARIH.findall(A))
        tb_ = set(TARIH.findall(B))
        e(f"  DEGISIKLIK TARIHI KUMESI  (uretici bagimsiz olcut)")
        e(f"    korpus {len(ta)} tarih | taze {len(tb_)} tarih")
        def anahtar_t(d):
            g, ay, yil = d.split("/")
            return (int(yil), int(ay), int(g))

        yalniz_taze = sorted(tb_ - ta, key=anahtar_t)
        yalniz_kor = sorted(ta - tb_, key=anahtar_t)
        al = alinma_yili(korpus_y)
        e(f"    korpus alinma tarihi (PDF ustverisi): "
          + (f"{al[2]:02d}.{al[1]:02d}.{al[0]}" if al else "okunamadi"))
        # YON FILTRESI: korpus alindiktan SONRAKI tarihler gercek adaydir.
        # Daha eski bir tarihin tazede "yeni" gorunmesi, korpus renderinda
        # tarihin bolunmus olmasindan kaynaklanir (ornek: "2 1/12/2011").
        if al:
            yeni = [d for d in yalniz_taze if anahtar_t(d) > al]
            eski = [d for d in yalniz_taze if anahtar_t(d) <= al]
        else:
            yeni, eski = yalniz_taze, []
        if yeni:
            e(f"    ! ALINMA TARIHINDEN SONRAKI tarih: {len(yeni)} -> {', '.join(yeni[:10])}")
            e("      GERCEK degisiklik adayi. Ilgili maddeler elden gecirilmeli.")
        else:
            e("    alinma tarihinden sonraki yeni degisiklik tarihi YOK -> korpus guncel.")
        if eski:
            e(f"    (yalniz tazede ama ESKI: {len(eski)} -> {', '.join(eski[:6])}"
              f" — korpusta bolunmus, render artigi)")
        if yalniz_kor:
            e(f"    (yalniz korpusta: {len(yalniz_kor)} -> {', '.join(yalniz_kor[:6])}"
              f" — tazede bolunmus, render artigi)")

        ca = set(CUMLE.split(A))
        cb = set(CUMLE.split(B))
        yalniz_a = [c for c in (ca - cb) if len(c) > 40]
        yalniz_b = [c for c in (cb - ca) if len(c) > 40]
        e(f"  cumle farki: yalniz korpusta {len(yalniz_a)} | yalniz tazede {len(yalniz_b)}")
        kunyeli = [c for c in yalniz_b if KUNYE.search(c)]
        e(f"  (bilgi) tazede kunye tasiyan farkli cumle: {len(kunyeli)}")
        e("  NOT: bu sayi ZAYIF bir sinyaldir. Iki render cumleyi farkli yerden")
        e("  boldugu icin ayni kunye iki tarafta da farkli cumleye dusebilir.")
        e("  Belirleyici olcut yukaridaki TARIH KUMESI ve kapsanma testidir.")
        for c in yalniz_b[:a.ornek]:
            e(f"      taze+ {c[:100]}")
        for c in yalniz_a[:a.ornek]:
            e(f"      korpus+ {c[:100]}")

    if kayiplar:
        os.makedirs(os.path.dirname(a.kayip) or ".", exist_ok=True)
        with open(a.kayip, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(kayiplar[0].keys()))
            w.writeheader()
            w.writerows(kayiplar)
        print(f"\nyazildi: {a.kayip}  ({len(kayiplar)} iddia)")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.out}")


if __name__ == "__main__":
    main()
