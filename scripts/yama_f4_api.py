# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — f4_api.py VARYANT YONLENDIRME YAMASI

SORUN
-----
Arsivdeki f4_api.py yalnizca varyant-A sistem istemlerini tanimlar
(E1_SISTEM / E2_SISTEM), kosula gore daima bunlardan birini secer, fakat
--varyant ile verilen harfi JSONL'ye oldugu gibi yazar. Sonuc: frontCB_k1-3
dosyalari "varyant": "B" etiketi tasir ama gonderilen istem A'dir.

Olcumle dogrulandi: frontC (A) ve frontCB (B) kollari arasindaki etiket
uyusmasi 0.8894; A kolu ici uyusma 0.9070, B kolu ici uyusma 0.8788.
Kollar arasi uyusma kol ici araligin ICINDE. Iki kol ayni kosulun alti
kosusundan ibarettir.

BU YAMA NE YAPAR
----------------
1. f4_kos.py'deki B istemlerini BIREBIR (karakter karakter) f4_api.py'ye tasir.
2. Istem secimini PROMPT[varyant][kosul] haritasina baglar.
3. Her JSONL satirina butunluk alanlari yazar:
   sistem_sha256, kullanici_sablon_sha256, betik_sha256, varyant
4. Kosudan ONCE pozitif kontrol calistirir: A ve B hash'leri FARKLI olmak
   zorunda; degilse betik cikar ve tek bir API cagrisi yapmaz.
5. Tam ham yaniti ayri alanda saklar (parse denetimi icin; eski 160 karakterlik
   'ham' alani semayi bozmamak icin aynen kalir).

KULLANIM
--------
    python -u scripts\\yama_f4_api.py --girdi scripts\\f4_api.py --cikti scripts\\f4_api_v2.py

