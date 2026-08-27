# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F5 — DAYANAKLI KOL KOSUCUSU  (R1 / R2 / R3-bm25)

ON KAYIT: EK-4 (kollar, karsilastirmalar, gecersizlik sartlari) +
          EK-6 (korpus secimi). IKISI DE KOSUDAN ONCE commit'lendi.

KOLLAR
------
  R1        n=289  atifla cozulen birimin TAM METNI isteme enjekte edilir
  R2        n=473  BM25 top-k (varsayilan k=3), korpusun tamami uzerinde
  R3-bm25   n=473  LLM YOK. R2'nin GETIRDIGI AYNI pasajlarda dizgi eslestirme

R1 bir TAVANDIR, dagitim tahmini degildir (EK-4 5). Iddialar bu korpustan
uretildigi icin dayanak verildiginde yuksek basari BEKLENIR.

MANSET KARSILASTIRMA (HANDOVER 3): R2 - R3-bm25.
R3 (oracle atifli) 1.00 verdigi icin R1-R0 "bilgi eklendi" kaniti olamaz;
bilgi tasiyan soru sudur: AYNI KANIT verildiginde LLM dizgi eslestirmeye
ne katiyor.

ISTEMLER — TEK DEGISKEN ILKESI
------------------------------
Kapali kitap istemleri (f4_kos.py) BIREBIR korunur; degisen TEK sey
"KAPALI KITAP: yalnizca kendi bilginle karar ver" cumlesinin yerine
dayanak talimatinin gecmesidir. Format cumlesi, etiket kumesi, kacinma
politikasi ve kullanici mesajindaki "Iddia: " oneki AYNEN ayni. Boylece
R0 ile fark yalnizca DAYANAGIN VARLIGIDIR.

Bu ifade EK-4'te sabitlenmemisti; HANDOVER 8 bunu acik soru olarak
isaretlemisti. Karar burada verilmis ve kosudan once commit'lenmistir.

