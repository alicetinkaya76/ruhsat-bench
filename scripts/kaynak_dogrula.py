# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F3 — kaynak-kimlik dogrulayici (MODEL KULLANMAZ).

Neden: model-konsensus on-taramasi altin hatasini bulamiyor (oy verenlerin en
iyisi J=0.14). Ama altin etiket hatasinin BUYUK cogunlugu model bilgisi
gerektirmez: "bu cumle gercekten bu maddede mi geciyor?" sorusu kaynak metin
uzerinde deterministik olarak yanitlanir.

Ozellikle P5_capraz/maddeshift ailesi (setin ~%26'si) tek bir varsayima dayanir:
cumlenin kayitli madde numarasi DOGRUDUR. Bu varsayim bozulursa, ureticinin
"yanlis maddeye atif" diye urettigi iddia kazara DOGRU olur ve altin etiket
YANLIS kalir -> sessiz altin hatasi.

Uc kontrol:
  [A] BASLIK TARAMASI  siki regex (ureticinin gordugu) vs gevsek regex (gercekte
      olan). Gevsek bulup siki bulamadigi her baslik, bir maddenin bir oncekine
      YUTULDUGU yerdir; o noktadan sonraki tum cumlelerin madde etiketi kayar.
  [B] KOKEN KONTROLU   her iddianin kaynak cumlesi ham metinde aranir; cumleden
      onceki son gercek baslik = cumlenin GERCEK maddesi. CSV'deki madde ile
      karsilastirilir.
  [C] KAZARA-DOGRU TESTI  P5_maddeshift(A->B) iddialarinda, cumlenin gercek
      maddesi B ise iddia dogrudur ama altin YANLIS'tir -> KESIN ALTIN HATASI.

Kullanim:
    python scripts/kaynak_dogrula.py
    python scripts/kaynak_dogrula.py --pdf-dir data/kaynak_pdf --ayrinti
"""
import argparse
import csv
import os
import re
import sys
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
YAPISAL = ("Amaç", "Kapsam", "Dayanak", "Tanımlar", "Kısaltmalar",
           "Yürürlük", "Yürütme")


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
    """(konum, no, siki_mi, ham) listesi; gevsek tarama esas alinir."""
    siki_konum = {m.start() for m in SIKI.finditer(t)}
    out = []
    for m in GEVSEK.finditer(t):
        onek = (m.group(1) or "").strip()
        no = int(m.group(2))
        out.append({"konum": m.start(), "no": no, "onek": onek,
                    "siki": m.start() in siki_konum, "ham": t[m.start():m.start() + 42]})
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/iddialar/uretilen_iddialar_v1.csv")
    ap.add_argument("--pdf-dir", default="data/kaynak_pdf")
    ap.add_argument("--txt-dir", default="", help="test icin: PDF yerine <kod>.txt oku")
    ap.add_argument("--ayrinti", action="store_true")
    ap.add_argument("--out", default="sonuclar/kaynak_dogrulama.txt")
    ap.add_argument("--hata-csv", default="sonuclar/altin_hatalari.csv")
    a = ap.parse_args()

    with open(a.csv, encoding="utf-8-sig") as fh:
        satirlar = list(csv.DictReader(fh))

    L = []

    def e(s=""):
        L.append(s)
        print(s)

    e("=" * 78)
    e("RUHSAT-Bench — KAYNAK KIMLIK DOGRULAMA (deterministik, modelsiz)")
    e("=" * 78)
    e(f"iddia sayisi: {len(satirlar)}")

    metinler, basl = {}, {}
    kodlar = sorted({s.get("kanun", "") for s in satirlar if s.get("kanun")})
    for kod in kodlar:
        if kod not in LAWS:
            e(f"  ! bilinmeyen kaynak kodu: {kod}")
            continue
        t = metin_yukle(kod, a.pdf_dir, a.txt_dir)
        if t is None:
            e(f"  ! kaynak dosya bulunamadi: {os.path.join(a.pdf_dir, LAWS[kod])}")
            continue
        metinler[kod] = t
        basl[kod] = bent_basliklari(t) if kod == "TBDY" else basliklar(t)

    e()
    e("[A] BASLIK TARAMASI  (yutulan madde tespiti)")
    yutulan = defaultdict(list)
    for kod in sorted(metinler):
        bas = basl[kod]
        if kod == "TBDY":
            e(f"  {kod:<9} bent basligi={len(bas)}  (ondalikli bent yapisi; yutulma testi uygulanmaz)")
            continue
        gecersiz = [b for b in bas if not b["siki"] and not b["onek"]]
        numaralar = sorted({b["no"] for b in bas if b["siki"] and not b["onek"]})
        bosluk = [n for n in range(1, (max(numaralar) if numaralar else 0) + 1)
                  if n not in numaralar]
        e(f"  {kod:<9} siki baslik={len([b for b in bas if b['siki']]):<4} "
          f"gevsek={len(bas):<4} bulunan madde={len(numaralar):<4} "
          f"eksik no={len(bosluk):<4} YUTULAN={len(gecersiz)}")
        if bosluk and a.ayrinti:
            e(f"            eksik: {bosluk[:25]}{' ...' if len(bosluk) > 25 else ''}")
        for b in gecersiz:
            yutulan[kod].append(b)
            if a.ayrinti:
                e(f"            ! yutulan baslik @ {b['konum']}: {b['ham']!r}")
    topyut = sum(len(v) for v in yutulan.values())
    if topyut:
        e(f"  ! toplam {topyut} baslik ureticinin regexine takilmamis.")
        e(f"    Bu basliklardan SONRAKI her cumle bir onceki maddenin blogunda")
        e(f"    sayilmis demektir; madde etiketi kaymis olabilir.")
    else:
        e("  temiz: gevsek tarama ekstra baslik bulmadi.")

    e()
    e("[B] KOKEN KONTROLU  (cumle gercekten kayitli maddede mi?)")
    dur = {"eslesti": 0, "kaydi": 0, "bulunamadi": 0, "coklu": 0, "atlandi": 0}
    kaymalar = []
    gercek_madde = {}
    for s in satirlar:
        kod, cid = s.get("kanun", ""), s.get("id", "")
        alinti = " ".join((s.get("kaynak_alinti") or "").split())
        if kod not in metinler or len(alinti) < 40:
            dur["atlandi"] += 1
            continue
        t = metinler[kod]
        p = t.find(alinti)
        if p < 0:
            dur["bulunamadi"] += 1
            continue
        if t.find(alinti, p + 1) >= 0:
            dur["coklu"] += 1
        b = onceki_baslik(basl[kod], p)
        if not b:
            dur["bulunamadi"] += 1
            continue
        gercek = f"{b['onek']} {b['no']}".strip() if b["onek"] else str(b["no"])
        gercek_madde[cid] = gercek
        kayitli = str(s.get("madde", "")).strip()
        if gercek == kayitli:
            dur["eslesti"] += 1
        else:
            dur["kaydi"] += 1
            kaymalar.append((cid, kod, kayitli, gercek, s.get("probe", ""), alinti[:80]))
    n_kontrol = dur["eslesti"] + dur["kaydi"]
    e(f"  kontrol edilebilen: {n_kontrol} | eslesti: {dur['eslesti']} | "
      f"KAYMIS: {dur['kaydi']} | metinde bulunamadi: {dur['bulunamadi']} | atlandi: {dur['atlandi']}")
    if dur["coklu"]:
        e(f"  {dur['coklu']} cumle belgede birden fazla yerde geciyor (madde atfi belirsiz).")
    if n_kontrol:
        e(f"  kayma orani: %{100.0 * dur['kaydi'] / n_kontrol:.1f}")
    for k in kaymalar[:25] if a.ayrinti else kaymalar[:8]:
        e(f"    #{k[0]:<5} {k[1]:<8} kayitli={k[2]:<9} gercek={k[3]:<9} {k[4]:<13} {k[5]}")
    if len(kaymalar) > (25 if a.ayrinti else 8):
        e(f"    ... (+{len(kaymalar) - (25 if a.ayrinti else 8)})")

    e()
    e("[C] KAZARA-DOGRU TESTI  (P5 madde-kaydirma hedefi gercek maddeye denk mi?)")
    kesin_hata = []
    n_p5 = 0
    for s in satirlar:
        not_ = s.get("degisiklik_notu") or ""
        m = re.search(r"P5_maddeshift\((\d+)\s*[→>-]+\s*(\d+)\)", not_)
        if not m:
            continue
        n_p5 += 1
        cid = s.get("id", "")
        hedef = m.group(2)
        gercek = gercek_madde.get(cid)
        if gercek is None:
            continue
        if str(gercek) == str(hedef):
            kesin_hata.append((cid, s.get("kanun", ""), m.group(1), hedef, gercek,
                               " ".join((s.get("iddia") or "").split())[:90]))
    e(f"  P5_maddeshift iddiasi: {n_p5} | koken kontrolu yapilabilen: "
      f"{sum(1 for s in satirlar if s.get('id') in gercek_madde and 'P5_maddeshift' in (s.get('degisiklik_notu') or ''))}")
    if kesin_hata:
        e(f"  ! {len(kesin_hata)} iddiada kaydirma hedefi cumlenin GERCEK maddesine denk geliyor.")
        e(f"    Bu iddialar aslinda DOGRU; altin etiket YANLIS. KESIN ALTIN HATASI.")
        for k in kesin_hata[:20]:
            e(f"    #{k[0]:<5} {k[1]:<8} kayitli={k[2]} -> atif={k[3]} | gercek madde={k[4]}")
            e(f"           {k[5]}")
    else:
        e("  temiz: hicbir kaydirma hedefi gercek maddeye denk gelmiyor.")

    e()
    e("[D] YAPISAL MADDE UYARISI  (Amac/Kapsam/Dayanak/Tanimlar'dan hukum cikmaz)")
    supheli = defaultdict(int)
    for s in satirlar:
        kod, kayitli = s.get("kanun", ""), str(s.get("madde", "")).strip()
        if kod == "TBDY" or not kayitli.isdigit():
            continue
        if int(kayitli) <= 4 and s.get("probe") in ("P1_dogrudan", "P5_capraz", "P2_sayisal"):
            supheli[(kod, kayitli)] += 1
    if supheli:
        e("  Bu maddeler tipik olarak Amac/Kapsam/Dayanak/Tanimlar'dir; buradan")
        e("  cikan 'hukum' cumleleri buyuk olasilikla sonraki maddelerden yutulmustur:")
        for (kod, no), n in sorted(supheli.items(), key=lambda x: -x[1]):
            e(f"    {kod:<9} madde {no:<4} -> {n} iddia")
    else:
        e("  temiz.")

    e()
    e("[E] KARAR")
    if kesin_hata:
        e(f"  {len(kesin_hata)} KESIN altin hatasi bulundu (modelsiz, deterministik).")
        e(f"  Karsilastirma: model konsensusu 73 satir isaretleyip beklenen ~3 hata veriyordu.")
    if dur["kaydi"]:
        e(f"  {dur['kaydi']} iddianin madde etiketi kaynak metinle uyusmuyor. P5/P1 aileleri")
        e(f"  madde etiketinin dogrulugunu VARSAYAR; bunlar duzeltilmeden F4 calistirmayin.")
    if topyut:
        e(f"  Kok neden: ureticinin baslik regexi {topyut} basligi kaciriyor")
        e(f"  (uret_iddia_v3_6.py -> maddeler(): '(?:Madde|MADDE)\\s+\\d+\\s*[dash]').")
        e(f"  Dash'siz ('MADDE 5 (1) ...') ve noktali ('MADDE 5.') basliklar eklenmeli.")
    if not (kesin_hata or dur["kaydi"] or topyut):
        e("  Kaynak-kimlik katmani temiz. Altin hatasi varsa anlamsal duzeydedir;")
        e("  onu ancak uzman denetimi bulur.")

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"\nyazildi: {a.out}")

    if kaymalar or kesin_hata:
        os.makedirs(os.path.dirname(a.hata_csv) or ".", exist_ok=True)
        with open(a.hata_csv, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "kanun", "tur", "kayitli_madde", "gercek_madde", "atif_hedefi", "probe", "ozet"])
            for k in kesin_hata:
                w.writerow([k[0], k[1], "KESIN_ALTIN_HATASI", k[2], k[4], k[3], "P5_capraz", k[5]])
            for k in kaymalar:
                w.writerow([k[0], k[1], "MADDE_ETIKETI_KAYMIS", k[2], k[3], "", k[4], k[5]])
        print(f"yazildi: {a.hata_csv}")


if __name__ == "__main__":
    main()
