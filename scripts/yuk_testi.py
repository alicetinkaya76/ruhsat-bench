# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — YUK / HIZ SONDASI.

BULGU
-----
Tek cagri dokumu:
    total 7.218 sn | load 6.972 sn | prompt_eval 0.150 sn | eval 0.089 sn
Gercek hesap 0.24 sn; kalan her sey MODEL YUKLEME.

F4 kosusunda cagrilar arka arkaya ve sure sabit 2.96 sn. Eger model yukluyse
cagri ~0.3 sn surmeli. Demek ki ya model her cagrida yeniden yukleniyor ya
da baska bir sabit maliyet var. Bu betik AYRIMI OLCER.

YONTEM
------
Ayni modele arka arkaya N cagri yapilir ve her cagrinin load_duration'i
basilir. Sonra ayni sey keep_alive verilerek tekrarlanir.

    ilk cagri yuksek, sonrakiler ~0   -> model yukluyor, sorun baska yerde
    hepsi yuksek                      -> her cagrida yeniden yukleniyor
    keep_alive ile dusuyorsa          -> cozum keep_alive

keep_alive ollama'ya modeli VRAM'de ne kadar tutacagini soyler. Varsayilan
5 dakikadir; ama istekler arasinda parametre degisirse ya da baska bir model
araya girerse tahliye olur.

Kimlik kontrolu YOK — bu betik yalnizca hiz olcer. Cikti degisikligi riski
tasiyan bir parametre (num_ctx, num_predict) denenecekse ctx_testi.py
kullanilmalidir; o kayitli kosuyla birebir karsilastirma yapar.

Kullanim:
    python scripts/yuk_testi.py --model gemma3:4b
    python scripts/yuk_testi.py --model qwen2.5:32b-instruct --n 5
"""
import argparse
import csv
import json
import statistics
import urllib.request

SISTEM = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. KAPALI KITAP: yalnizca kendi bilginle karar ver. "
    "Cevabin SADECE su uc etiketten biri ve 0-100 guven puani olsun: DOGRU | YANLIS | EMIN_DEGILIM. "
    "Emin degilsen EMIN_DEGILIM demek, yanlis cevap vermekten iyidir. "
    "Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)


def cagir(model, kullanici, host, keep_alive):
    govde = {"model": model, "stream": False,
             "options": {"temperature": 0, "num_predict": 32, "seed": 1},
             "messages": [{"role": "system", "content": SISTEM},
                          {"role": "user", "content": kullanici}]}
    if keep_alive is not None:
        govde["keep_alive"] = keep_alive
    req = urllib.request.Request(host + "/api/chat",
                                 data=json.dumps(govde).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


def blok(baslik, model, iddialar, host, keep_alive, e):
    e()
    e(f"--- {baslik}")
    e(f"    {'#':>3} {'toplam':>9} {'yukleme':>9} {'istem':>9} {'uretim':>9}  cikti")
    sureler = []
    for i, it in enumerate(iddialar, 1):
        r = cagir(model, "Iddia: " + it, host, keep_alive)
        tot = r.get("total_duration", 0) / 1e9
        yuk = r.get("load_duration", 0) / 1e9
        ist = r.get("prompt_eval_duration", 0) / 1e9
        ure = r.get("eval_duration", 0) / 1e9
        sureler.append((tot, yuk, ist, ure))
        e(f"    {i:>3} {tot:>8.3f}s {yuk:>8.3f}s {ist:>8.3f}s {ure:>8.3f}s  "
          f"{r['message']['content'].strip()[:24]!r}")
    return sureler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--keep-alive", default="30m")
    ap.add_argument("--host", default="http://localhost:11434")
    a = ap.parse_args()

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddialar = [r["iddia"] for r in csv.DictReader(fh)][:a.n]

    L = []

    def e(s=""):
        L.append(s)
        print(s, flush=True)

    e("=" * 78)
    e(f"YUK SONDASI — {a.model} — {a.n} ardisik cagri")
    e("=" * 78)

    a_blok = blok("keep_alive YOK (varsayilan)", a.model, iddialar, a.host, None, e)
    b_blok = blok(f"keep_alive = {a.keep_alive}", a.model, iddialar, a.host, a.keep_alive, e)

    e()
    e("=" * 78)
    e("KARAR")
    e("=" * 78)
    for ad, blk in (("varsayilan", a_blok), (f"keep_alive={a.keep_alive}", b_blok)):
        tot = [x[0] for x in blk]
        yuk = [x[1] for x in blk]
        hesap = [x[2] + x[3] for x in blk]
        ilk_haric = yuk[1:] or yuk
        e(f"  {ad:<22} toplam medyan {statistics.median(tot):6.3f}s | "
          f"yukleme medyan {statistics.median(yuk):6.3f}s | "
          f"ilk cagri haric yukleme medyan {statistics.median(ilk_haric):6.3f}s | "
          f"saf hesap {statistics.median(hesap):6.3f}s")
    ka = statistics.median([x[0] for x in a_blok])
    kb = statistics.median([x[0] for x in b_blok])
    hesap = statistics.median([x[2] + x[3] for x in b_blok])
    e()
    if kb < ka * 0.7:
        e(f"  => keep_alive ISE YARIYOR: x{ka/max(kb,1e-9):.1f} hizlanma.")
        e("     f4_kos.py'ye keep_alive eklenmeli.")
    elif statistics.median([x[1] for x in b_blok][1:] or [9]) > 0.5:
        e("  => Model her cagrida YENIDEN YUKLENIYOR ve keep_alive cozmedi.")
        e("     Baska bir surec VRAM'i paylasiyor olabilir; 'ollama ps' ve")
        e("     'nvidia-smi' ile bakin, OLLAMA_MAX_LOADED_MODELS / OLLAMA_KEEP_ALIVE")
        e("     ortam degiskenlerini kontrol edin.")
    else:
        e("  => Yukleme sorunu YOK; sabit maliyet baska yerden geliyor.")
    e(f"  Saf hesap suresi cagri basina ~{hesap:.3f}s. Teorik alt sinir bu;")
    e(f"  946 cagri = ~{946*hesap/60:.0f} dk/model, 18 model = ~{18*946*hesap/3600:.1f} saat.")

    print()


if __name__ == "__main__":
    main()