DETERMINIZM UYARISI (28.08.2026 OLCULDU — ORTAM.md 3 ile CELISIYOR)
-------------------------------------------------------------------
ORTAM.md 3: "temperature 0 + sabit seed -> 946/946 birebir tekrar"
(Windows'ta, KAPALI KITAP istemlerle olculmustu).

TF-HPC'de olculen:
  kapali kitap (f4_kos.py, 10 iddia x 2 kosul)   -> 20/20 BIREBIR
  dayanakli    (bu betik, 20 iddia, R2/E1)       -> 17/20  (3 FARK)
Farklardan biri KARARIN KENDISI (DOGRU -> ayristirilamadi), biri guven
puani (85 -> 60). Ayni model, ayni makine, ayni gun, ayni tohum.

SONUC: yerel dayanakli kollar TEK KOSU ile raporlanamaz. API kollarinda
zorunlu olan 3 KOSU + COGUNLUK OYU yordami burada da uygulanmalidir.
Sebep arastirilmadi (durma kurali); kusur kutugu #29.

EK-4 10 — KOLU GECERSIZ KILAN DURUMLAR (betik bunlari OLCER)
------------------------------------------------------------
  * istem sha256 satir basina yazilmazsa      -> her satirda istem_sha256
  * kesilen yanit orani %1'i asarsa           -> --kuru sonrasi ozet uyarir
  * R2 geri cagirma orani raporlanmazsa       -> geri_cagirma alani + ozet
  * R3 izinli iki sutun disina erisirse       -> R3-bm25 yalniz id+iddia okur

KUTUK #9: "kesilen" ile "ayristirilamadi" AYRI sayaclardir. Etiket once
yazildigi icin kesilme her zaman veri kaybettirmez.

KOSU (bash)
-----------
    cd ~/Desktop/ruhsat-bench
    # 1) LLM'siz duman testi — istem hash'leri ve getirim gorulur
    .venv/bin/python -u scripts/f4_dayanak.py --kuru --sinir 10 \\
        --korpus data/korpus_v2/korpus.jsonl

    # 2) yerel model (Ollama 127.0.0.1, localhost DEGIL — ORTAM.md 2.1)
    .venv/bin/python -u scripts/f4_dayanak.py --kol R1 R2 \\
        --models llama3.2:3b-instruct-q8_0 --kosul E1 E2 \\
        --korpus data/korpus_v2/korpus.jsonl --out sonuclar/f5_dayanak.jsonl

    # 3) duyarlilik kolu (EK-6 3: ZORUNLU, ayni tabloda)
    .venv/bin/python -u scripts/f4_dayanak.py --kol R1 R2 --models ... \\
        --korpus data/korpus/korpus.jsonl --out sonuclar/f5_dayanak_1366.jsonl
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8")
    except Exception:
        pass

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

try:
    from atif_coz import atif                     # EK-4 2: atif YALNIZ iddia metninden
    from kural_taban import anahtar, icerik       # olculmus Unicode duzeltmeleri
except Exception as exc:                                    # noqa: BLE001
    print(f"! import hatasi: {exc}")
    sys.exit(1)

# ------------------------------------------------------------------ ISTEMLER
# f4_kos.py'deki kapali kitap istemleriyle KELIME KELIME karsilastirilabilir.
# Degisen tek cumle isaretlendi.
R_E1 = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. "
    "DAYANAK VERILDI: karari YALNIZCA asagidaki mevzuat metnine dayandir; "  # <-- degisen
    "hafizandaki bilgiyi kullanma. "                                          # <-- degisen
    "Cevabin SADECE su uc etiketten biri ve 0-100 guven puani olsun: DOGRU | YANLIS | EMIN_DEGILIM. "
    "Emin degilsen EMIN_DEGILIM demek, yanlis cevap vermekten iyidir. "
    "Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)
R_E2 = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. "
    "DAYANAK VERILDI: karari YALNIZCA asagidaki mevzuat metnine dayandir; "
    "hafizandaki bilgiyi kullanma. "
    "Cevabin SADECE DOGRU veya YANLIS etiketi ve 0-100 guven puani olsun; kacinma SECENEGIN YOK, "
    "emin olmasan bile en olasi cevabi sec. Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)
ISTEM = {"E1": R_E1, "E2": R_E2}

TR_MAP = str.maketrans({
    "Ğ": "G", "ğ": "g", "Ş": "S", "ş": "s",
    "İ": "I", "ı": "i", "Ü": "U", "ü": "u",
    "Ö": "O", "ö": "o", "Ç": "C", "ç": "c",
})


def belirtec(t):
    """BM25 icin belirtecleme. anahtar() butun bosluklari atar; BM25'e
    kelime siniri lazim, bu yuzden ayri. Unicode sirasi anahtar() ile AYNI:
    NFC -> lower -> U+0307 at (Turkce noktali I tuzagi)."""
    t = unicodedata.normalize("NFC", t).lower().replace("̇", "")
    return [w for w in re.split(r"[^0-9a-zçğıöşü]+", t) if len(w) > 1]


def ollama_chat(model, system, user, host, tohum, azami):
    """f4_api_v2.py'nin yerel yolu ile ayni cagri bicimi.
    ORTAM.md 2.1: host 127.0.0.1, localhost DEGIL (x4.2 yavaslama, olculdu)."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "stream": False,
        "options": {"temperature": 0, "num_predict": azami, "seed": tohum},
    }).encode()
    req = urllib.request.Request(host + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    return d["message"]["content"], d.get("done_reason", "")


def parse(out, forced):
    """f4_kos.py:parse ile AYNI mantik (son etiket, son sayi).
    KUTUK #9: 'ayristirilamadi' ile 'kesilen' AYRI kavramlardir; bu
    fonksiyon yalniz ayristirmayi bildirir, kesilmeyi cagiran karar verir."""
    t = out.translate(TR_MAP).upper()
    etiketler = []
    for m in re.finditer(r"EMIN[\s_\-]*DEGILIM", t):
        etiketler.append((m.start(), "EMIN_DEGILIM"))
    for m in re.finditer(r"\b(DOGRU|YANLIS)", t):
        etiketler.append((m.start(), m.group(1)))
    ham = sorted(etiketler)[-1][1] if etiketler else None
    sayilar = [int(x) for x in re.findall(r"\d{1,3}", t) if int(x) <= 100]
    guven = sayilar[-1] if sayilar else None
    if ham is None:
        return None, ham, guven, "ayristirilamadi"
    if ham == "EMIN_DEGILIM" and forced:
        return None, ham, guven, "e2_kacinma"
    return ham, ham, guven, "tamam"


# ------------------------------------------------------------------ KORPUS
def korpus_yukle(yol):
    birim, sira = {}, []
    for s in open(yol, encoding="utf-8"):
        r = json.loads(s)
        k = (r["kanun"], r["birim"])
        birim[k] = r
        sira.append(k)
    return birim, sira


class BM25:
    """rank_bm25 varsa onu kullanir; yoksa saf-Python BM25Okapi.
    HANDOVER 7: 'rank_bm25 kurulabilir; degilse saf-Python BM25 yaz,
    disa bagimliligi raporla.'"""

    def __init__(self, belgeler):
        self.kaynak = None
        try:
            from rank_bm25 import BM25Okapi
            self._m = BM25Okapi(belgeler)
            self.kaynak = f"rank_bm25 {_surum('rank_bm25')}"
            self._saf = False
        except Exception:
            self._saf = True
            self.kaynak = "saf-python (rank_bm25 YOK)"
            self._kur(belgeler)

    def _kur(self, belgeler, k1=1.5, b=0.75):
        self.k1, self.b, self.D = k1, b, belgeler
        self.uzunluk = [len(d) for d in belgeler]
        self.ort = sum(self.uzunluk) / max(1, len(belgeler))
        df = collections.Counter()
        self.tf = []
        for d in belgeler:
            c = collections.Counter(d)
            self.tf.append(c)
            df.update(c.keys())
        import math
        N = len(belgeler)
        self.idf = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in df.items()}

    def puanlar(self, sorgu):
        if not self._saf:
            return self._m.get_scores(sorgu)
        out = []
        for i, c in enumerate(self.tf):
            s = 0.0
            for w in sorgu:
                f = c.get(w, 0)
                if not f:
                    continue
                s += self.idf.get(w, 0.0) * f * (self.k1 + 1) / (
                    f + self.k1 * (1 - self.b + self.b * self.uzunluk[i] / self.ort))
            out.append(s)
        return out


