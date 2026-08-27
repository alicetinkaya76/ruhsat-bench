# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F5 — R3: KURAL TABANLI BASELINE  (LLM YOK)

NE OLCER
--------
"Mevzuat metni elde varken, iddiayi dogrulamak icin dil modeline gerek
var mi?" Deterministik bir atif-cozme + metin-arama sistemi, ayni 473
iddiada ayni etiketleri uretir. Kapali kitap LLM sonuclari bunun karsisinda
bir MIMARI ALT SINIRI olarak okunur.

KORLUK SARTI (EK-4 madde 6)
---------------------------
Bu betik CSV'den YALNIZCA `id` ve `iddia` sutunlarini okur. `probe`,
`gold`, `kanun`, `madde`, `uretim_sablonu`, `degisiklik_notu` ve
`kaynak_alinti` sutunlarina ERISMEZ; kosu basinda assert edilir.
Puanlama f4_skor.py tarafindan ayrica yapilir.

Tek istisna: --tani modu. O modda altin etiketler SADECE teshis tablosu
basmak icin okunur, karar uretiminden SONRA. Karar fonksiyonu altin
gormez.

KARAR KURALI (EK-4 madde 9'da kosudan once sabitlendi)
------------------------------------------------------
  1. Yil kaliplari:
       "<madde>de YYYY yilinda degisiklik yapilmistir"
            -> DOGRU  <=>  YYYY in birim.degisiklik_yillari
       "<madde> ... hic degistirilmemistir"
            -> DOGRU  <=>  birim.degisiklik_yillari bos
       "YYYY yilinda kabul edilmistir / yayimlanmistir / yururluge girmistir"
            -> DOGRU  <=>  YYYY == belge meta verisindeki kabul yili
               (META VERI TUREVLI — EK-4 madde 8, ayri raporlanir)
  2. Aksi halde icerik varligi:
       iddianin ilk " gore "sinden sonraki kismi, atif cozulen birimde
       (madde duzeyi) ya da belgenin tamaminda (belge duzeyi) aranir.
       Bulunursa DOGRU, bulunmazsa YANLIS.

  Madde duzeyinde atifta BELGEYE DUSULMEZ. Dusulseydi P5_maddeshift
  maddelerinde icerik baska maddede bulunur ve YANLIS olan iddia DOGRU
  cikardi.

CIKTI
-----
f4_api.py ile AYNI JSONL semasi. f4_skor.py hicbir degisiklik olmadan
puanlar. Kacinma yoktur: E1 ve E2 ayni karari alir, kapsam 1.00.

KULLANIM
--------
    python -u scripts\\kural_taban.py --tani
    python -u scripts\\kural_taban.py --out sonuclar\\r3_kural.jsonl
    python scripts\\f4_skor.py --jsonl sonuclar\\r3_kural.jsonl
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import random
import re
import sys
import time
import unicodedata

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

# ---------------------------------------------------------- STDOUT KODLAMA
# Python, stdout bir KONSOL ise konsolun kod sayfasini kullanir; BORUYA veya
# DOSYAYA yaziliyorsa yerel ANSI kod sayfasina duser (bu makinede cp1252).
# cp1252'de ı, ğ, ş ve "→" yoktur. Bu yuzden betik konsolda calisirken
# sorunsuz, `| Select-String` veya `> dosya.txt` ile CALISIRKEN COKER —
# yani tam olarak sonuclari kaydederken. Asagidaki iki satir bunu keser.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                       # noqa: BLE001
        pass

try:
    import uret_iddia_v3_6 as UR
    from atif_coz import atif
except Exception as exc:                                    # noqa: BLE001
    print(f"! import hatasi: {exc}")
    sys.exit(1)

IZINLI_SUTUN = {"id", "iddia"}

SERH = re.compile(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]{0,140}\)")
TIRNAK = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}

YIL_DEGISIKLIK = re.compile(r"(\d{4})\s*yılında\s+değişiklik\s+yapılmıştır")
HIC_DEGISMEDI = re.compile(r"hiç\s+değiştirilmemiştir")
YIL_KABUL = re.compile(r"(\d{4})\s*yılında\s+(?:kabul\s+edilmiştir"
                       r"|Resmî\s+Gazete'?de\s+yayımlanmıştır)")
YIL_YURURLUK = re.compile(r"(\d{4})\s*tarihinde\s+yürürlüğe\s+girmiştir")
GORE = re.compile(r"\sgöre\s")