Her degisiklik icin eslesme sayisi dogrulanir. Bir yama tam olarak bir kez
eslesmezse betik HATA verir ve dosya YAZILMAZ.
"""
import argparse
import hashlib
import os
import sys

# --------------------------------------------------------------- YAMA 1
# f4_kos.py satir 54-71'den birebir kopyalandi. Tek karakter degistirilmedi.
EKLENECEK_B = '''
# ---------------------------------------------------------------- VARYANT B
# f4_kos.py'den BIREBIR kopyalandi (satir 54-71). Ayni gorev, farkli ifade.
# Kullanici mesaji A ile AYNI tutulur ki degisen tek sey sistem promptu olsun.
E1_B = (
    "Asagida Turkiye mevzuatina iliskin bir iddia var. Yalnizca hafizandaki bilgiye dayan; "
    "kaynak metne bakmiyorsun. Iddia dogru mu, yanlis mi, yoksa karar veremiyor musun? "
    "Karar veremiyorsan tahmin yurutme, EMIN_DEGILIM yaz. "
    "Yanitin tek satir olsun: ETIKET|GUVEN  (ETIKET = DOGRU, YANLIS veya EMIN_DEGILIM; GUVEN = 0-100)."
)
E2_B = (
    "Asagida Turkiye mevzuatina iliskin bir iddia var. Yalnizca hafizandaki bilgiye dayan; "
    "kaynak metne bakmiyorsun. Iddia dogru mu yanlis mi? Kararsiz kalma hakkin yok; "
    "belirsizsen bile daha olasi gordugun secenegi isaretle. "
    "Yanitin tek satir olsun: ETIKET|GUVEN  (ETIKET = DOGRU veya YANLIS; GUVEN = 0-100)."
)

PROMPT = {"A": {"E1": E1_SISTEM, "E2": E2_SISTEM},
          "B": {"E1": E1_B, "E2": E2_B}}

KULLANICI_SABLON = "Iddia: {iddia}"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def istem_butunluk_kontrolu(varyant):
    """POZITIF KONTROL: A ve B gercekten farkli istemler mi?

    Bu fonksiyon TEK BIR API CAGRISINDAN ONCE calisir. A ve B hash'leri
    esitse arsivdeki yonlendirme hatasi tekrarlaniyor demektir; betik
    para harcamadan durur."""
    h = {(v, k): _sha(PROMPT[v][k]) for v in ("A", "B") for k in ("E1", "E2")}
    print("  istem butunluk kontrolu (pozitif kontrol):")
    for (v, k), d in sorted(h.items()):
        print(f"    varyant {v} / {k}  sha256={d[:16]}...")
    for k in ("E1", "E2"):
        if h[("A", k)] == h[("B", k)]:
            print(f"! DURDU: {k} icin A ve B istemleri AYNI. Varyant yonlendirmesi bozuk.")
            sys.exit(2)
    if varyant not in PROMPT:
        print(f"! DURDU: bilinmeyen varyant '{varyant}'. Gecerli: {sorted(PROMPT)}")
        sys.exit(2)
    print(f"    -> A != B dogrulandi. Bu kosuda gonderilecek varyant: {varyant}")
    return {k: h[(varyant, k)] for k in ("E1", "E2")}

'''

YAMALAR = [
    # 1) B istemleri + PROMPT haritasi + pozitif kontrol fonksiyonu
    (
        'TR_MAP = str.maketrans({',
        EKLENECEK_B.lstrip("\n") + '\nTR_MAP = str.maketrans({',
        "B istemleri, PROMPT haritasi ve pozitif kontrol eklendi",
    ),
    # 2) istem secimi haritaya baglandi
    (
        '            sistem = E1_SISTEM if kosul == "E1" else E2_SISTEM',
        '            sistem = PROMPT[a.varyant][kosul]',
        "istem secimi PROMPT[varyant][kosul] haritasina baglandi",
    ),
    # 3) kosu basinda pozitif kontrol cagrisi
    (
        '    denenmis, hatali = set(), set()',
        '    ISTEM_HASH = istem_butunluk_kontrolu(a.varyant)\n'
        '    BETIK_HASH = hashlib.sha256(\n'
        '        open(os.path.abspath(__file__), "rb").read()).hexdigest()\n'
        '    SABLON_HASH = hashlib.sha256(\n'
        '        KULLANICI_SABLON.encode("utf-8")).hexdigest()\n\n'
        '    denenmis, hatali = set(), set()',
        "kosu basina pozitif kontrol + betik/sablon hash'i eklendi",
    ),
    # 4) JSONL satirina butunluk alanlari
    (
        '                    "dusunme_token": tok[2], "bitis_sebebi": tok[3],',
        '                    "ham_tam": str(ham_cikti).strip(),\n'
        '                    "sistem_sha256": ISTEM_HASH[kosul],\n'
        '                    "kullanici_sablon_sha256": SABLON_HASH,\n'
        '                    "betik_sha256": BETIK_HASH,\n'
        '                    "dusunme_token": tok[2], "bitis_sebebi": tok[3],',
        "JSONL satirina istem/sablon/betik hash'i ve tam ham yanit eklendi",
    ),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--girdi", default="scripts/f4_api.py")
    ap.add_argument("--cikti", default="scripts/f4_api_v2.py")
    a = ap.parse_args()

    with open(a.girdi, encoding="utf-8-sig") as fh:
        kod = fh.read()

    print(f"girdi : {a.girdi}")
    print(f"  sha256 = {hashlib.sha256(kod.encode('utf-8')).hexdigest()}")
    print()

    hata = False
    for eski, yeni, aciklama in YAMALAR:
        n = kod.count(eski)
        if n != 1:
            print(f"! YAMA BASARISIZ ({n} eslesme, 1 bekleniyordu): {aciklama}")
            print(f"    aranan: {eski[:70]!r}")
            hata = True
            continue
        kod = kod.replace(eski, yeni, 1)
        print(f"  [tamam] {aciklama}")

    if hata:
        print("\n! Dosya YAZILMADI. Girdi beklenen surum degil.")
        sys.exit(1)

    # yama sonrasi ozdogrulama
    for gerekli in ("PROMPT[a.varyant][kosul]", "E1_B", "E2_B",
                    "istem_butunluk_kontrolu", "sistem_sha256"):
        if gerekli not in kod:
            print(f"! OZDOGRULAMA BASARISIZ: '{gerekli}' ciktida yok.")
            sys.exit(1)
    if 'sistem = E1_SISTEM if kosul' in kod:
        print("! OZDOGRULAMA BASARISIZ: eski istem secimi hala duruyor.")
        sys.exit(1)

    os.makedirs(os.path.dirname(a.cikti) or ".", exist_ok=True)
    with open(a.cikti, "w", encoding="utf-8") as fh:
        fh.write(kod)

    print()
    print(f"cikti : {a.cikti}")
    print(f"  sha256 = {hashlib.sha256(kod.encode('utf-8')).hexdigest()}")
    print("\n4/4 yama uygulandi, ozdogrulama gecti.")
    print("Sonraki adim: --sinir 10 ile kuru kosu yapip A/B hash farkini gorun.")


if __name__ == "__main__":
    main()
