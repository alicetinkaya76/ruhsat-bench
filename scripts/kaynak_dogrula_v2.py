# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — kaynak-kimlik dogrulayici v2 (MODEL KULLANMAZ).

v1'e gore DUZELTME + GENISLETME:

  DUZELTME. v1'de [C] kontrolu hicbir satirda calismadi ("P5_maddeshift
  iddiasi: 0"). Sebep uretecin kendisinde: uret_iddia_v3_6.py icindeki

      def ekle(kanun, madde_no, probe, iddia, gold, alinti, sablon, deg="")

  imzasina P5/P2 cagrileri 7 konumlu argumanla gidiyor, yani varyant etiketi
  ("P5_maddeshift(12->7)") 'degisiklik_notu' sutununa DEGIL 'uretim_sablonu'
  sutununa yaziliyor. degisiklik_notu yalnizca P6_guncellik satirlarinda dolu.
  v2 etiketi her iki sutundan da okur ve ok karakterine bagimli degildir.

  GENISLETME. Kazara-dogruluk yalnizca madde-kaydirmada olusmuyor:
    [C1] P5_maddeshift(A->B): cumle gercekten B'de de geciyorsa iddia DOGRU,
         altin YANLIS -> kesin altin hatasi.
    [C2] P5_lawshuffle(X->Y): cumle Y belgesinde de (neredeyse ayni sekilde)
         geciyorsa -- mevzuatta Amac/Kapsam/Dayanak/Tanimlar/Yururluk kaliplari
         belgeler arasi tekrar eder -- iddia DOGRU, altin YANLIS.
    [C3] P2_swap(a->b): saptirilan sayi bir madde/fikra ATFI ise iddia
         "yanlis nicelik" degil "yanlis atif" testine donusur (kalite uyarisi).

  Ayrica [B] artik cumlenin TUM gectigi yerleri toplar (tek yer degil) ve
  tam eslesme basarisiz olursa 6-kelimelik n-gram kapsanmasiyla yaklasik
  konum bulur; boylece v1'deki "metinde bulunamadi" satirlari aciklanir.

Kullanim:
    python scripts/kaynak_dogrula_v2.py --ayrinti
