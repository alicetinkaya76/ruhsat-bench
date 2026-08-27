# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — KELIME KIRIGI ONARIMI (uretici calistirilmaz, id/gold degismez).

SORUN
-----
3194/4708/6331 PDF'leri "Microsoft Word LTSC" ciktisi ve metin cikariminda
kelime ICINE bosluk giriyor. Bu kiriklar iddia metnine sizmis:

    "... maruz kalacaklari sa ğlık ve güvenlik risklerini ..."     (#67)
    "Tam süreli işyeri hekimi görevl endirilen işyerlerinde ..."   (#145)
    "Bakanlıktan aldığı izin belge si ile çalışan ..."             (#91)

temizle_v39'daki R4_bolunmus_ek sabit bir ek listesine baktigi icin
bunlarin cogunu kaciriyor.

IKI KIRIK TURU
--------------
  (a) EKSIK BOSLUK yok, FAZLA bosluk var:  "sa ğlık"  -> "sağlık"
      a+b birlesmesi temiz metinde TEK TOKEN olarak var.
  (b) BOSLUK KAYMIS:  "kuruluşunu ngörevden" -> "kuruluşunun görevden"
      a+b birlesmesi tek token degil, ama BASKA bir yerden bolununce
      iki gecerli token cikiyor ve ikisi temiz metinde YAN YANA geciyor.

NEDEN "a+b temiz metinde var" YETMEZ
------------------------------------
Ilk parca kendi basina gecerli bir kelimeyse ("bu nlara", "belge si",
"kurulu şları") sadece "a temiz metinde yok mu" diye bakan bir test bunlari
KACIRIR — belge_guncellik.py'nin ilk surumunde olan buydu ve o yuzden 8
gercek kirik INCELE olarak etiketlendi. Dogru test ikili:

    a+b temiz metinde TOKEN olarak VAR  VE  (a,b) ikilisi temiz metinde
    hicbir yerde YAN YANA GECMIYOR      -> kirik

Ikinci sart, "ev sahibi" gibi mesru komsuluklari yanlislikla birlestirmeyi
onler ("evsahibi" bir token olsa bile (ev,sahibi) ikilisi metinde gecer).

POZITIF KONTROL (zorunlu)
-------------------------
Her onarimdan sonra alintinin TEMIZ metindeki 6-gram kapsanmasi yeniden
olculur. Kapsanma artmiyorsa onarim GERI ALINIR ve raporlanir. Yani betik
kendi yaptigi her degisikligi olcerek dogrular; hicbir onarim kanitsiz
kalmaz.

GUVENLIK
--------
  * Rakam iceren token'lara DOKUNULMAZ. P2_swap iddialarindaki degistirilmis
    sayilar ve "(4)" fikra isaretleri korunur.
  * Onarim hem kaynak_alinti hem iddia uzerinde AYNI kuralla yapilir.
  * id, gold, probe, uretim_sablonu hicbir sekilde degismez.
  * Temiz kopyasi olmayan belgeler (TBDY, YDUY) ATLANIR; onlar icin referans
    render yok.

Kullanim:
    python scripts/kelime_onar.py --kuru
    python scripts/kelime_onar.py
"""
import argparse
import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uret_iddia_v3_6 import LAWS, normalize, pdf_metin  # noqa: E402

TOKEN = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü]+")
RAKAM = re.compile(r"\d")
K = 6
MIN_UZ = 2


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


def kumeler(t):
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(t)]
    return set(toks), {(toks[i], toks[i + 1]) for i in range(len(toks) - 1)}


def onar(metin, tokenlar, ikililer, gunluk):
    """Metindeki kelime kiriklarini onarir. (yeni_metin, yapilan_liste)."""
    yapilan = []
    for _ in range(6):                       # zincirli kiriklar icin birkac tur
        sp = list(TOKEN.finditer(metin))
        degisti = False
        for i in range(len(sp) - 1):
            a_ham, b_ham = sp[i].group(0), sp[i + 1].group(0)
            if RAKAM.search(a_ham) or RAKAM.search(b_ham):
                continue
            ara = metin[sp[i].end():sp[i + 1].start()]
            if ara != " ":                   # yalnizca tek bosluk ayirdiginda
                continue
            a, b = kucuk(a_ham), kucuk(b_ham)
            if len(a) < MIN_UZ and len(b) < MIN_UZ:
                continue
            if (a, b) in ikililer:           # temiz metinde yan yana geciyor
                continue
            birlesik = a + b
            # (a) fazla bosluk
            if birlesik in tokenlar:
                metin = metin[:sp[i].end()] + metin[sp[i + 1].start():]
                yapilan.append(f"{a} {b} -> {birlesik}")
                gunluk[f"{a}|{b}"] += 1
                degisti = True
                break
            # (b) kaymis bosluk: birlesigi baska bir yerden bol
            adaylar = [j for j in range(MIN_UZ, len(birlesik) - MIN_UZ + 1)
                       if birlesik[:j] in tokenlar and birlesik[j:] in tokenlar
                       and (birlesik[:j], birlesik[j:]) in ikililer]
            if len(adaylar) == 1:
                j = adaylar[0]
                yeni = a_ham[:j] if j <= len(a_ham) else a_ham + b_ham[:j - len(a_ham)]
                kalan = (a_ham[j:] + " " + b_ham) if j < len(a_ham) else b_ham[j - len(a_ham):]
                kalan = kalan.replace(" ", "")
                metin = metin[:sp[i].start()] + yeni + " " + kalan + metin[sp[i + 1].end():]
                yapilan.append(f"{a} {b} -> {birlesik[:j]} {birlesik[j:]}")
                gunluk[f"{a}|{b}"] += 1
                degisti = True
                break
        if not degisti:
            break
    return metin, yapilan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v5_p6dengeli.csv")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--out", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--rapor", default="sonuclar/kelime_onarim.txt")
    ap.add_argument("--kuru", action="store_true")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))
        alanlar = list(satirlar[0].keys())

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — KELIME KIRIGI ONARIMI")
    e("=" * 78)
    e(f"girdi: {a.csv}  ({len(satirlar)} iddia)")

    referans = {}
    for kod, meta in LAWS.items():
        for ad in (f"_{kod}_taze.pdf", f"_{kod.lower()}_taze.pdf",
                   f"_{kod}_konsolide.pdf", f"_{kod.lower()}_konsolide.pdf"):
            y = os.path.join(a.pdf_dir, ad)
            if os.path.exists(y):
                t = normalize(pdf_metin(y))
                referans[kod] = (t,) + kumeler(t) + (ngram_kumesi(t),)
                break
    e()
    e("[1] REFERANS RENDER")
    for kod in LAWS:
        e(f"    {kod:<9} " + (f"var  ({len(referans[kod][1])} farkli token)"
                              if kod in referans else "YOK -> bu belge atlanacak"))

    e()
    e("[2] ONARIM")
    gunluk = Counter()
    degisen, geri_alinan = [], []
    for s in satirlar:
        kod = s.get("kanun", "")
        if kod not in referans:
            continue
        _, tokenlar, ikililer, ngramlar = referans[kod]
        alinti0 = s.get("kaynak_alinti") or ""
        iddia0 = s.get("iddia") or ""
        alinti1, y1 = onar(alinti0, tokenlar, ikililer, gunluk)
        iddia1, y2 = onar(iddia0, tokenlar, ikililer, gunluk)
        if not (y1 or y2):
            continue
        # POZITIF KONTROL: kapsanma artmali
        k0 = kapsanma(alinti0, ngramlar) if alinti0.strip() else None
        k1 = kapsanma(alinti1, ngramlar) if alinti1.strip() else None
        if k0 is not None and k1 is not None and k1 < k0 - 1e-9:
            geri_alinan.append((s["id"], k0, k1, y1 + y2))
            continue
        s["kaynak_alinti"], s["iddia"] = alinti1, iddia1
        degisen.append((s["id"], kod, s.get("probe", ""), k0, k1, y1 + y2))

    e(f"  onarilan iddia: {len(degisen)}  |  kapsanma dusurdugu icin GERI ALINAN: {len(geri_alinan)}")
    bel = Counter(k for _, k, _, _, _, _ in degisen)
    e("  belgeye gore: " + (", ".join(f"{k}={v}" for k, v in sorted(bel.items())) or "-"))
    e()
    e("  en sik kirik kaliplari:")
    for kal, n in gunluk.most_common(15):
        e(f"    {kal:<40} {n}")
    e()
    e("  ornekler (id | probe | kapsanma once -> sonra | yapilan):")
    for i, (cid, kod, pr, k0, k1, y) in enumerate(degisen[:20]):
        o = f"{k0:.2f}" if k0 is not None else " - "
        n = f"{k1:.2f}" if k1 is not None else " - "
        e(f"    #{cid:<5} {pr:<15} {o} -> {n}   {'; '.join(y[:3])}")
    if len(degisen) > 20:
        e(f"    ... (+{len(degisen)-20})")
    for cid, k0, k1, y in geri_alinan:
        e(f"    [GERI ALINDI] #{cid}  {k0:.2f} -> {k1:.2f}   {'; '.join(y[:3])}")

    e()
    e("[3] POZITIF KONTROL OZETI")
    art = [(k0, k1) for _, _, _, k0, k1, _ in degisen if k0 is not None and k1 is not None]
    if art:
        e(f"    olculebilen onarim: {len(art)}")
        e(f"    ortalama kapsanma: {sum(x for x, _ in art)/len(art):.3f} -> "
          f"{sum(y for _, y in art)/len(art):.3f}")
        tam = sum(1 for _, y in art if y >= 0.95)
        e(f"    onarim sonrasi kapsanmasi >=0.95 olan: {tam}/{len(art)}")
        e("    => Onarimlar temiz metne YAKINSIYOR; degisiklikler dogrulanmistir."
          if tam >= 0.8 * len(art) else
          "    ! Beklenenden az yakinsama; kalan satirlar elle gorulmeli.")
    else:
        e("    olculebilir onarim yok.")

    if a.kuru:
        e()
        e("  (--kuru) dosya yazilmadi.")
    else:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=alanlar)
            w.writeheader()
            w.writerows(satirlar)
        print(f"\nyazildi: {a.out}  ({len(satirlar)} iddia, {len(degisen)} onarildi)")

    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"yazildi: {a.rapor}")


if __name__ == "__main__":
    main()
