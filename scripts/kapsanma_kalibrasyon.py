# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — [C2] icin POZITIF KONTROL + filtre-etkisi olcumu (MODELSIZ).

NEDEN BU DOSYA VAR
------------------
kaynak_dogrula_v2.py'nin [C2] kontrolu 34 P5_lawshuffle iddiasinin HEPSINDE
kapsanma = 0.00 dondurdu. Bir kontrolun tabana yapisik cikmasinin iki ayri
aciklamasi olabilir:

  (H1) Kontrol dogru calisiyor ve gercekten kazara-dogru yok.
  (H2) Kontrol sessizce bos donuyor (yanlis hedef belge, bos n-gram haritasi,
       tokenizasyon uyusmazligi) ve 0.00 bir OLCUM degil bir ARIZA.

Sifir sonucu tek basina H1'i kanitlamaz. Bu betik ikisini ayirir:

  [1] POZITIF KONTROL. Ayni cumlenin KAYNAK belgedeki kapsanmasi olculur.
      Cumle oradan alindigi icin ~1.00 cikmali. Kaynak ~1.00 ve hedef 0.00
      ise mekanizma gercek veride ayirt edici demektir; 0.00 bir olcumdur.
      Kaynak da 0.00 cikarsa [C2] arizalidir ve [E] karari gecersizdir.

  [2] TAVAN OLCUMU. Belgeler arasi gercek tekrar taranir: X'in her aday
      cumlesi Y'de aranir. Boylece "bu korpusta kazara-dogruluk uretebilecek
      cumle havuzu ne kadar?" sorusu olculur. Her tekrar eden cumle icin
      uretecin temiz_mi() suzgeci de calistirilir. Hipotez: tekrar eden
      cumleler (Amac/Kapsam/Dayanak/Tanimlar/Yururluk) HUKUM_ANAHTAR + fiil
      sonu sartina takildigi icin iddia havuzuna hic girmiyor. Dogruysa
      [C2]'nin bos cikmasi sans degil TASARIM sonucudur ve makalede
      "suzgec, kazara-dogruluk riskini uretim aninda yok ediyor" diye
      raporlanabilir.

  [3] Tekrar eden VE temiz_mi'yi gecen cumle varsa: bunlar gercek risk
      havuzudur; 34 lawshuffle iddiasindan kaci bu havuzdan cekilmis
      sayilir.

Kullanim:
    python scripts/kapsanma_kalibrasyon.py
    python scripts/kapsanma_kalibrasyon.py --ayrinti
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uret_iddia_v3_6 import temiz_mi, normalize, pdf_metin  # noqa: E402

LAWS = {
    "6331": "6331_isg_kanunu.pdf",
    "4708": "4708_yapi_denetimi.pdf",
    "3194": "3194_imar_kanunu.pdf",
    "ISGRISK": "isg_risk_yonetmeligi.pdf",
    "TBDY": "TBDY_2018.pdf",
    "YDUY": "yapi_denetim_uygulama_yon.pdf",
}

TOKEN = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü]+")
VARYANT = re.compile(r"(P5_maddeshift|P5_lawshuffle|P2_swap)\(([^)]*)\)")
K = 6


def kucuk(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def ngram_kumesi(t):
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(t)]
    return {tuple(toks[i:i + K]) for i in range(len(toks) - K + 1)}


def kapsanma(q, kume):
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(q)]
    if len(toks) < K:
        return 0.0
    top = len(toks) - K + 1
    return sum(1 for i in range(top) if tuple(toks[i:i + K]) in kume) / top


def metin_yukle(kod, pdf_dir, txt_dir):
    if txt_dir:
        p = os.path.join(txt_dir, kod + ".txt")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return normalize(fh.read())
    p = os.path.join(pdf_dir, LAWS[kod])
    if not os.path.exists(p) and os.path.isdir(pdf_dir):
        anahtar = kod.lower().replace("isgrisk", "risk").replace("yduy", "uygulama")
        aday = [f for f in sorted(os.listdir(pdf_dir))
                if f.lower().endswith(".pdf") and anahtar in f.lower()]
        if len(aday) == 1:
            p = os.path.join(pdf_dir, aday[0])
    if not os.path.exists(p):
        return None
    return normalize(pdf_metin(p))