def anahtar(t):
    """Karsilastirma anahtari.

    UNICODE TUZAGI (olculdu): PDF metninde "İ" bazen ayrisik saklanir
    ("I" + U+0307 birlesik nokta). Iddia uretilirken kucult() bunu "i"ye
    cevirdiginden iki taraf esitlenmez. Ayrica Python'da "İ".lower()
    "i" + U+0307 verir — Turkce I sorununun Unicode hali.

    Cozum sirasi ONEMLI: once NFC (o+U+0308 -> ö gibi ayrisik harfleri
    birlestirir), sonra lower(), sonra kalan U+0307'yi at. Yalnizca nokta
    isareti atilir; ö/ü/ç/ğ/ş isaretlerine dokunulmaz, cunku NFC onlari
    zaten birlestirmistir ve atmak anlami degistirirdi.
    """
    t = unicodedata.normalize("NFC", t)
    for a, b in TIRNAK.items():
        t = t.replace(a, b)
    t = SERH.sub(" ", t).lower().replace("\u0307", "")
    return re.sub(r"\s+", "", t)


# --------------------------------------------------------------- OZ TEST
# NEDEN VAR: gelistirme sirasinda GORE kalibi r"\s göre\s" yazilmisti —
# \s ARTI literal bosluk, yani "gore"den once IKI bosluk ariyordu. Hicbir
# maddede eslesmedi ve 334 iddia sessizce "atif cozulemedi"ye dustu. Betik
# CALISTI, sadece YANLIS calisti. Asagidaki kontrol bu sinifi yakalar:
# her kalip, bilinen bir ornekte eslesmek ZORUNDA.
OZ_TEST = [
    (YIL_DEGISIKLIK, "3194 sayılı Kanun'un 38. maddesinde 1989 yılında "
                     "değişiklik yapılmıştır.", "1989"),
    (HIC_DEGISMEDI,  "3194 sayılı Kanun'un 3. maddesi, ilk yayımlandığı 1985 "
                     "yılından bu yana hiç değiştirilmemiştir.", None),
    (YIL_KABUL,      "3194 sayılı İmar Kanunu 2003 yılında kabul edilmiştir.", "2003"),
    (YIL_KABUL,      "Yapı Denetimi Uygulama Yönetmeliği 2003 yılında Resmî "
                     "Gazete'de yayımlanmıştır.", "2003"),
    (YIL_YURURLUK,   "TBDY 2018, 1 Ocak 2019 tarihinde yürürlüğe girmiştir.", "2019"),
    (GORE,           "Yapı Denetimi Uygulama Yönetmeliği'nin 26. maddesine göre "
                     "her yıl 1 Ocak tarihinden geçerli olmak üzere yayınlanır.", None),
    (SERH,           "ilgililerin (Değişik ibare:RG-5/2/2013-28550) Merkez Yapı "
                     "Denetim Komisyonuna başvurarak", None),
]


def oz_test():
    hata = 0
    for kalip, ornek, grup in OZ_TEST:
        m = kalip.search(ornek)
        if not m or (grup is not None and m.group(1) != grup):
            print(f"! OZ TEST BASARISIZ: {kalip.pattern!r}")
            print(f"    ornekte eslesmedi: {ornek[:70]}")
            hata += 1
    # icerik() gercekten kirpiyor mu
    ic = icerik("TBDY 2018'e göre perdeler, planda uzun kenarının kalınlığına "
                "oranı en az dört olan elemanlardır.")
    if ic.startswith("TBDY"):
        print("! OZ TEST BASARISIZ: icerik() atif onekini kirpmadi.")
        hata += 1
    if hata:
        print(f"\n! {hata} oz test hatasi. Karar kurallari bozuk; KOSU YAPILMADI.")
        sys.exit(3)
    print(f"oz test: {len(OZ_TEST) + 1}/{len(OZ_TEST) + 1} kalip dogrulandi")



def icerik(iddia):
    """Iddianin ilk ' gore 'sinden sonraki bolumu = one surulen hukum."""
    m = GORE.search(iddia)
    g = iddia[m.end():] if m else iddia
    return g.strip().rstrip(".").strip()