"""
import argparse
import csv
import os
import re
from collections import defaultdict

LAWS = {
    "6331": "6331_isg_kanunu.pdf",
    "4708": "4708_yapi_denetimi.pdf",
    "3194": "3194_imar_kanunu.pdf",
    "ISGRISK": "isg_risk_yonetmeligi.pdf",
    "TBDY": "TBDY_2018.pdf",
    "YDUY": "yapi_denetim_uygulama_yon.pdf",
}

SIKI = re.compile(r"(?:Madde|MADDE)\s+(\d{1,3})\s*[–\-—]")
GEVSEK = re.compile(
    r"(?:(Geçici|Ek|GEÇİCİ|EK)\s+)?(?:Madde|MADDE)\s+(\d{1,3})"
    r"\s*(?:[–\-—]|\(\d\)|[.:])"
)
BENT = re.compile(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\s*[–\-—]\s")
TOKEN = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü]+")
VARYANT = re.compile(r"(P5_maddeshift|P5_lawshuffle|P2_swap)\(([^)]*)\)")
ATIF = re.compile(r"madde|fıkra|bent|bendi|sayılı|inci|ıncı|üncü|uncu|nci|ncı")
K = 6  # n-gram uzunlugu


def pdf_metin(path):
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


def normalize(t):
    """uret_iddia_v3_6.py ile BIREBIR ayni olmali; konum eslesmesi buna bagli."""
    t = t.replace("­", "")
    t = re.sub(r"-\n(?=[a-zçğıöşü])", "", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\b([bcçdfgğhıijklmnöprsştuüvyzBCÇDFGĞHİIJKLMNÖPRSŞTUÜVYZe])"
               r"\s(?=[a-zçğıöşü]{2,}\b)", r"\1", t)
    for bozuk, dogru in [("herh angi", "herhangi"), ("hal lerde", "hallerde"), ("İma r", "İmar"),
                         ("v eilgili", "ve ilgili"), ("v e ", "ve "), ("il gili", "ilgili"),
                         ("yü kümlü", "yükümlü"), ("zo runlu", "zorunlu"),
                         ("artı rılır", "artırılır"), ("inti kal", "intikal"),
                         ("ücretl erini", "ücretlerini"), ("inşa at", "inşaat"),
                         ("başv uru", "başvuru"), ("düzenl enir", "düzenlenir")]:
        t = t.replace(bozuk, dogru)
    return t


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
            print(f"  (dosya adi esleme: {kod} -> {aday[0]})")
            p = os.path.join(pdf_dir, aday[0])
    if not os.path.exists(p):
        return None
    return normalize(pdf_metin(p))


def basliklar(t):
    siki_konum = {m.start() for m in SIKI.finditer(t)}
    out = []
    for m in GEVSEK.finditer(t):
        out.append({"konum": m.start(), "no": int(m.group(2)),
                    "onek": (m.group(1) or "").strip(),
                    "siki": m.start() in siki_konum,
                    "ham": t[m.start():m.start() + 42]})
    return out


def bent_basliklari(t):
    return [{"konum": m.start(), "no": m.group(1), "onek": "", "siki": True,
             "ham": t[m.start():m.start() + 42]} for m in BENT.finditer(t)]


def onceki_baslik(bas, konum):
    son = None
    for b in bas:
        if b["konum"] <= konum:
            son = b
        else:
            break
    return son


def etiket(bas):
    if not bas:
        return None
    return f"{bas['onek']} {bas['no']}".strip() if bas["onek"] else str(bas["no"])


def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def ngram_haritasi(t):
    """n-gram -> metindeki ilk karakter konumu."""
    toks = [(kucuk(m.group(0)), m.start()) for m in TOKEN.finditer(t)]
    d = {}
    for i in range(len(toks) - K + 1):
        anahtar = tuple(toks[j][0] for j in range(i, i + K))
        if anahtar not in d:
            d[anahtar] = toks[i][1]
    return d


def kapsanma(q, harita):
    """(oran, medyan_konum): q'nun n-gramlarinin ne kadari hedef belgede var."""
    toks = [kucuk(m.group(0)) for m in TOKEN.finditer(q)]
    if len(toks) < K:
        return 0.0, -1
    konumlar = []
    top = len(toks) - K + 1
    for i in range(top):
        p = harita.get(tuple(toks[i:i + K]))
        if p is not None:
            konumlar.append(p)
    if not konumlar:
        return 0.0, -1
    konumlar.sort()
    return len(konumlar) / top, konumlar[len(konumlar) // 2]


def tum_konumlar(t, s, limit=25):
    out, p = [], t.find(s)
    while p >= 0 and len(out) < limit:
        out.append(p)
        p = t.find(s, p + 1)
    return out


def varyantlar(satir):
    """uretim_sablonu VE degisiklik_notu birlikte taranir (v1 hatasinin duzeltmesi)."""
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
    ap.add_argument("--ayrinti", action="store_true")
    ap.add_argument("--esik-kesin", type=float, default=0.85)
    ap.add_argument("--esik-suphe", type=float, default=0.60)
    ap.add_argument("--esik-yaklasik", type=float, default=0.45,
                    help="[B] tam eslesme yoksa konumu n-gram ile atama esigi")
    ap.add_argument("--out", default="sonuclar/kaynak_dogrulama_v2.txt")
    ap.add_argument("--hata-csv", default="sonuclar/altin_hatalari_v2.csv")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — KAYNAK KIMLIK DOGRULAMA v2 (deterministik, modelsiz)")
    e("=" * 78)
    e(f"iddia sayisi: {len(satirlar)}")

    sayac = defaultdict(int)
    for s in satirlar:
        for tur, _ in varyantlar(s):
            sayac[tur] += 1
    e(f"varyant etiketi okundu -> P5_maddeshift: {sayac['P5_maddeshift']} | "
      f"P5_lawshuffle: {sayac['P5_lawshuffle']} | P2_swap: {sayac['P2_swap']}")
    if not sayac:
        e("  ! HIC varyant etiketi okunamadi. CSV'de 'uretim_sablonu' sutunu var mi?")

    metinler, basl, harita = {}, {}, {}
    kodlar = sorted({s.get("kanun", "") for s in satirlar if s.get("kanun")})
    # lawshuffle hedefleri CSV'de kanun sutunu olarak gecmese de yuklenmeli
    for s in satirlar:
        for tur, p in varyantlar(s):
            if tur == "P5_lawshuffle" and len(p) >= 2:
                for x in p[:2]:
                    if x in LAWS and x not in kodlar:
                        kodlar.append(x)
    for kod in sorted(set(kodlar)):
        if kod not in LAWS:
            e(f"  ! bilinmeyen kaynak kodu: {kod}")
            continue
        t = metin_yukle(kod, a.pdf_dir, a.txt_dir)
        if t is None:
            e(f"  ! kaynak dosya bulunamadi: {os.path.join(a.pdf_dir, LAWS[kod])}")
            continue
        metinler[kod] = t
        basl[kod] = bent_basliklari(t) if kod == "TBDY" else basliklar(t)
        harita[kod] = ngram_haritasi(t)

    e()
    e("[A] BASLIK TARAMASI  (yutulan madde tespiti)")
    yutulan = defaultdict(list)
    for kod in sorted(metinler):
        bas = basl[kod]
        if kod == "TBDY":
            e(f"  {kod:<9} bent basligi={len(bas)}  (ondalikli yapi; yutulma testi uygulanmaz)")
            continue
        gecersiz = [b for b in bas if not b["siki"] and not b["onek"]]
        numaralar = sorted({b["no"] for b in bas if b["siki"] and not b["onek"]})
        bosluk = [n for n in range(1, (max(numaralar) if numaralar else 0) + 1)
                  if n not in numaralar]
        e(f"  {kod:<9} siki={len([b for b in bas if b['siki']]):<4} "
          f"gevsek={len(bas):<4} madde={len(numaralar):<4} "
          f"eksik no={len(bosluk):<4} YUTULAN={len(gecersiz)}")
        for b in gecersiz:
            yutulan[kod].append(b)
            if a.ayrinti:
                e(f"            ! yutulan @ {b['konum']}: {b['ham']!r}")
    topyut = sum(len(v) for v in yutulan.values())
    e("  temiz: gevsek tarama ekstra baslik bulmadi." if not topyut
      else f"  ! toplam {topyut} baslik ureticinin regexine takilmamis.")

    e()
    e("[B] KOKEN KONTROLU  (cumle gercekten kayitli maddede mi? tum yerler)")
    dur = defaultdict(int)
    kaymalar, yaklasiklar = [], []
    yerler = {}  # cid -> {"maddeler": [...], "yontem": ..., "n": ...}
    for s in satirlar:
        kod, cid = s.get("kanun", ""), s.get("id", "")
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        if kod not in metinler or len(alinti) < 40:
            dur["atlandi"] += 1
            continue
        t = metinler[kod]
        konumlar = tum_konumlar(t, alinti)
        yontem = "tam"
        if not konumlar:
            oran, p = kapsanma(alinti, harita[kod])
            if oran >= a.esik_yaklasik and p >= 0:
                konumlar, yontem = [p], f"yaklasik({oran:.2f})"
                yaklasiklar.append((cid, kod, oran, alinti[:70]))
            else:
                dur["bulunamadi"] += 1
                yaklasiklar.append((cid, kod, oran, alinti[:70]))
                continue
        mds = []
        for p in konumlar:
            et = etiket(onceki_baslik(basl[kod], p))
            if et and et not in mds:
                mds.append(et)
        if not mds:
            dur["bulunamadi"] += 1
            continue
        yerler[cid] = {"maddeler": mds, "yontem": yontem, "n": len(konumlar)}
        if len(konumlar) > 1:
            dur["coklu"] += 1
        kayitli = str(s.get("madde", "")).strip()
        if kayitli in mds:
            dur["eslesti"] += 1
        else:
            dur["kaydi"] += 1
            kaymalar.append((cid, kod, kayitli, "/".join(mds), s.get("probe", ""), alinti[:80]))
    n_kontrol = dur["eslesti"] + dur["kaydi"]
    e(f"  kontrol edilebilen: {n_kontrol} | eslesti: {dur['eslesti']} | "
      f"KAYMIS: {dur['kaydi']} | bulunamadi: {dur['bulunamadi']} | atlandi: {dur['atlandi']}")
    e(f"  birden fazla yerde gecen cumle: {dur['coklu']}  "
      f"(bunlarda madde atfi tek degil; [C1] hepsini test eder)")
    for k in kaymalar[:25]:
        e(f"    #{k[0]:<5} {k[1]:<8} kayitli={k[2]:<9} gercek={k[3]:<12} {k[4]:<13} {k[5]}")

    e()
    e("[B2] TAM ESLESMEYEN CUMLELER  (v1'de 'bulunamadi' diyenler)")
    if not yaklasiklar:
        e("  yok.")
    else:
        e(f"  {len(yaklasiklar)} cumle ham metinde birebir bulunamadi. Beklenen sebep:")
        e("  uretecteki cumleler() '(Değişik: ...)' etiketlerini ve bastaki 'b)' /")
        e("  '(4)' isaretlerini SOKUYOR; kaynak_alinti bu yuzden ham metnin birebir")
        e("  alt dizisi olmayabilir. n-gram kapsanmasi bunu ayirt eder:")
        for cid, kod, oran, oz in sorted(yaklasiklar, key=lambda x: -x[2])[:20]:
            if oran >= a.esik_yaklasik:
                tani = "duzenleme artigi (zararsiz; konum n-gram ile bulundu)"
            elif oran >= 0.15:
                tani = "kismi ortusme - GOZ KONTROLU"
            else:
                tani = "GERCEKTEN YOK - incele"
            e(f"    #{cid:<5} {kod:<8} kapsanma={oran:.2f}  {tani}")
            if a.ayrinti:
                e(f"           {oz}")

    e()
    e("[C1] KAZARA-DOGRU TESTI - madde kaydirma  (P5_maddeshift)")
    kesin, n_c1, kontrol_c1 = [], 0, 0
    for s in satirlar:
        for tur, p in varyantlar(s):
            if tur != "P5_maddeshift" or len(p) < 2:
                continue
            n_c1 += 1
            cid = s.get("id", "")
            kaynak_no, hedef_no = p[0], p[1]
            y = yerler.get(cid)
            if not y:
                continue
            kontrol_c1 += 1
            if hedef_no in y["maddeler"]:
                kesin.append((cid, s.get("kanun", ""), kaynak_no, hedef_no,
                              "/".join(y["maddeler"]), "maddeshift",
                              " ".join((s.get("iddia") or "").split())[:100]))
    e(f"  P5_maddeshift iddiasi: {n_c1} | koken kontrolu yapilabilen: {kontrol_c1}")
    if not n_c1:
        e("  ! hala 0. CSV'de varyant etiketi hangi sutunda? (bkz. basliktaki sayac)")
    n_kesin_c1 = len(kesin)
    if n_kesin_c1:
        e(f"  ! {n_kesin_c1} iddiada kaydirma hedefi cumlenin GERCEK maddelerinden birine denk geliyor")
        e("    -> iddia aslinda DOGRU, altin etiket YANLIS. KESIN ALTIN HATASI.")
        for k in kesin[:25]:
            e(f"    #{k[0]:<5} {k[1]:<8} {k[2]} -> atif={k[3]} | cumlenin gercek maddesi={k[4]}")
            e(f"           {k[6]}")
    else:
        e("  temiz: hicbir kaydirma hedefi cumlenin gectigi maddelere denk gelmiyor.")

    e()
    e("[C2] KAZARA-DOGRU TESTI - belge degistirme  (P5_lawshuffle)")
    e("  Mantik: cumle hedef belgede de gecerse 'yanlis belgeye atif' iddiasi DOGRU olur.")
    lw, n_c2 = [], 0
    for s in satirlar:
        for tur, p in varyantlar(s):
            if tur != "P5_lawshuffle" or len(p) < 2:
                continue
            n_c2 += 1
            kaynak_k, hedef_k = p[0], p[1]
            if hedef_k not in harita:
                continue
            alinti = " ".join((s.get("kaynak_alinti") or "").split())
            if len(alinti) < 40:
                continue
            oran, poz = kapsanma(alinti, harita[hedef_k])
            lw.append((oran, s.get("id", ""), kaynak_k, hedef_k, poz,
                       " ".join((s.get("iddia") or "").split())[:100]))
    lw.sort(reverse=True)
    kesin_c2 = [x for x in lw if x[0] >= a.esik_kesin]
    suphe_c2 = [x for x in lw if a.esik_suphe <= x[0] < a.esik_kesin]
    e(f"  P5_lawshuffle iddiasi: {n_c2} | test edilen: {len(lw)}")
    e(f"  kapsanma >= {a.esik_kesin}: {len(kesin_c2)} (KESIN)  |  "
      f"{a.esik_suphe}-{a.esik_kesin}: {len(suphe_c2)} (SUPHELI)")
    for x in (kesin_c2 + suphe_c2)[:25]:
        et = etiket(onceki_baslik(basl.get(x[3], []), x[4])) if x[4] >= 0 else "?"
        e(f"    #{x[1]:<5} {x[2]}->{x[3]:<8} kapsanma={x[0]:.2f} hedefte madde={et}")
        e(f"           {x[5]}")
    if not (kesin_c2 or suphe_c2):
        e("  temiz: hicbir kaynak cumle hedef belgede kayda deger olcude gecmiyor.")
    if a.ayrinti and lw:
        e(f"  (kalibrasyon) en yuksek 10 kapsanma: "
          f"{', '.join(f'{x[0]:.2f}' for x in lw[:10])}")

    e()
    e("[C3] P2 ATIF BOZMA UYARISI  (nicelik testi mi, atif testi mi?)")
    p2_atif, n_c3 = [], 0
    for s in satirlar:
        for tur, p in varyantlar(s):
            if tur != "P2_swap" or not p:
                continue
            n_c3 += 1
            eski = p[0]
            if not eski.isdigit():
                continue
            alinti = " ".join((s.get("kaynak_alinti") or "").split())
            for m in re.finditer(rf"\b{re.escape(eski)}\b", alinti):
                cevre = kucuk(alinti[max(0, m.start() - 30):m.end() + 30])
                if ATIF.search(cevre):
                    p2_atif.append((s.get("id", ""), s.get("kanun", ""), eski,
                                    p[1] if len(p) > 1 else "?", alinti[max(0, m.start() - 40):m.end() + 40]))
                    break
    e(f"  P2_swap iddiasi: {n_c3} | atif baglaminda sayi saptirilmis: {len(p2_atif)}")
    if p2_atif:
        e("  Bunlarda altin etiket yine YANLIS'tir (hata degil) ama olculen sey")
        e("  'sayisal hafiza' degil 'capraz atif hafizasi'dir; P2 skoru kirlenir.")
        for k in p2_atif[:12]:
            e(f"    #{k[0]:<5} {k[1]:<8} {k[2]}->{k[3]}   ...{k[4]}...")
    else:
        e("  temiz.")

    e()
    e("[C4] P6 DEGISIKLIK DOGRULAMASI  (kayitli yil madde blogunda gercekten var mi?)")
    p6_hata, n_c4 = [], 0
    for s in satirlar:
        if s.get("probe") != "P6_guncellik":
            continue
        m = re.search(r"(\d{4})", s.get("degisiklik_notu") or "")
        kod, kayitli = s.get("kanun", ""), str(s.get("madde", "")).strip()
        if not m or kod not in metinler or not kayitli.isdigit():
            continue
        n_c4 += 1
        bas = basl[kod]
        blok = None
        for i, b in enumerate(bas):
            if not b["onek"] and str(b["no"]) == kayitli:
                son = bas[i + 1]["konum"] if i + 1 < len(bas) else len(metinler[kod])
                blok = metinler[kod][b["konum"]:son]
                break
        if blok is None:
            continue
        yillar = {y for _, y in re.findall(
            r"\((?:Değişik|Ek|Yeniden düzenleme|Mülga)[^)]{0,80}?(\d{1,2}/\d{1,2}/(\d{4}))[^)]*\)", blok)}
        if m.group(1) not in yillar:
            p6_hata.append((s.get("id", ""), kod, kayitli, m.group(1),
                            ",".join(sorted(yillar)) or "YOK", s.get("gold", ""),
                            " ".join((s.get("iddia") or "").split())[:100]))
    e(f"  P6 iddiasi (yil kayitli): {n_c4} | blokta dogrulanamayan: {len(p6_hata)}")
    if p6_hata:
        e("  ! Kayitli degisiklik yili madde blogunda bulunamadi. 'YIL yilinda degisiklik")
        e("    yapilmistir' (gold=DOGRU) ve 'hic degistirilmemistir' (gold=YANLIS) ciftinin")
        e("    IKISI DE bu yila dayanir; yil yanlissa iki iddianin altini da yanlistir.")
        for k in p6_hata[:20]:
            e(f"    #{k[0]:<5} {k[1]:<8} m.{k[2]:<4} kayitli yil={k[3]} blokta={k[4]} gold={k[5]}")
    else:
        e("  temiz: her P6 iddiasinin yili kendi madde blogunda dogrulandi.")

    e()
    e("[D] YAPISAL MADDE UYARISI  (Amac/Kapsam/Dayanak/Tanimlar)")
    supheli = defaultdict(int)
    for s in satirlar:
        kod, kayitli = s.get("kanun", ""), str(s.get("madde", "")).strip()
        if kod == "TBDY" or not kayitli.isdigit():
            continue
        if int(kayitli) <= 4 and s.get("probe") in ("P1_dogrudan", "P5_capraz", "P2_sayisal"):
            supheli[(kod, kayitli)] += 1
    if supheli:
        e("  [B] bu cumlelerin gercekten bu bloklarda oldugunu dogruladi; sorun etiket")
        e("  degil ICERIK: tanim/amac cumleleri belgeler arasi tekrar eder, bu yuzden")
        e("  P5_lawshuffle'da kazara-dogru riski en yuksek olan satirlar bunlardir.")
        for (kod, no), n in sorted(supheli.items(), key=lambda x: -x[1]):
            e(f"    {kod:<9} madde {no:<4} -> {n} iddia")
    else:
        e("  temiz.")

    e()
    e("[E] KARAR")
    toplam_hata = n_kesin_c1 + len(kesin_c2) + len(p6_hata)
    if toplam_hata:
        e(f"  {toplam_hata} KESIN altin hatasi (modelsiz, deterministik, tam kapsam):")
        e(f"    maddeshift {n_kesin_c1} + lawshuffle {len(kesin_c2)} + P6 yil {len(p6_hata)}")
        e(f"    hata orani: %{100.0 * toplam_hata / max(len(satirlar), 1):.1f} (tum sette)")
        e("  Karsilastirma: model konsensusu 73 satir isaretleyip beklenen ~3 hata veriyordu;")
        e("  bu katman 0 uzman-dakikasi harcayarak tam kapsam veriyor.")
    if suphe_c2:
        e(f"  + {len(suphe_c2)} supheli satir (kapsanma {a.esik_suphe}-{a.esik_kesin}); goz kontrolu gerek.")
    if p2_atif:
        e(f"  + {len(p2_atif)} P2 satiri atif bozuyor (altin dogru, olcum kirli).")
    if dur["kaydi"]:
        e(f"  {dur['kaydi']} iddianin madde etiketi kaynak metinle uyusmuyor.")
    if not (toplam_hata or suphe_c2 or dur["kaydi"] or topyut):
        e("  Kaynak-kimlik VE kazara-dogruluk katmanlari temiz.")
        e("  Kalan altin hatasi anlamsal duzeydedir; onu ancak uzman denetimi bulur.")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\nyazildi: {a.out}")

    if kesin or kesin_c2 or suphe_c2 or kaymalar or p6_hata or p2_atif:
        os.makedirs(os.path.dirname(a.hata_csv) or ".", exist_ok=True)
        with open(a.hata_csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "kanun", "tur", "detay", "skor", "ozet"])
            for k in kesin:
                w.writerow([k[0], k[1], "KESIN_ALTIN_HATASI_maddeshift",
                            f"atif={k[3]} gercek={k[4]}", "1.00", k[6]])
            for x in kesin_c2:
                w.writerow([x[1], x[2], "KESIN_ALTIN_HATASI_lawshuffle",
                            f"hedef={x[3]}", f"{x[0]:.2f}", x[5]])
            for x in suphe_c2:
                w.writerow([x[1], x[2], "SUPHELI_lawshuffle",
                            f"hedef={x[3]}", f"{x[0]:.2f}", x[5]])
            for k in p6_hata:
                w.writerow([k[0], k[1], "KESIN_ALTIN_HATASI_P6_yil",
                            f"kayitli yil={k[3]} blokta={k[4]}", "1.00", k[6]])
            for k in kaymalar:
                w.writerow([k[0], k[1], "MADDE_ETIKETI_KAYMIS",
                            f"kayitli={k[2]} gercek={k[3]}", "", k[5]])
            for k in p2_atif:
                w.writerow([k[0], k[1], "KALITE_P2_atif_bozuldu",
                            f"{k[2]}->{k[3]}", "", k[4]])
        print(f"yazildi: {a.hata_csv}")


if __name__ == "__main__":
    main()