BASLIK_ONEK = re.compile(
    r"^(?:(?:Geçici|Ek|GEÇİCİ|EK)\s+)?(?:Madde|MADDE)\s+\d{1,3}\s*[–\-—.:]\s*"
    r"|^\d{1,2}(?:\.\d{1,2}){1,3}\s*[–\-—]\s*")


def aday_cumleler(metin):
    """cumleler() ile ayni bolme, ama temiz_mi SUZGECI UYGULANMADAN.

    Ek olarak madde/bent basligi oneki sokulur: uretecte cumleler() madde
    BLOGUNA uygulandigi icin baslik cumleye yapismaz; burada tum belge
    taranidigi icin elle sokmek gerekiyor, yoksa temiz_mi sonucu ve uzunluk
    olcusu yapay olarak kayar.
    """
    metin = re.sub(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]*\)", " ", metin)
    out = []
    for c in re.split(r"(?<=\.)\s+", metin):
        c = re.sub(r"^\(?[a-z0-9]{1,2}\)\s*", "", c.strip()).strip()
        c = BASLIK_ONEK.sub("", c).strip()
        if 60 <= len(c) <= 300:
            out.append(c)
    return list(dict.fromkeys(out))  # ayni cumle bir kez sayilsin


def ozet(v):
    if not v:
        return "yok"
    s = sorted(v)
    n = len(s)
    return (f"min={s[0]:.2f} q1={s[n//4]:.2f} med={s[n//2]:.2f} "
            f"q3={s[(3*n)//4]:.2f} max={s[-1]:.2f}")