def _surum(p):
    try:
        import importlib.metadata as md
        return md.version(p)
    except Exception:
        return "?"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def dayanak_blogu(birimler):
    """Getirilen pasajlari isteme koyulacak bicime cevirir."""
    p = []
    for r in birimler:
        p.append(f"[{r['kanun']} / {r['birim']}]\n{r['metin']}")
    return "DAYANAK:\n" + "\n\n".join(p)


def main():
    ap = argparse.ArgumentParser(description="F5 dayanakli kol kosucusu (EK-4 + EK-6)")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v7a.csv")
    ap.add_argument("--korpus", default="data/korpus_v2/korpus.jsonl")
    ap.add_argument("--out", default="sonuclar/f5_dayanak.jsonl")
    ap.add_argument("--kol", nargs="+", default=["R1", "R2", "R3bm25"],
                    choices=["R1", "R2", "R3bm25"])
    ap.add_argument("--kosul", nargs="+", default=["E1", "E2"], choices=["E1", "E2"])
    ap.add_argument("--models", nargs="+", default=[])
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--k", type=int, default=3, help="BM25 top-k (EK-4: 3)")
    # KALIBRASYON (28.08.2026, kosudan once olculdu — sonuca gore ayarlanmadi):
    #   llama3.2:3b, 78 cagri, kesilen orani: 32 -> %16,7 · 64 -> %2,56
    #   64 = 128 = 256 BIREBIR AYNI; kalan 2 kesilme butce degil TEKRAR
    #   DEJENERASYONUDUR (ham cikti: ayni cumle donguye giriyor).
    #   qwen2.5:32b ayni kosuda 64 ile 0/78 kesilme verdi.
    # 128 secildi: 64 zaten yetiyor, 128 ise kapali kitap frontier kollarinin
    # yerlesik degeri (HANDOVER 3) — kollar arasi karsilastirilabilirlik icin.
    ap.add_argument("--max-token", type=int, default=128)
    ap.add_argument("--tohum", type=int, default=42)
    ap.add_argument("--sinir", type=int, default=0, help="ilk N iddia (duman testi)")
    ap.add_argument("--kuru", action="store_true",
                    help="LLM CAGIRMA; istem hash'lerini ve getirimi bas")
    a = ap.parse_args()

    if not a.kuru and not a.models:
        print("! --models verilmedi. LLM'siz calistirmak icin --kuru kullanin.")
        sys.exit(1)

    iddialar = list(csv.DictReader(open(a.claims, encoding="utf-8-sig")))
    if a.sinir:
        iddialar = iddialar[:a.sinir]
    birim, sira = korpus_yukle(a.korpus)
    korpus_sha = hashlib.sha256(open(a.korpus, "rb").read()).hexdigest()
    betik_sha = hashlib.sha256(open(__file__, "rb").read()).hexdigest()

    print(f"iddia   : {len(iddialar)}   ({a.claims})")
    print(f"korpus  : {len(birim)} birim   sha256 {korpus_sha[:16]}...")
    print(f"betik   : sha256 {betik_sha[:16]}...")

    # --- BM25 indeksi
    dizin = [belirtec(birim[k]["metin"]) for k in sira]
    bm = BM25(dizin)
    print(f"BM25    : {bm.kaynak}   k={a.k}")

    # --- atif cozumu (EK-4 2: YALNIZ iddia metninden)
    coz = {}
    for x in iddialar:
        kod, no = atif(x["iddia"])
        coz[x["id"]] = (kod, None if no is None else str(no))
    n_madde = sum(1 for v in coz.values() if v[1] is not None)
    print(f"atif    : {n_madde} madde duzeyi · {len(coz)-n_madde} belge duzeyi")
    print(f"istemler: E1 sha {_sha(R_E1)[:16]}...  E2 sha {_sha(R_E2)[:16]}...")
    print()

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    fh = open(a.out, "w", encoding="utf-8")
    sayac = collections.Counter()
    geri_cagirma = collections.Counter()

    for x in iddialar:
        kod, no = coz[x["id"]]
        # ---- R2 / R3bm25 getirimi (AYNI pasajlar — EK-4 3)
        sorgu = belirtec(x["iddia"])
        pu = bm.puanlar(sorgu)
        ilk = sorted(range(len(sira)), key=lambda i: -pu[i])[:a.k]
        getirilen = [sira[i] for i in ilk]
        dogru_birim = (kod, no) if no is not None else None
        gc = dogru_birim in getirilen if dogru_birim else None
        if gc is not None:
            geri_cagirma["ilk_k_icinde" if gc else "kacirdi"] += 1

        for kol in a.kol:
            if kol == "R1":
                if no is None or (kod, no) not in birim:
                    sayac["R1 kapsam disi (belge duzeyi)"] += 1
                    continue
                pasajlar = [birim[(kod, no)]]
            else:
                pasajlar = [birim[g] for g in getirilen]

            blok = dayanak_blogu(pasajlar)
            kullanici = blok + "\n\nIddia: " + x["iddia"]

            if kol == "R3bm25":
                # LLM YOK. EK-4 6: yalniz id ve iddia sutunlari okunur.
                gövde = " ".join(anahtar(p["metin"]) for p in pasajlar)
                bulundu = anahtar(icerik(x["iddia"])) in gövde
                kayit = dict(kol=kol, id=x["id"], kosul="-", model="r3_bm25",
                             karar="DOGRU" if bulundu else "YANLIS",
                             ham_etiket=None, guven=100, durum="tamam",
                             bitis_sebebi="kural", kesilen=False,
                             getirilen=[f"{c}/{b}" for c, b in getirilen],
                             geri_cagirma=gc,
                             istem_sha256=None, sistem_sha256=None,
                             korpus_sha256=korpus_sha, betik_sha256=betik_sha,
                             tohum=None, sure_sn=0.0)
                fh.write(json.dumps(kayit, ensure_ascii=False) + "\n")
                sayac[f"{kol}"] += 1
                continue

            for kosul in a.kosul:
                sistem = ISTEM[kosul]
                istem_sha, sistem_sha = _sha(sistem + "\n" + kullanici), _sha(sistem)
                if a.kuru:
                    kayit = dict(kol=kol, id=x["id"], kosul=kosul, model="(kuru)",
                                 karar=None, ham_etiket=None, guven=None,
                                 durum="kuru", bitis_sebebi=None, kesilen=None,
                                 getirilen=[f"{c}/{b}" for c, b in
                                            ([dogru_birim] if kol == "R1" else getirilen)],
                                 geri_cagirma=gc, istem_sha256=istem_sha,
                                 sistem_sha256=sistem_sha, istem_karakter=len(kullanici),
                                 korpus_sha256=korpus_sha, betik_sha256=betik_sha,
                                 tohum=a.tohum, sure_sn=0.0)
                    fh.write(json.dumps(kayit, ensure_ascii=False) + "\n")
                    sayac[f"{kol}/{kosul} kuru"] += 1
                    continue
                for model in a.models:
                    t0 = time.time()
                    try:
                        ham_cikti, bitis = ollama_chat(model, sistem, kullanici,
                                                       a.host, a.tohum, a.max_token)
                        karar, ham_et, guven, durum = parse(ham_cikti, kosul == "E2")
                    except Exception as exc:                # noqa: BLE001
                        ham_cikti, bitis = "", f"hata: {type(exc).__name__}"
                        karar, ham_et, guven, durum = None, None, None, "hata"
                    kesilen = bitis == "length"
                    sayac[f"{kol}/{kosul} {durum}"] += 1
                    if kesilen:
                        sayac["KESILEN"] += 1      # kutuk #9: ayristirilamadi'dan AYRI
                    fh.write(json.dumps(dict(
                        kol=kol, id=x["id"], kosul=kosul, model=model,
                        karar=karar, ham_etiket=ham_et, guven=guven, durum=durum,
                        bitis_sebebi=bitis, kesilen=kesilen,
                        getirilen=[f"{c}/{b}" for c, b in
                                   ([dogru_birim] if kol == "R1" else getirilen)],
                        geri_cagirma=gc, istem_sha256=istem_sha,
                        sistem_sha256=sistem_sha, istem_karakter=len(kullanici),
                        ham=ham_cikti[:160], korpus_sha256=korpus_sha,
                        betik_sha256=betik_sha, tohum=a.tohum,
                        sure_sn=round(time.time() - t0, 2)),
                        ensure_ascii=False) + "\n")
    fh.close()

    # ------------------------------------------------------------- OZET
    print("=" * 66)
    print("OZET")
    print("=" * 66)
    for k, v in sorted(sayac.items()):
        print(f"  {k:<38}{v:>6}")
    print()
    top_gc = sum(geri_cagirma.values())
    if top_gc:
        oran = geri_cagirma["ilk_k_icinde"] / top_gc
        print(f"  R2 GERI CAGIRMA (EK-4 10 zorunlu): "
              f"{geri_cagirma['ilk_k_icinde']}/{top_gc} = {oran:.4f}  (k={a.k})")
        print(f"    kacirdi: {geri_cagirma['kacirdi']}")
    n_cagri = sum(v for k, v in sayac.items() if "/" in k and "kuru" not in k)
    if n_cagri:
        kes = sayac["KESILEN"]
        print(f"  KESILEN: {kes}/{n_cagri} = {kes/n_cagri:.4f}")
        if kes / n_cagri > 0.01:
            print("  ! EK-4 10 IHLALI: kesilen orani %1'i asti -> KOL GECERSIZ")
    print(f"\n  cikti: {a.out}")


if __name__ == "__main__":
    main()
