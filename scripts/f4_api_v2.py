# -*- coding: utf-8 -*-
"""
RUHSAT-Bench F4 — FRONTIER MODEL KOSUCUSU (tavan olcumu).

NEDEN GEREKLI
-------------
Yerel 16 modelin hicbiri sans ustunde degil (en yuksek Youden J = 0.28,
lambda <= 0.21). Bu tek basina IKI ayri sonucla uyumludur:

  (a) gorev kapali kitap cozulemez  -> bulgu: "bu gorev cok zor"
  (b) bu modeller zayif             -> bulgu: "acik agirlikli modeller yetersiz"

Tavan olcumu olmadan ayirt edilemez ve hakemin ilk soracagi sey budur.
Birkac frontier model, taban olcumune anlam veren referansi saglar.

TASARIM
-------
  * PROMPTLAR f4_kos.py ile BIREBIR AYNI (varyant A). Karsilastirilabilirlik
    buna baglidir; tek karakter degistirilmemistir.
  * Ayristirma mantigi ayni: son etiket, son sayi, E2 kacinmasi ayri durum.
  * CIKTI SEMASI ayni -> f4_skor.py hicbir degisiklik olmadan puanlar.
  * sicaklik 0. Frontier saglayicilarda tam determinizm garanti degildir;
    bu bir SINIRLILIKTIR ve makalede yazilmalidir.
  * Devam mantigi ayni: denenmis (model, kosul, varyant, id) atlanir.
  * Hiz sinirlamasi icin ustel geri cekilme; hata durumu kaydedilir ve
    --sadece-hatalar ile yeniden denenebilir.

SAGLAYICI
---------
  --saglayici openai   : OpenAI uyumlu /chat/completions
                         (OpenAI, Azure, OpenRouter, Together, DeepSeek,
                          Groq, Fireworks vb. hepsi bu arayuzu sunar)
  --saglayici anthropic: Anthropic /v1/messages

Anahtar ortam degiskeninden okunur; komut satirina YAZILMAZ (kabuk gecmisine
ve ekran goruntulerine sizmasin diye).

    $env:LLM_API_KEY = "..."
    python scripts/f4_api.py --saglayici openai --taban https://api.openai.com/v1 --models gpt-4o

MALIYET
-------
473 iddia x 2 kosul = 946 cagri/model. Istem ~180 token, cikti ~10 token.
Model basina kabaca 170k girdi + 10k cikti token. Betik kosu sonunda
gercek token sayimini basar.
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import time
import urllib.error
import urllib.request

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


TR_MAP = str.maketrans({
    "\u011e": "G", "\u011f": "g", "\u015e": "S", "\u015f": "s",
    "\u0130": "I", "\u0131": "i", "\u00dc": "U", "\u00fc": "u",
    "\u00d6": "O", "\u00f6": "o", "\u00c7": "C", "\u00e7": "c",
})


def parse(out, forced):
    """f4_kos.py ile BIREBIR ayni ayristirma."""
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


def istek(saglayici, taban, model, anahtar, sistem, kullanici, tohum, sicaklik,
          max_token, dusunme):
    """sicaklik None ise parametre HIC GONDERILMEZ.
    Gerekce: bazi modeller (or. claude-sonnet-5) `temperature` kabul etmiyor ve
    400 donuyor. Parametreyi gondermemek, o modelin varsayilan ornekleme
    davranisini kullanmak demektir; bu DETERMINIZM GARANTISI VERMEZ ve
    makalede sinirlilik olarak yazilmalidir (bkz. --sinir ile tekrar sondasi)."""
    if saglayici == "anthropic":
        url = taban.rstrip("/") + "/v1/messages"
        govde = {"model": model, "max_tokens": max_token,
                 "system": sistem,
                 "messages": [{"role": "user", "content": kullanici}]}
        if sicaklik is not None:
            govde["temperature"] = sicaklik
        # DUSUNME: yerel modeller dogrudan cevap uretiyordu (6-11 token).
        # Frontier modelin genisletilmis dusunmesi acikken butcenin tamami
        # dusunmeye gidiyor ve `text` blogu hic olusmuyor. Protokolu esitlemek
        # icin birincil kolda dusunme KAPATILIR.
        if dusunme is None:
            govde["thinking"] = {"type": "disabled"}
        else:
            govde["thinking"] = {"type": "enabled", "budget_tokens": dusunme}
        baslik = {"Content-Type": "application/json", "x-api-key": anahtar,
                  "anthropic-version": "2023-06-01"}
    else:
        url = taban.rstrip("/") + "/chat/completions"
        govde = {"model": model, "max_tokens": max_token, "seed": tohum,
                 "messages": [{"role": "system", "content": sistem},
                              {"role": "user", "content": kullanici}]}
        if sicaklik is not None:
            govde["temperature"] = sicaklik
        baslik = {"Content-Type": "application/json",
                  "Authorization": "Bearer " + anahtar}
    req = urllib.request.Request(url, data=json.dumps(govde).encode(), headers=baslik)
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    if saglayici == "anthropic":
        metin = "".join(p.get("text", "") for p in d.get("content", []))
        kul = d.get("usage", {})
        tok = (kul.get("input_tokens", 0), kul.get("output_tokens", 0),
               (kul.get("output_tokens_details") or {}).get("thinking_tokens", 0),
               d.get("stop_reason", ""))
    else:
        metin = d["choices"][0]["message"]["content"]
        kul = d.get("usage", {})
        tok = (kul.get("prompt_tokens", 0), kul.get("completion_tokens", 0), 0,
               (d.get("choices") or [{}])[0].get("finish_reason", ""))
    return metin, tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--saglayici", default="openai", choices=["openai", "anthropic"])
    ap.add_argument("--taban", default="https://api.openai.com/v1")
    ap.add_argument("--anahtar-env", default="LLM_API_KEY")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--out", default="sonuclar/f4_frontier.jsonl")
    ap.add_argument("--varyant", default="A")
    ap.add_argument("--bekle", type=float, default=0.0, help="cagrilar arasi saniye")
    ap.add_argument("--sadece-hatalar", action="store_true")
    ap.add_argument("--sicaklik", default="otomatik",
                    help="sayi verilirse o deger gonderilir; 'yok' ise HIC gonderilmez; "
                         "'otomatik' -> openai icin 0, anthropic icin gonderilmez")
    ap.add_argument("--sinir", type=int, default=0,
                    help="ilk N iddia ile sinirla (tekrar/determinizm sondasi icin)")
    # max_tokens bir DAVRANIS parametresi degil, UST SINIRDIR. Yerel modeller
    # 6-11 token uretti ve 32'ye hic yaklasmadi (medyan cikti 8 karakter), bu
    # yuzden siniri yukseltmek onlarin ciktisini DEGISTIRMEZ. Buna karsilik
    # daha ayrintili yazan bir model, etiketi yazmadan sinira dayanip
    # "ayristirilamadi" olarak kaydedilir. Sinir yukseltilirken promptlar
    # ve ayristirma AYNEN kalir; karsilastirilabilirlik korunur.
    ap.add_argument("--dusunme", default="kapali",
                    help="'kapali' (birincil kol, yerel protokolle esit) veya "
                         "'acik:N' (N token dusunme butcesi, kesifsel kol)")
    ap.add_argument("--max-token", type=int, default=32,
                    help="yanit ust siniri. Yerel kosularda 32 kullanildi; "
                         "ayristirilamayan orani yuksekse yukseltin (or. 128)")
    a = ap.parse_args()

    anahtar = os.environ.get(a.anahtar_env, "")
    if not anahtar:
        print(f"! {a.anahtar_env} ortam degiskeni bos. Once ayarlayin:")
        print(f'    $env:{a.anahtar_env} = "sk-..."')
        return

    if a.sicaklik == "otomatik":
        sicaklik = None if a.saglayici == "anthropic" else 0.0
    elif str(a.sicaklik).lower() in ("yok", "none", ""):
        sicaklik = None
    else:
        sicaklik = float(a.sicaklik)

    if str(a.dusunme).lower().startswith("acik"):
        dusunme = int(str(a.dusunme).split(":")[1]) if ":" in str(a.dusunme) else 1024
        if a.max_token <= dusunme:
            a.max_token = dusunme + 64
    else:
        dusunme = None

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddialar = list(csv.DictReader(fh))
    if a.sinir:
        iddialar = iddialar[:a.sinir]
    print(f"iddia: {len(iddialar)} | saglayici: {a.saglayici} | model: {len(a.models)} | "
          f"temperature: {'GONDERILMIYOR' if sicaklik is None else sicaklik} | "
          f"max_tokens: {a.max_token} | "
          f"dusunme: {'KAPALI' if dusunme is None else str(dusunme) + ' token'}")
    if sicaklik is None:
        print("  ! temperature gonderilmiyor -> determinizm GARANTI DEGIL.")
        print("    --sinir ile iki kez kosup ciktilari karsilastirin (tekrar sondasi).")

    ISTEM_HASH = istem_butunluk_kontrolu(a.varyant)
    BETIK_HASH = hashlib.sha256(
        open(os.path.abspath(__file__), "rb").read()).hexdigest()
    SABLON_HASH = hashlib.sha256(
        KULLANICI_SABLON.encode("utf-8")).hexdigest()

    denenmis, hatali = set(), set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8-sig") as fh:
            for satir in fh:
                r = json.loads(satir)
                k = (r["model"], r["kosul"], r.get("varyant", "A"), r["id"])
                denenmis.add(k)
                if r.get("durum") == "hata":
                    hatali.add(k)
    atlanacak = (denenmis - hatali) if a.sadece_hatalar else denenmis
    bu_kosu = {(m, k, a.varyant, c["id"])
               for m in a.models for k in ("E1", "E2") for c in iddialar}
    toplam = len(bu_kosu - atlanacak)
    print(f"yapilacak: {toplam}")

    fh_out = open(a.out, "a", encoding="utf-8")
    yapildi, t0_hep, tok_in, tok_out, tok_dus, kesilen = 0, time.time(), 0, 0, 0, 0

    for model in a.models:
        tohum = int(hashlib.sha256(model.encode()).hexdigest()[:8], 16) % (2 ** 31)
        sira = list(iddialar)
        random.Random(tohum).shuffle(sira)
        for kosul in ("E1", "E2"):
            sistem = PROMPT[a.varyant][kosul]
            forced = (kosul == "E2")
            for c in sira:
                if (model, kosul, a.varyant, c["id"]) in atlanacak:
                    continue
                t0 = time.time()
                ham_cikti, karar, ham_et, guven, durum = "", None, None, None, "hata"
                tok = (0, 0, 0, "")
                for deneme in range(5):
                    try:
                        ham_cikti, tok = istek(a.saglayici, a.taban, model, anahtar,
                                               sistem, "Iddia: " + c["iddia"], tohum,
                                               sicaklik, a.max_token, dusunme)
                        karar, ham_et, guven, durum = parse(ham_cikti, forced)
                        break
                    except urllib.error.HTTPError as e:
                        if e.code in (429, 500, 502, 503, 529) and deneme < 4:
                            time.sleep(2 ** deneme + random.random())
                            continue
                        ham_cikti = f"HATA {e.code}: {e.read()[:120]}"
                        break
                    except Exception as exc:
                        if deneme < 4:
                            time.sleep(2 ** deneme)
                            continue
                        ham_cikti = f"HATA: {exc}"
                        break
                tok_in += tok[0]
                tok_out += tok[1]
                tok_dus += tok[2]
                kesilen += (tok[3] in ("max_tokens", "length"))
                fh_out.write(json.dumps({
                    "model": model, "kosul": kosul, "varyant": a.varyant,
                    "id": c["id"], "karar": karar, "ham_etiket": ham_et,
                    "guven": guven, "durum": durum, "konum": 0, "tohum": tohum,
                    "ham": str(ham_cikti).strip()[:160],
                    "ham_tam": str(ham_cikti).strip(),
                    "sistem_sha256": ISTEM_HASH[kosul],
                    "kullanici_sablon_sha256": SABLON_HASH,
                    "betik_sha256": BETIK_HASH,
                    "dusunme_token": tok[2], "bitis_sebebi": tok[3],
                    "sure_sn": round(time.time() - t0, 2)}, ensure_ascii=False) + "\n")
                fh_out.flush()
                yapildi += 1
                if a.bekle:
                    time.sleep(a.bekle)
                if yapildi % 25 == 0 or yapildi == toplam:
                    g = time.time() - t0_hep
                    print(f"  {yapildi}/{toplam}  {model} {kosul}  gecen {g/60:.0f} dk  "
                          f"kalan ~{(toplam-yapildi)*g/max(yapildi,1)/60:.0f} dk  "
                          f"token {tok_in//1000}k/{tok_out//1000}k", flush=True)
    fh_out.close()
    print(f"\nbitti: {a.out}")
    print(f"toplam token: girdi {tok_in:,} | cikti {tok_out:,} | dusunme {tok_dus:,}")
    print(f"butceyi asarak kesilen yanit: {kesilen}")
    if dusunme is None and tok_dus > 0:
        print("  ! DUSUNME KAPATILAMADI: kapali istendi ama dusunme token'i uretildi.")
        print("    Bu kolu birincil sayMAYIN; parametrenin bu modelde gecerli")
        print("    oldugunu dogrulamadan yerel modellerle karsilastirmayin.")
    elif dusunme is None:
        print("  dusunme token'i 0 -> protokol yerel kosularla esitlendi.")
    print("Puanlama: python scripts/f4_skor.py --jsonl " + a.out)


if __name__ == "__main__":
    main()