def karar_ver(iddia, korpus, belge_a, kabul_yili, esleme=None, esleme_belge=None):
    """ALTIN GORMEZ. (karar, gerekce) dondurur.

    esleme / esleme_belge: NEGATIF KONTROL icin atif->birim yonlendirmesini
    saptirir. None ise kimlik eslemesi (normal kosu)."""
    kanun, madde = atif(iddia)
    if kanun is None:
        return None, "atif cozulemedi"
    if madde is not None and esleme:
        kanun, madde = esleme.get((kanun, madde), (kanun, madde))
    elif madde is None and esleme_belge:
        kanun = esleme_belge.get(kanun, kanun)

    m = YIL_DEGISIKLIK.search(iddia)
    if m:
        b = korpus.get((kanun, madde))
        if b is None:
            return None, "birim yok"
        var = int(m.group(1)) in b["degisiklik_yillari"]
        return ("DOGRU" if var else "YANLIS"), f"serh yillari={b['degisiklik_yillari']}"

    if HIC_DEGISMEDI.search(iddia):
        b = korpus.get((kanun, madde))
        if b is None:
            return None, "birim yok"
        bos = not b["degisiklik_yillari"]
        return ("DOGRU" if bos else "YANLIS"), f"serh yillari={b['degisiklik_yillari']}"

    m = YIL_KABUL.search(iddia) or YIL_YURURLUK.search(iddia)
    if m:
        gercek = kabul_yili.get(kanun)
        # yururluk kalibinda kabul yilindan sonraki yil da kabul edilir
        kabul_edilen = {gercek, gercek + 1} if YIL_YURURLUK.search(iddia) else {gercek}
        return ("DOGRU" if int(m.group(1)) in kabul_edilen else "YANLIS"), \
               f"meta veri kabul={gercek} [META VERI TUREVLI]"

    ic = anahtar(icerik(iddia))
    if not ic:
        return None, "icerik bos"
    if madde is not None:
        b = korpus.get((kanun, madde))
        if b is None:
            return None, "birim yok"
        return ("DOGRU" if ic in b["_a"] else "YANLIS"), f"madde duzeyi {kanun}/{madde}"
    hedef = belge_a.get(kanun)
    if hedef is None:
        return None, "belge yok"
    return ("DOGRU" if ic in hedef else "YANLIS"), f"belge duzeyi {kanun}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--korpus", default="data/korpus/korpus.jsonl")
    ap.add_argument("--belge", default="data/korpus/belge_tam.jsonl")
    ap.add_argument("--out", default="sonuclar/r3_kural.jsonl")
    ap.add_argument("--model-adi", default=None,
                    help="JSONL model alani; karistirmada otomatik ayrilir")
    ap.add_argument("--tani", action="store_true",
                    help="altin etiketlere karsi teshis tablosu bas (kararlardan SONRA)")
    ap.add_argument("--karistir", action="store_true",
                    help="NEGATIF KONTROL: atif->birim eslemesini kanun ici permute et. "
                         "Duzenek sizdirmiyorsa dogruluk sans duzeyine dusmeli. "
                         "Yuksek kalirsa R3'un HICBIR sayisi kullanilamaz.")
    ap.add_argument("--tohum", type=int, default=20260802,
                    help="karistirma tohumu (yeniden uretilebilirlik)")
    a = ap.parse_args()

    # ---------------------------------------------------- KORLUK KONTROLU
    oz_test()
    with open(a.claims, encoding="utf-8-sig") as fh:
        ham = list(csv.DictReader(fh))
    iddialar = [{"id": r["id"], "iddia": r["iddia"]} for r in ham]
    for r in iddialar:
        assert set(r) <= IZINLI_SUTUN, f"KORLUK IHLALI: {set(r) - IZINLI_SUTUN}"
    print(f"korluk kontrolu: karar uretimine giden sutunlar = {sorted(IZINLI_SUTUN)}")

    korpus = {}
    with open(a.korpus, encoding="utf-8-sig") as fh:
        for s in fh:
            if not s.strip():
                continue
            v = json.loads(s)
            v["_a"] = anahtar(v["metin"])
            korpus[(v["kanun"], v["birim"])] = v
    belge_a = {}
    with open(a.belge, encoding="utf-8-sig") as fh:
        for s in fh:
            if not s.strip():
                continue
            v = json.loads(s)
            belge_a[v["kanun"]] = anahtar(v["metin"])
    kabul = {k: m["kabul"] for k, m in UR.LAWS.items()}
    print(f"korpus: {len(korpus)} birim, {len(belge_a)} belge")

    betik_sha = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    kural_sha = hashlib.sha256(
        (SERH.pattern + YIL_DEGISIKLIK.pattern + HIC_DEGISMEDI.pattern
         + YIL_KABUL.pattern + YIL_YURURLUK.pattern + GORE.pattern).encode()).hexdigest()

    t0 = time.time()
    esleme = esleme_belge = None
    if a.karistir:
        rnd = random.Random(a.tohum)
        esleme = {}
        gruplar = collections.defaultdict(list)
        for (k, m) in korpus:
            gruplar[k].append(m)
        sabit = 0
        for k, ms in gruplar.items():
            hedef = list(ms)
            for _ in range(20):                    # sabit noktayi azalt
                rnd.shuffle(hedef)
                if len(ms) < 2 or all(x != y for x, y in zip(ms, hedef)):
                    break
            for x, y in zip(ms, hedef):
                esleme[(k, x)] = (k, y)
                sabit += (x == y)
        kanunlar = sorted(belge_a)
        hedefk = list(kanunlar)
        for _ in range(20):
            rnd.shuffle(hedefk)
            if all(x != y for x, y in zip(kanunlar, hedefk)):
                break
        esleme_belge = dict(zip(kanunlar, hedefk))
        print(f"\n!! NEGATIF KONTROL AKTIF (tohum={a.tohum})")
        print(f"   madde eslemesi permute edildi: {len(esleme)} birim, "
              f"sabit nokta {sabit}")
        print(f"   belge eslemesi: {esleme_belge}")
        print("   BEKLENTI: dogruluk sans duzeyine dusmeli. Yuksek kalirsa")
        print("   kural altin etiketi korpustan degil baska bir yerden aliyor.")

    kararlar, gerekceler = {}, {}
    for r in iddialar:
        k, g = karar_ver(r["iddia"], korpus, belge_a, kabul, esleme, esleme_belge)
        kararlar[r["id"]] = k
        gerekceler[r["id"]] = g
    sure = time.time() - t0

    model_adi = a.model_adi or ("kural_taban_r3_KARISTIRILMIS" if a.karistir
                                else "kural_taban_r3")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    n = 0
    with open(a.out, "w", encoding="utf-8") as fh:
        for kosul in ("E1", "E2"):
            for r in iddialar:
                k = kararlar[r["id"]]
                fh.write(json.dumps({
                    "model": model_adi, "kosul": kosul, "varyant": "A",
                    "id": r["id"], "karar": k, "ham_etiket": k,
                    "guven": 100 if k else None,
                    "durum": "tamam" if k else "ayristirilamadi",
                    "konum": 0, "tohum": 0,
                    "ham": f"{k}|100" if k else "",
                    "gerekce": gerekceler[r["id"]],
                    "betik_sha256": betik_sha, "kural_sha256": kural_sha,
                    "dusunme_token": 0, "bitis_sebebi": "deterministik",
                    "sure_sn": 0.0}, ensure_ascii=False) + "\n")
                n += 1

    print(f"\nyazildi: {a.out}  ({n} satir, {sure:.2f} sn)")
    print(f"  betik_sha256 = {betik_sha[:32]}...")
    print(f"  kural_sha256 = {kural_sha[:32]}...")
    d = collections.Counter(kararlar.values())
    print(f"  karar dagilimi: {dict(d)}")
    print(f"  kapsam: {sum(1 for v in kararlar.values() if v)/len(kararlar):.4f}"
          f"   (kacinma yok — EK-4 madde 6)")

    if not a.tani:
        print("\nPuanlama:")
        print(f"  python scripts/f4_skor.py --jsonl {a.out}")
        return

    # ------------------------------------------- TESHIS (kararlardan SONRA)
    print("\n" + "=" * 76)
    print("TESHIS — altin etiketler YALNIZCA burada okundu, kararlar uretildikten sonra")
    print("=" * 76)
    altin = {r["id"]: (r["gold"], r["probe"], r["uretim_sablonu"]) for r in ham}
    ok = collections.Counter(); top = collections.Counter()
    hatalar = collections.defaultdict(list)
    for i, k in kararlar.items():
        g, p, s = altin[i]
        top[p] += 1
        if k == g:
            ok[p] += 1
        else:
            hatalar[p].append((i, s, g, k, gerekceler[i]))
    print(f"    {'prob':<18}{'gecen':>10}{'oran':>9}")
    for p in sorted(top):
        print(f"    {p:<18}{f'{ok[p]}/{top[p]}':>10}{ok[p]/top[p]:>9.4f}")
    print(f"    {'TOPLAM':<18}{f'{sum(ok.values())}/{sum(top.values())}':>10}"
          f"{sum(ok.values())/sum(top.values()):>9.4f}")

    print("\n  alt sablon kirilimi (yalnizca hatali olanlar):")
    sb_ok = collections.Counter(); sb_top = collections.Counter()
    for i, k in kararlar.items():
        g, p, s = altin[i]
        t = s.split("(")[0]
        sb_top[t] += 1; sb_ok[t] += (k == g)
    for t in sorted(sb_top):
        if sb_ok[t] < sb_top[t]:
            print(f"    {t:<24}{sb_ok[t]:>4}/{sb_top[t]:<5}{sb_ok[t]/sb_top[t]:>8.4f}")

    for p in sorted(hatalar):
        print(f"\n  --- {p} ({len(hatalar[p])} hata) ---")
        for i, s, g, k, ger in hatalar[p][:4]:
            print(f"    id={i} {s} altin={g} kural={k}")
            print(f"       {ger}")


if __name__ == "__main__":
    main()
