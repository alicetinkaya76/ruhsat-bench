# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F4 — TAM MODEL MATRISI KOSUCUSU.

run_local.py'ye gore ne degisti (ON KAYIT maddeleriyle eslesir)
---------------------------------------------------------------
  * PROMPTLAR BIREBIR AYNI (varyant A). F1 pilotuyla karsilastirilabilirlik
    buna bagli; tek karakter degistirilmedi.
  * [ON KAYIT 4] Madde sirasi her MODEL icin ayri karistirilir. Eskisinde
    butun modeller ayni sirayi goruyordu; konum etkisi modeller arasinda
    eslesiyor ve model farki gibi gorunebiliyordu.
  * [ON KAYIT 5] Varyant B promptlari eklendi. Ayni gorev, farkli ifade.
  * [ON KAYIT 3] E2'de kacinma artik parse hatasi olarak KAYBOLMUYOR.
    Eskisinde 'karar = None' yapiliyordu ve iki farkli olay ayni kovaya
    dusuyordu: model talimata ragmen kacindi mi, yoksa cikti mi
    ayristirilamadi? Ayrimi 'durum' alani tasiyor:
        tamam | e2_kacinma | ayristirilamadi | hata
    E2 uyumsuzlugu makalede AYRI raporlanacak bir bulgudur.
  * Devam (resume) artik DENENMIS olana bakar, BASARILI olana degil.
    Eskisinde E2 kacinmalari her kosuda yeniden deneniyordu; sicaklik 0
    oldugu icin ayni cevap gelir, GPU zamani bosa gider.
  * options.seed sabitlendi (tekrarlanabilirlik).
  * Ilerleme ve kalan sure tahmini basilir.

Kullanim:
    python scripts/f4_kos.py --varyant A --models qwen2.5:32b-instruct gemma3:27b ...
    python scripts/f4_kos.py --varyant B --models <alt kume>
    python scripts/f4_kos.py --varyant A --models ... --sadece-hatalar
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import time
import urllib.request

# ---------------------------------------------------------------- VARYANT A
# F1 pilotundan BIREBIR. Degistirmeyin.
E1_SISTEM = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. KAPALI KITAP: yalnizca kendi bilginle karar ver. "
    "Cevabin SADECE su uc etiketten biri ve 0-100 guven puani olsun: DOGRU | YANLIS | EMIN_DEGILIM. "
    "Emin degilsen EMIN_DEGILIM demek, yanlis cevap vermekten iyidir. "
    "Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)
E2_SISTEM = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. KAPALI KITAP: yalnizca kendi bilginle karar ver. "
    "Cevabin SADECE DOGRU veya YANLIS etiketi ve 0-100 guven puani olsun; kacinma SECENEGIN YOK, "
    "emin olmasan bile en olasi cevabi sec. Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)

# ---------------------------------------------------------------- VARYANT B
# Ayni gorev, farkli ifade. Kullanici mesaji A ile AYNI tutulur ki
# degisen tek sey sistem promptu olsun.
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

TR_MAP = str.maketrans({
    "\u011e": "G", "\u011f": "g", "\u015e": "S", "\u015f": "s",
    "\u0130": "I", "\u0131": "i", "\u00dc": "U", "\u00fc": "u",
    "\u00d6": "O", "\u00f6": "o", "\u00c7": "C", "\u00e7": "c",
})


def ollama_chat(model, system, user, host, tohum):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "stream": False,
        "options": {"temperature": 0, "num_predict": 32, "seed": tohum},
    }).encode()
    req = urllib.request.Request(host + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]["content"]


def parse(out, forced):
    """run_local.py ile AYNI ayristirma mantigi (son etiket, son sayi).
    Fark: E2 kacinmasi None'a cevrilmez, ayri bir durum olarak dondurulur."""
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--out", default="sonuclar/f4_sonuclar.jsonl")
    # OLCULDU: Windows'ta "localhost" once IPv6 ::1'e cozuluyor, ollama IPv4'te
    # dinledigi icin baglanti zaman asimina ugrayip IPv4'e dusuyor. Cagri basina
    # ~2.3 sn ceza. Ayni 946 cagri: localhost 47.7 dk, 127.0.0.1 11.2 dk (x4.2),
    # ciktilar 946/946 BIREBIR AYNI. Varsayilan bu yuzden IP.
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--varyant", default="A", choices=["A", "B"])
    ap.add_argument("--sadece-hatalar", action="store_true",
                    help="yalnizca durum=hata olan satirlari yeniden dener")
    a = ap.parse_args()

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddialar = list(csv.DictReader(fh))
    print(f"iddia: {len(iddialar)} | varyant: {a.varyant} | model: {len(a.models)}")

    # [ON KAYIT 3] Devam: DENENMIS olan atlanir. Hata satirlari istege bagli yeniden denenir.
    denenmis, hatali = set(), set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as fh:
            for satir in fh:
                r = json.loads(satir)
                k = (r["model"], r["kosul"], r.get("varyant", "A"), r["id"])
                denenmis.add(k)
                if r.get("durum") == "hata":
                    hatali.add(k)
    atlanacak = (denenmis - hatali) if a.sadece_hatalar else denenmis
    print(f"kayitli: {len(denenmis)} | hata: {len(hatali)} | atlanacak: {len(atlanacak)}")

    toplam = len(a.models) * 2 * len(iddialar) - len(atlanacak)
    yapildi, t_bas = 0, time.time()
    fh_out = open(a.out, "a", encoding="utf-8")

    for model in a.models:
        # [ON KAYIT 4] sira model basina ayri; tohum model adindan turetilir
        tohum = int(hashlib.sha256(model.encode()).hexdigest()[:8], 16) % (2**31)
        sira = list(iddialar)
        random.Random(tohum).shuffle(sira)
        for kosul in ("E1", "E2"):
            sistem = PROMPT[a.varyant][kosul]
            forced = (kosul == "E2")
            for konum, c in enumerate(sira):
                k = (model, kosul, a.varyant, c["id"])
                if k in atlanacak:
                    continue
                t0 = time.time()
                try:
                    ham_cikti = ollama_chat(model, sistem, "Iddia: " + c["iddia"],
                                            a.host, tohum)
                    karar, ham_etiket, guven, durum = parse(ham_cikti, forced)
                except Exception as exc:
                    ham_cikti, karar, ham_etiket, guven, durum = (
                        f"HATA: {exc}", None, None, None, "hata")
                fh_out.write(json.dumps({
                    "model": model, "kosul": kosul, "varyant": a.varyant,
                    "id": c["id"], "karar": karar, "ham_etiket": ham_etiket,
                    "guven": guven, "durum": durum, "konum": konum,
                    "tohum": tohum, "ham": ham_cikti.strip()[:160],
                    "sure_sn": round(time.time() - t0, 2)},
                    ensure_ascii=False) + "\n")
                fh_out.flush()
                yapildi += 1
                if yapildi % 25 == 0 or yapildi == toplam:
                    gecen = time.time() - t_bas
                    kalan = (toplam - yapildi) * gecen / max(yapildi, 1)
                    print(f"  {yapildi}/{toplam}  {model} {kosul}  "
                          f"gecen {gecen/60:.0f} dk  kalan ~{kalan/60:.0f} dk", flush=True)
    fh_out.close()
    print("bitti:", a.out)


if __name__ == "__main__":
    main()