def varyantlar(satir):
    ham = " ".join([satir.get("uretim_sablonu") or "", satir.get("degisiklik_notu") or ""])
    out = []
    for m in VARYANT.finditer(ham):
        parcalar = [p for p in re.split(r"[^0-9A-Za-zÇĞİÖŞÜçğıöşü_.]+", m.group(2)) if p]
        out.append((m.group(1), parcalar))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v1.csv")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--txt-dir", default="")
    ap.add_argument("--out", default="sonuclar/kapsanma_kalibrasyon.txt")
    ap.add_argument("--csv-out", default="sonuclar/tekrar_eden_cumleler.csv")
    ap.add_argument("--esik-kesin", type=float, default=0.85)
    ap.add_argument("--esik-suphe", type=float, default=0.60)
    ap.add_argument("--max-cumle", type=int, default=6000)
    ap.add_argument("--ayrinti", action="store_true")
    a = ap.parse_args()

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))

    e("=" * 78)
    e("RUHSAT-Bench — [C2] POZITIF KONTROL + FILTRE ETKISI")
    e("=" * 78)
    e(f"iddia dosyasi: {a.csv}  ({len(satirlar)} iddia)")

    metinler, kumeler = {}, {}
    for kod in sorted(LAWS):
        t = metin_yukle(kod, a.pdf_dir, a.txt_dir)
        if t is None:
            e(f"  ! kaynak bulunamadi: {kod}")
            continue
        metinler[kod] = t
        kumeler[kod] = ngram_kumesi(t)
        e(f"  {kod:<9} {len(t):>9} karakter   {len(kumeler[kod]):>8} farkli {K}-gram")
    if not kumeler:
        e("  ! hicbir belge yuklenemedi, cikiliyor.")
        return

    bos = [k for k, v in kumeler.items() if len(v) < 100]
    if bos:
        e(f"  ! SUPHELI: {', '.join(bos)} icin n-gram haritasi neredeyse bos.")

    # ------------------------------------------------------------------ [1]
    e()
    e("[1] POZITIF KONTROL  (lawshuffle cumlesinin KENDI belgesindeki kapsanmasi)")
    e("  Beklenti: kaynak ~1.00, hedef ~0.00. Kaynak da 0.00 ise [C2] arizalidir.")
    kay_v, hed_v, ciftler = [], [], []
    for s in satirlar:
        for tur, p in varyantlar(s):
            if tur != "P5_lawshuffle" or len(p) < 2:
                continue
            kk, hk = p[0], p[1]
            alinti = " ".join((s.get("kaynak_alinti") or "").split())
            if len(alinti) < 40 or kk not in kumeler or hk not in kumeler:
                continue
            ok, oh = kapsanma(alinti, kumeler[kk]), kapsanma(alinti, kumeler[hk])
            kay_v.append(ok)
            hed_v.append(oh)
            ciftler.append((ok, oh, s.get("id", ""), kk, hk, alinti[:90]))

    e(f"  olculen lawshuffle iddiasi: {len(ciftler)}")
    e(f"  KAYNAK belgede kapsanma : {ozet(kay_v)}")
    e(f"  HEDEF  belgede kapsanma : {ozet(hed_v)}")
    dusuk = [c for c in ciftler if c[0] < 0.85]
    if dusuk:
        e(f"  ! kaynak kapsanmasi 0.85 altinda kalan {len(dusuk)} satir:")
        for c in sorted(dusuk)[:15]:
            e(f"      #{c[2]:<5} {c[3]}->{c[4]:<8} kaynak={c[0]:.2f} hedef={c[1]:.2f}")
            e(f"             {c[5]}")
    yuksek = sorted((c for c in ciftler if c[1] >= a.esik_suphe),
                    key=lambda c: -c[1])
    if yuksek:
        e(f"  ! HEDEF belgede de gecen {len(yuksek)} satir (kazara-dogru adayi;")
        e("    [C2] ile ayni bulgu olmali - degilse iki katman celisiyor demektir):")
        for c in yuksek[:15]:
            e(f"      #{c[2]:<5} {c[3]}->{c[4]:<8} hedef={c[1]:.2f}")
            e(f"             {c[5]}")
    if kay_v and min(kay_v) >= 0.85 and max(hed_v) < 0.10:
        e("  => KANIT: mekanizma gercek veride tam ayirt edici. [C2]=0.00 bir OLCUMDUR.")
    elif kay_v and max(kay_v) < 0.10:
        e("  => ARIZA: kaynak belgede bile bulunamiyor. [C2] sonucu GECERSIZ.")
    else:
        e("  => KISMI: ayrim var ama tam degil; asagidaki dusuk satirlara bakin.")

    # ------------------------------------------------------------------ [2]
    e()
    e("[2] TAVAN OLCUMU  (belgeler arasi GERCEK tekrar ve suzgecin etkisi)")
    e("  X'in her aday cumlesi (60-300 karakter) Y'de aranir. temiz_mi() ayrica")
    e("  calistirilir: tekrar eden cumle iddia havuzuna girebilir miydi?")
    adaylar = {}
    for kod in sorted(kumeler):
        c = aday_cumleler(metinler[kod])
        if len(c) > a.max_cumle:
            e(f"  ! {kod}: {len(c)} aday cumleden ilk {a.max_cumle} taraniyor (kirpildi).")
            c = c[:a.max_cumle]
        adaylar[kod] = c
    e(f"  aday cumle sayisi: {', '.join(f'{k}={len(v)}' for k, v in sorted(adaylar.items()))}")

    tekrar = []
    cift_say = defaultdict(lambda: [0, 0])
    for x in sorted(adaylar):
        for y in sorted(kumeler):
            if x == y:
                continue
            for c in adaylar[x]:
                o = kapsanma(c, kumeler[y])
                if o < a.esik_suphe:
                    continue
                t = temiz_mi(c)
                cift_say[(x, y)][0 if o >= a.esik_kesin else 1] += 1
                tekrar.append((o, x, y, t, c))
    tekrar.sort(reverse=True)

    n_kesin = sum(1 for t in tekrar if t[0] >= a.esik_kesin)
    n_suphe = len(tekrar) - n_kesin
    gecen = [t for t in tekrar if t[3]]
    e()
    e(f"  tekrar eden cumle olayi: {len(tekrar)}  "
      f"(>={a.esik_kesin}: {n_kesin} | {a.esik_suphe}-{a.esik_kesin}: {n_suphe})")
    e(f"  bunlardan temiz_mi() SUZGECINI GECEN: {len(gecen)}")
    if tekrar and not gecen:
        e("  => Tekrar eden butun cumleler suzgece takiliyor. [C2]'nin bos cikmasi")
        e("     tesaduf degil: risk havuzu uretim aninda zaten bosaltilmis.")
    elif not tekrar:
        e("  => Bu korpusta belgeler arasi kayda deger tekrar YOK. Kazara-dogruluk")
        e("     riski lawshuffle icin yapisal olarak dusuk.")
    else:
        e("  => DIKKAT: suzgeci gecen tekrar eden cumle var; gercek risk havuzu bu.")
        for t in gecen[:20]:
            e(f"      {t[1]}->{t[2]:<8} kapsanma={t[0]:.2f}  {t[4][:100]}")

    if a.ayrinti and tekrar:
        e()
        e("  belge cifti bazinda (kesin / supheli):")
        for (x, y), v in sorted(cift_say.items(), key=lambda z: -(z[1][0] + z[1][1])):
            e(f"    {x:<9} -> {y:<9} {v[0]:>4} / {v[1]:>4}")
        e()
        e("  en yuksek 15 tekrar (suzgec sonucu ile):")
        for t in tekrar[:15]:
            e(f"    {t[0]:.2f} {t[1]}->{t[2]:<9} temiz_mi={str(t[3]):<5} {t[4][:88]}")

    # ------------------------------------------------------------------ [3]
    e()
    e("[3] RISK HAVUZU ILE IDDIA SETININ KESISIMI")
    riskli = list({" ".join(t[4].split()) for t in gecen})
    if not riskli:
        e(f"  risk havuzu bos -> {len(ciftler)} lawshuffle iddiasinin hicbiri riskli")
        e("  cumleden turemis olamaz. [C2] sonucu yapisal olarak guvenli.")
    else:
        # tam metin esitligi kirilgan (kirpma/normalize farki); kapsanma ile eslestir
        risk_kume = ngram_kumesi(" . ".join(riskli))
        vur = []
        for s in satirlar:
            al = " ".join((s.get("kaynak_alinti") or "").split())
            if len(al) >= 40 and kapsanma(al, risk_kume) >= a.esik_kesin:
                vur.append(s.get("id", ""))
        e(f"  risk havuzu: {len(riskli)} cumle | bu havuzdan turemis iddia: {len(vur)}")
        if vur:
            e(f"    id: {', '.join(vur[:40])}")
            e("    -> bu id'ler kazara-dogru acisindan ELDEN GECIRILMELI.")

    e()
    e("[4] KARAR")
    if kay_v and min(kay_v) >= 0.85 and max(hed_v) < 0.10 and not gecen:
        e("  [C2] gecerli VE bos. Kazara-dogruluk lawshuffle'da yok; sebebi sans degil")
        e("  uretecin muhafazakar cumle suzgeci. Bu, makalede olculmus bir tasarim")
        e("  sonucu olarak raporlanabilir (geri cagirmadan feragat -> etiket gecerliligi).")
    elif kay_v and max(kay_v) < 0.10:
        e("  [C2] ARIZALI. kaynak_dogrula_v2 [E] karari lawshuffle boyutunda gecersiz;")
        e("  once bu duzeltilmeli.")
    else:
        e("  Karisik sonuc; yukaridaki dusuk/riskli satirlar elden gecirilmeli.")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\nyazildi: {a.out}")

    if tekrar:
        os.makedirs(os.path.dirname(a.csv_out) or ".", exist_ok=True)
        with open(a.csv_out, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["kapsanma", "kaynak", "hedef", "temiz_mi_gecti", "cumle"])
            for t in tekrar:
                w.writerow([f"{t[0]:.2f}", t[1], t[2], int(t[3]), t[4][:300]])
        print(f"yazildi: {a.csv_out}")


if __name__ == "__main__":
    main()
