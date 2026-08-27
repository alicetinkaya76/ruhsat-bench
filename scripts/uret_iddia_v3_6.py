# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F2 v3 — resmî mevzuat PDF'lerinden aday iddia üretimi.
v3 değişiklikleri (v2 örnek çıktısındaki kirliliğe göre kalibre edildi):
- Değişiklik-notu/dipnot cümleleri artık hüküm sayılmıyor (ibaresi/değiştirilmiştir/AYM kararı vb.)
- OCR tek-harf kopmaları onarılıyor ("b ilgileri"→"bilgileri"); dipnot artıklı cümleler eleniyor
- Cümle bölme yalnızca nokta ile (";" fragmanları bitti); büyük harfle başlama + fiille bitme şartı
- P2 tarih ve parantez-içi sayıları saptırmıyor
- P5 madde-kaydırma hedefi kanunun GERÇEK maddelerinden seçiliyor (daha aldatıcı)
- Aynı kaynak cümleden tek DOĞRU varyant (verbatim VEYA atıflı) ve tek P5 varyantı seçiliyor

Kullanım:  python scripts/uret_iddia.py --hedef 1500   |   --selftest
Girdi:  data/kaynak_pdf/*.pdf   Çıktı: data/iddialar/uretilen_iddialar_v1.csv (durum=ONAY_BEKLIYOR)
"""
import argparse, csv, random, re, os, sys

random.seed(42)

LAWS = {
    "6331": {"dosya": "6331_isg_kanunu.pdf", "ad": "6331 sayılı İş Sağlığı ve Güvenliği Kanunu",
             "kisa": "6331 sayılı Kanun", "kabul": 2012, "alan": "ISG-6331",
             "tur": "kanun", "gore": "'a göre", "iyelik": "'un"},
    "4708": {"dosya": "4708_yapi_denetimi.pdf", "ad": "4708 sayılı Yapı Denetimi Hakkında Kanun",
             "kisa": "4708 sayılı Kanun", "kabul": 2001, "alan": "YapiDenetim-4708",
             "tur": "kanun", "gore": "'a göre", "iyelik": "'un"},
    "3194": {"dosya": "3194_imar_kanunu.pdf", "ad": "3194 sayılı İmar Kanunu",
             "kisa": "3194 sayılı Kanun", "kabul": 1985, "alan": "Imar-3194",
             "tur": "kanun", "gore": "'a göre", "iyelik": "'un"},
    "ISGRISK": {"dosya": "isg_risk_yonetmeligi.pdf",
             "ad": "İş Sağlığı ve Güvenliği Risk Değerlendirmesi Yönetmeliği",
             "kisa": "İSG Risk Değerlendirmesi Yönetmeliği", "kabul": 2012, "alan": "ISG-RiskYon",
             "tur": "yonetmelik", "gore": "'ne göre", "iyelik": "'nin"},
    "TBDY": {"dosya": "TBDY_2018.pdf",
             "ad": "Türkiye Bina Deprem Yönetmeliği (TBDY 2018)",
             "kisa": "TBDY 2018", "kabul": 2018, "alan": "Deprem-TBDY2018",
             "tur": "tbdy", "gore": "'e göre", "iyelik": "'in"},
    "YDUY": {"dosya": "yapi_denetim_uygulama_yon.pdf",
             "ad": "Yapı Denetimi Uygulama Yönetmeliği",
             "kisa": "Yapı Denetimi Uygulama Yönetmeliği", "kabul": 2008, "alan": "YapiDenetim-UygYon",
             "tur": "yonetmelik", "gore": "'ne göre", "iyelik": "'nin"},
}

SAYI_KELIME = {"iki": "dört", "üç": "beş", "dört": "iki", "beş": "üç",
               "altı": "dört", "yedi": "on", "sekiz": "altı", "dokuz": "yedi", "on": "yirmi",
               "onbeş": "otuz", "yirmi": "kırk", "otuz": "altmış", "kırk": "yirmi",
               "altmış": "otuz", "doksan": "kırkbeş"}
HUKUM_ANAHTAR = ["yükümlü", "zorunlu", "mecbur", "gerekir", "sayılır", "verilir", "uygulanır",
                 "yapılır", "ceza", "yasak", "muaf", "hükümsüz", "iptal", "men edil", "ister",
                 "gün", "yıl", "metrekare", "m2", "oran", "yüzde", "sınıf", "karşılanır"]
# Değişiklik tarihçesi / dipnot / karar cümlelerini dışla (bunlar hüküm değil)
KARA_LISTE = ["ibaresi", "şeklinde değiştirilmiş", "değiştirilmiştir", "yürürlükten kaldırılmış",
              "madde başlığı", "eklenmiştir", "Anayasa Mahkemesi", "sayılı Kararı", "iptal edilmiş",
              "sayılı Kanunun", "maddesiyle", "Kanun Hükmünde Kararname", "mülga", "Mülga",
              "Resmî Gazete", "yeniden düzenlen", "metne işlenmiş",
              "aşağıda", "Aşağıda", "yukarıda", "Yukarıda", "bu Bölümde", "bu bentte"]
FORMUL_ARTIK = re.compile(r"Denk\.|Tablo|Şekil|=|[νбраβγδλμθσΣΔ]|\bEK\s|(?:[A-Za-zÇĞİÖŞÜçğıöşü]\s){4,}")
TBDY_UYDURMA = ["Yıllık Deprem Dayanım Etiketi", "Bina Salınım Sertifikası",
                "Zorunlu Rezonans Testi Raporu", "Deprem Kimlik Plakası"]
KISA_ISTISNA = r"(?:o|ne|ve|de|da|ki|bu|şu|iş|ay|ek|el|ev|su|üç|on|en|az|ya)"
OCR_ONEK = re.compile(r"\b(?!" + KISA_ISTISNA + r"\b)[a-zçğıöşü]{1,2}\s(?=[a-zçğıöşü]{4,})")
OCR_ARTIK = re.compile(r"\b[a-zçğıöşü]{4,}\s(?!o\b)[a-zçğıöşü]\b")
FIIL_SON = re.compile(r"(r|z|ır|ir|ur|ür|mez|maz|dır|dir|tır|tir|tur|tür|lır|lir|nır|nir|ılır|ilir|"
                      r"ulur|ülür|nur|nür|edilir|olunur|anır|enir|dedir|tedir|ındadır|ndedir)\s*\.?\s*$")
UYDURMA_BELGELER = ["Ulusal Denetim Sicil Belgesi", "Yıllık Saha Uygunluk Karnesi",
                    "Dijital Şantiye Kayıt Sertifikası", "Mevzuat Uyum Plakası",
                    "Merkezi Ruhsat Doğrulama Kartı", "Zorunlu Teknik Beyan Defteri",
                    "Ulusal Yapı Güvenlik Rozeti", "Elektronik Fenni Mesuliyet Cüzdanı"]
UYDURMA_EYLEM = ["her yıl yenilemek", "her ay ilgili idareye ibraz etmek",
                 "şantiye girişine asmak", "altı ayda bir onaylatmak"]


def pdf_metin(path):
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


def normalize(t):
    t = t.replace("­", "")
    t = re.sub(r"-\n(?=[a-zçğıöşü])", "", t)
    t = re.sub(r"\s+", " ", t)
    # OCR tek-harf kopması onarımı: "b ilgileri"→"bilgileri", "K anunda"→"Kanunda", "ö ngörülen"→"öngörülen"
    # Tek başına anlamlı Türkçe kelime olan "o/O" hariç tutulur.
    t = re.sub(r"\b([bcçdfgğhıijklmnöprsştuüvyzBCÇDFGĞHİIJKLMNÖPRSŞTUÜVYZe])\s(?=[a-zçğıöşü]{2,}\b)", r"\1", t)
    for bozuk, dogru in [("herh angi", "herhangi"), ("hal lerde", "hallerde"), ("İma r", "İmar"),
                         ("v eilgili", "ve ilgili"), ("v e ", "ve "), ("il gili", "ilgili"),
                         ("yü kümlü", "yükümlü"), ("zo runlu", "zorunlu"),
                         ("artı rılır", "artırılır"), ("inti kal", "intikal"),
                         ("ücretl erini", "ücretlerini"), ("inşa at", "inşaat"),
                         ("başv uru", "başvuru"), ("düzenl enir", "düzenlenir")]:
        t = t.replace(bozuk, dogru)
    return t


def maddeler(t):
    out = {}
    for p in re.split(r"(?=(?:Madde|MADDE)\s+\d+\s*[–\-—])", t):
        m = re.match(r"(?:Madde|MADDE)\s+(\d+)\s*[–\-—]\s*(.*)", p, re.S)
        if not m:
            continue
        no, govde = int(m.group(1)), m.group(2).strip()
        if no in out:
            continue
        degisiklikler = re.findall(r"\((?:Değişik|Ek|Yeniden düzenleme)[^)]{0,80}?(\d{1,2}/\d{1,2}/(\d{4}))[^)]*\)", govde)
        out[no] = {"metin": govde[:4000], "degisiklik_yillari": sorted({int(y) for _, y in degisiklikler})}
    return out


def bentler(t):
    """TBDY tarzı '4.3.6.2 -' numaralı bentlere böl (finditer: örtüşmesiz, iç-numara bölmesi yok)."""
    out = {}
    ms = list(re.finditer(r"\b(\d{1,2}(?:\.\d{1,2}){1,3})\s*[–\-—]\s", t))
    for i, m in enumerate(ms):
        no = m.group(1)
        son = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        govde = t[m.end():son].strip()
        if no in out or len(govde) < 60:
            continue
        out[no] = {"metin": govde[:2500], "degisiklik_yillari": []}
    return out


def temiz_mi(c):
    if not (60 <= len(c) <= 300):
        return False
    if any(k in c for k in KARA_LISTE):
        return False
    if not re.match(r"^[A-ZÇĞİÖŞÜ]", c):                      # büyük harfle başlamalı
        return False
    if re.match(r"^(Aksi|Ancak|Ayrıca|Bu\s|Bunlar|Bununla|Buna\s|Şu\s|O\s|Aynı\s|Söz konusu)", c):
        return False                                           # bağlam-kopuk anafor başlangıcı
    if re.search(r"\.\d{1,3}\b|\d[A-ZÇĞİÖŞÜ]|\(\.{2,}\)|\)\d|[KE]\.\s*:|\d{4}/\d+", c):
        return False                                           # dipnot/karar artıkları
    if re.search(r"\b\d{3,4}\s*sayılı", c):
        return False                                           # başka kanuna atıf içeren cümle (karışıklık riski)
    if c.count("(") != c.count(")") or c.count("(") > 1:
        return False
    if OCR_ONEK.search(c) or OCR_ARTIK.search(c):
        return False                                           # kelime-içi kopma kalıntısı
    if FORMUL_ARTIK.search(c):
        return False                                           # denklem/tablo/sembol artığı
    if re.search(r"\b(\S{2,})\s+\1\b", c):
        return False                                           # başlık yapışması ("DD-1 DD-1")
    if not FIIL_SON.search(c):                                 # fiille bitmeli (fragman eleme)
        return False
    return any(k in c.lower() for k in HUKUM_ANAHTAR)


def cumleler(metin):
    # Parantez içi değişiklik etiketlerini at, sonra yalnızca nokta ile böl
    metin = re.sub(r"\((?:Değişik|Ek|Mülga|Yeniden düzenleme)[^)]*\)", " ", metin)
    adaylar = []
    for c in re.split(r"(?<=\.)\s+", metin):
        c = re.sub(r"^\(?[a-z0-9]{1,2}\)\s*", "", c.strip())   # baştaki "b)" / "(4)" işaretini sök
        c = c.strip()
        if c and temiz_mi(c):
            adaylar.append(c)
    return adaylar


def sayi_sapt(c):
    """Tarih ve parantez-içi olmayan ilk sayıyı saptır."""
    for m in re.finditer(r"\b(\d{1,4})\b", c):
        s = m.group(1)
        cevre = c[max(0, m.start() - 12):m.end() + 12]
        if re.search(r"\d/\d|\d\.\d|sayılı|n[cç][iı]|inci|üncü|uncu\b|madde|Denk|Tablo|Bölüm|'[dt]", cevre):  # tarih/atıf atla
            continue
        n = int(s)
        if n < 1 or n > 5000:
            continue
        yeni = n * 2 if n < 500 else n // 2
        if yeni != n:
            return c[:m.start()] + str(yeni) + c[m.end():], f"{s}→{yeni}"
    for kelime, yeni in SAYI_KELIME.items():
        if re.search(rf"\b{kelime}\b", c):
            return re.sub(rf"\b{kelime}\b", yeni, c, count=1), f"{kelime}→{yeni}"
    return None


def kucult(c):
    if not c:
        return c
    ilk = {"İ": "i", "I": "ı"}.get(c[0], c[0].lower())
    return ilk + c[1:]


def uret(pdfdir, hedef):
    kayitlar = []
    kanun_madde = {}
    for kod, meta in LAWS.items():
        yol = os.path.join(pdfdir, meta["dosya"])
        if not os.path.exists(yol):
            print(f"UYARI: {yol} yok, atlanıyor"); continue
        ham = normalize(pdf_metin(yol))
        kanun_madde[kod] = bentler(ham) if meta["tur"] == "tbdy" else maddeler(ham)
        n_cumle = sum(len(cumleler(m["metin"])) for m in kanun_madde[kod].values())
        print(f"{kod}: {len(kanun_madde[kod])} madde, {n_cumle} temiz hüküm cümlesi")

    tekrar = {}
    for kod2, mds2 in kanun_madde.items():
        for no2, md2 in mds2.items():
            for c2 in cumleler(md2["metin"])[:8]:
                k2 = re.sub(r"\s+", " ", c2.lower())[:150]
                tekrar[k2] = tekrar.get(k2, 0) + 1

    def ekle(kanun, madde_no, probe, iddia, gold, alinti, sablon, deg=""):
        kayitlar.append({"kanun": kanun, "madde": madde_no, "probe": probe, "iddia": iddia,
                         "gold": gold, "kaynak_alinti": alinti[:220], "degisiklik_notu": deg,
                         "uretim_sablonu": sablon, "durum": "ONAY_BEKLIYOR"})

    for kod, mds in kanun_madde.items():
        meta = LAWS[kod]
        digerleri = [k for k in kanun_madde if k != kod and LAWS[k]["tur"] != "tbdy" and meta["tur"] != "tbdy"]
        mevcut_maddeler = sorted(mds)
        for no, md in sorted(mds.items()):
            for c in cumleler(md["metin"])[:8]:
                coklu = tekrar.get(re.sub(r"\s+", " ", c.lower())[:150], 1) > 1
                # Tek DOĞRU varyant: verbatim veya madde-atıflı (çok-yerli cümlede yalnız verbatim)
                if coklu or random.random() < 0.5:
                    ekle(kod, no, "P1_dogrudan", f"{meta['kisa']}{meta['gore']} {kucult(c)}",
                         "DOGRU", c, "P1_verbatim")
                else:
                    birim1 = f"{no} numaralı bendine" if meta["tur"] == "tbdy" else f"{no}. maddesine"
                    ekle(kod, no, "P1_dogrudan",
                         f"{meta['kisa']}{meta['iyelik']} {birim1} göre {kucult(c)}",
                         "DOGRU", c, "P1_madde_atifli")
                s = sayi_sapt(c)
                if s:
                    sc, not_ = s
                    ekle(kod, no, "P2_sayisal", f"{meta['kisa']}{meta['gore']} {kucult(sc)}",
                         "YANLIS", c, f"P2_swap({not_})")
                # Tek P5 varyantı (çok-yerli cümlede madde-kaydırma güvensiz → atla/karıştır)
                if coklu and not digerleri:
                    continue
                if (coklu or random.random() < 0.5) and digerleri:
                    hk = random.choice(digerleri)
                    ekle(kod, no, "P5_capraz", f"{LAWS[hk]['kisa']}{LAWS[hk]['gore']} {kucult(c)}",
                         "YANLIS", c, f"P5_lawshuffle({kod}→{hk})")
                else:
                    hedef_no = random.choice([m for m in mevcut_maddeler if m != no] or [no])
                    birim = "numaralı bendine" if meta["tur"] == "tbdy" else "maddesine"
                    hedef_gosterim = f"{hedef_no} {birim}" if meta["tur"] == "tbdy" else f"{hedef_no}. {birim}"
                    ekle(kod, no, "P5_capraz",
                         f"{meta['kisa']}{meta['iyelik']} {hedef_gosterim} göre {kucult(c)}",
                         "YANLIS", c, f"P5_maddeshift({no}→{hedef_no})")
            if md["degisiklik_yillari"] and meta["tur"] != "tbdy":
                yil = md["degisiklik_yillari"][-1]
                ekle(kod, no, "P6_guncellik",
                     f"{meta['kisa']}{meta['iyelik']} {no}. maddesi, ilk yayımlandığı {meta['kabul']} yılından bu yana hiç değiştirilmemiştir.",
                     "YANLIS", md["metin"][:200], "P6_degismedi", f"değişiklik: {yil}")
                ekle(kod, no, "P6_guncellik",
                     f"{meta['kisa']}{meta['iyelik']} {no}. maddesinde {yil} yılında değişiklik yapılmıştır.",
                     "DOGRU", md["metin"][:200], "P6_yil", f"değişiklik: {yil}")
        p3_fiil = "kabul edilmiştir" if meta["tur"] == "kanun" else "Resmî Gazete'de yayımlanmıştır"
        for yanlis_yil in {meta["kabul"] - 10, meta["kabul"] + 9, 2003} - {meta["kabul"]}:
            ekle(kod, 0, "P3_anakronizm", f"{meta['ad']} {yanlis_yil} yılında {p3_fiil}.",
                 "YANLIS", f"yıl: {meta['kabul']}", "P3_yil")
        ekle(kod, 0, "P3_anakronizm", f"{meta['ad']} {meta['kabul']} yılında {p3_fiil}.",
             "DOGRU", f"yıl: {meta['kabul']}", "P3_yil_dogru")
        if meta["tur"] == "tbdy":
            for belge in TBDY_UYDURMA:
                ekle(kod, 0, "P4_uydurma",
                     f"{meta['kisa']}{meta['gore']} her yeni binada '{belge}' bulundurulması zorunludur.",
                     "YANLIS", "uydurma TBDY şartı", "P4_tbdy")
            ekle(kod, 0, "P3_anakronizm",
                 f"{meta['kisa']}, 1 Ocak 2019 tarihinde yürürlüğe girmiştir.",
                 "DOGRU", "yürürlük: 01.01.2019", "P3_yururluk")
        else:
            for belge in random.sample(UYDURMA_BELGELER, 4):
                ekle(kod, 0, "P4_uydurma",
                     f"{meta['kisa']}{meta['gore']} ilgililer '{belge}' belgesini {random.choice(UYDURMA_EYLEM)} zorundadır.",
                     "YANLIS", "uydurma belge şablonu", "P4_belge")

    gorulen, tekil = set(), []
    for k in kayitlar:
        anahtar = re.sub(r"\s+", " ", k["iddia"].lower())
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar); tekil.append(k)
    dogru = [k for k in tekil if k["gold"] == "DOGRU"]
    yanlis = [k for k in tekil if k["gold"] == "YANLIS"]
    yarim = min(len(dogru), len(yanlis), hedef // 2)
    random.shuffle(dogru); random.shuffle(yanlis)
    secim = dogru[:yarim] + yanlis[:yarim]
    random.shuffle(secim)
    for i, k in enumerate(secim, 1):
        k["id"] = i
    print(f"aday havuzu: {len(tekil)} (D:{len(dogru)} / Y:{len(yanlis)}) → seçilen: {len(secim)} (50/50)")
    return secim


def yaz(kayitlar, yol):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    alanlar = ["id", "kanun", "madde", "probe", "iddia", "gold", "kaynak_alinti",
               "degisiklik_notu", "uretim_sablonu", "durum"]
    with open(yol, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader(); w.writerows(kayitlar)
    print("yazıldı:", yol)


ORNEK = """MADDE 10 – (Değişik: 4/7/2019-7181/12 md.) İşveren, iş sağlığı ve güvenliği yönünden risk değerlendirmesi yapmak veya yaptırmakla yükümlüdür. Bu fıkrada yer alan "risk" ibaresi "tehlike" şeklinde değiştirilmiştir. Anayasa Mahkemesinin 2020/51 sayılı Kararı ile iptal edilmiştir.
MADDE 14 – İşveren, iş kazalarını kazadan sonraki üç iş günü içinde Sosyal Güvenlik Kurumuna b ildirmekle yükümlüdür. b) Sağlık hizmeti sunucuları kendilerine intikal eden iş kazalarını en geç on gün içinde Kuruma bildirir.
Madde 29 – Yapıya başlama müddeti ruhsat tarihinden itibaren iki yıldır. Başlanmayan yapıda verilen ruhsat hükümsüz sayılır.89 (4) Bu durumda yeniden ruhsat alınması mecburidir."""


def selftest():
    t = normalize(ORNEK)
    assert "bildirmekle" in t, "OCR onarımı çalışmıyor"
    mds = maddeler(t)
    assert set(mds) == {10, 14, 29}, list(mds)
    assert mds[10]["degisiklik_yillari"] == [2019]
    c10 = cumleler(mds[10]["metin"])
    assert all("ibaresi" not in c and "Anayasa" not in c for c in c10), c10
    assert any("risk değerlendirmesi" in c for c in c10), c10
    c14 = cumleler(mds[14]["metin"])
    assert any(c.startswith("Sağlık hizmeti") for c in c14), c14   # "b)" işareti söküldü
    c29 = cumleler(mds[29]["metin"])
    assert all(".89" not in c for c in c29), c29                    # dipnot artığı elendi
    s = sayi_sapt("İşveren, iş kazalarını kazadan sonraki üç iş günü içinde bildirmekle yükümlüdür.")
    assert s and "beş" in s[0]
    s2 = sayi_sapt("Bu Kanun 4/7/2019 tarihinde 200 metrekare sınırı getirmiştir.")
    assert s2 and "400" in s2[0] and "4/7/2019" in s2[0], s2        # tarih korunur, 200 saptırılır
    assert kucult("İşyeri tehlike") == "işyeri tehlike", kucult("İşyeri tehlike")
    assert kucult("Isparta ili") == "ısparta ili"
    assert not temiz_mi("Bu Kanunda hüküm bulunmayan hallerde 3194 sayılı İmar Kanunu hükümleri uygulanır ve buna göre işlem yapılır.")
    assert sayi_sapt("İşveren herhangi bir sebeple işten uzak kalanlara eğitim verir gün içinde.") is None or "iki sebeple" not in sayi_sapt("İşveren herhangi bir sebeple işten uzak kalanlara eğitim verir gün içinde.")[0], "bir-swap hala aktif"
    assert not temiz_mi("Aksi takdirde işveren hakkında bir yıllık sözleşme ücreti tutarında ceza uygulanır."), "anafor filtresi çalışmıyor"
    assert "artırılır" in normalize("hizmet bedeli yıllık %5 artı rılır"), "OCR sözlük onarımı eksik"
    assert not temiz_mi("Güvenlik raporu hazırlam a yükümlülüğü bulunan işveren raporu makama sunmakla yükümlüdür ve gerekir.")
    assert not temiz_mi("Sermayelerinin ta mamının mimar veya mühendislere ait olması zorunlu sayılır ve gerekir bu yıl gün.")
    assert temiz_mi("İşveren, iş kazalarını kazadan sonraki üç iş günü içinde Sosyal Güvenlik Kurumuna bildirmekle yükümlüdür.")
    assert temiz_mi("İşyerleri az tehlikeli sınıfta yer alan işler için üç yıllık plan hazırlamakla yükümlü sayılır ve gün içinde bildirilir.")
    assert LAWS["ISGRISK"]["gore"] == "'ne göre" and LAWS["6331"]["gore"] == "'a göre"
    tb = bentler(normalize("3.1.2 - Bina yükseklik sınıfları, bina yüksekliğine ve deprem tasarım sınıfına bağlı olarak Tablo 3.3 esas alınarak belirlenir ve tasarımda bu sınıflar kullanılır. 4.3.6.2 - Denk.(4.5a)'daki ilk terim üst bölümden aktarılan kuvvetleri gösterir ve DDD ν katsayısı = 0.6 alınır."))
    assert "3.1.2" in tb and "4.3.6.2" in tb, list(tb)
    c1 = cumleler(tb["3.1.2"]["metin"]); c2 = cumleler(tb["4.3.6.2"]["metin"])
    assert not c1 or all("Tablo" not in x for x in c1)
    assert not c2, c2   # denklem artığı cümle elenmeli
    assert len(LAWS) == 6
    assert not temiz_mi("Kirişler, aşağıda tanımlanan çapraz yükler için ayrıca hesaplanacak ve buna göre boyutlandırılacaktır.")
    assert not temiz_mi("Deprem Yer Hareketi DD-1 DD-1 spektral büyüklükleri için esas alınacak değerler burada verilir ve uygulanır.")
    print("SELFTEST OK — v3.6: çok-yerli cümle koruması, bağlam ve başlık-yapışması filtreleri")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfdir", default="data/kaynak_pdf")
    ap.add_argument("--out", default="data/iddialar/uretilen_iddialar_v1.csv")
    ap.add_argument("--hedef", type=int, default=1500)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); sys.exit(0)
    yaz(uret(a.pdfdir, a.hedef), a.out)
