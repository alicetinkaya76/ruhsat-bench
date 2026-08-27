# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — num_ctx SONDASI.

SORUN
-----
gemma3:4b kosusunda cagri sureleri neredeyse SABIT: medyan 2.96 sn,
p90 3.02 sn. Ama ciktilar 8 karakter ("DOGRU|98"), yani ~5 token. Bir 4b
modelin 5 token uretmesi 3 saniye surmez. Sabit maliyet uretimden degil,
ISTEK BASINA KURULUMDAN geliyor.

En olasi sebep: ollama modeli 131072 token'lik baglamla yukluyor
(`ollama ps` -> CONTEXT 131072). Her istekte o boyutta KV onbellegi
ayrilir/temizlenir. Iddialar birkac yuz karakter; 131k baglam gereksiz.

AMA VARSAYIMLA DEGISTIRMEYIZ
---------------------------
num_ctx'i dusurmek ciktiyi degistirmemeli (sicaklik 0, sabit tohum,
istem baglama sigiyor) — ama bu bir TAHMIN. Bu betik onu olcer:

  1. Kayitli kosudan N madde secilir (ayni model, ayni kosul).
  2. Ayni maddeler verilen num_ctx ile YENIDEN kosulur.
  3. karar, guven ve HAM CIKTI birebir karsilastirilir.
  4. Hiz farki raporlanir.

Birebir aynıysa num_ctx guvenle dusurulebilir ve butun matris hizlanir.
Tek bir cikti bile farkliysa DOKUNULMAZ — protokol degismis olur.

Kullanim:
    python scripts/ctx_testi.py --num-ctx 2048
    python scripts/ctx_testi.py --num-ctx 4096 --n 30
"""
import argparse
import json
import statistics
import time
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


def cagir(model, sistem, kullanici, host, tohum, num_ctx):
    ops = {"temperature": 0, "num_predict": 32, "seed": tohum}
    if num_ctx:
        ops["num_ctx"] = num_ctx
    body = json.dumps({"model": model, "stream": False, "options": ops,
                       "messages": [{"role": "system", "content": sistem},
                                    {"role": "user", "content": kullanici}]}).encode()
    req = urllib.request.Request(host + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]["content"], time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default="sonuclar/f4_sonuclar.jsonl")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--model", default="gemma3:4b")
    ap.add_argument("--kosul", default="E1", choices=["E1", "E2"])
    ap.add_argument("--num-ctx", type=int, required=True)
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--host", default="http://localhost:11434")
    a = ap.parse_args()

    import csv
    with open(a.claims, encoding="utf-8-sig") as fh:
        iddia = {r["id"]: r["iddia"] for r in csv.DictReader(fh)}

    kayit = []
    with open(a.jsonl, encoding="utf-8") as fh:
        for satir in fh:
            r = json.loads(satir)
            if r["model"] == a.model and r["kosul"] == a.kosul and r["id"] in iddia:
                kayit.append(r)
    kayit = kayit[:a.n]
    if not kayit:
        print("! kayitli kosuda eslesen madde yok.")
        return

    sistem = E1_SISTEM if a.kosul == "E1" else E2_SISTEM
    tohum = kayit[0].get("tohum", 0)
    print("=" * 74)
    print(f"num_ctx SONDASI — {a.model} / {a.kosul} / {len(kayit)} madde / num_ctx={a.num_ctx}")
    print("=" * 74)

    ayni, farkli, sureler = 0, [], []
    for r in kayit:
        yeni, sn = cagir(a.model, sistem, "Iddia: " + iddia[r["id"]],
                         a.host, tohum, a.num_ctx)
        sureler.append(sn)
        eski = r["ham"].strip()
        if yeni.strip()[:160] == eski:
            ayni += 1
        else:
            farkli.append((r["id"], eski, yeni.strip()[:60]))

    eski_sure = [r["sure_sn"] for r in kayit if r.get("sure_sn")]
    print(f"\n  birebir ayni cikti : {ayni}/{len(kayit)}")
    if farkli:
        print(f"  FARKLI: {len(farkli)}")
        for i, e_, y_ in farkli[:8]:
            print(f"    #{i}  kayitli={e_!r}  yeni={y_!r}")
    print(f"\n  eski sure medyan : {statistics.median(eski_sure):.2f} sn")
    print(f"  yeni sure medyan : {statistics.median(sureler):.2f} sn")
    hiz = statistics.median(eski_sure) / max(statistics.median(sureler), 1e-9)
    print(f"  hizlanma         : x{hiz:.2f}")

    print()
    if not farkli:
        print("  => CIKTILAR AYNI. num_ctx guvenle dusurulebilir.")
        print(f"     18 modellik varyant A butcesi kabaca x{hiz:.1f} kisalir.")
    else:
        print("  => CIKTI DEGISTI. num_ctx'e DOKUNMAYIN; protokol degismis olur")
        print("     ve F1 pilotuyla karsilastirilabilirlik gider.")


if __name__ == "__main__":
    main()
