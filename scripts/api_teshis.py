# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — API HAM YANIT TESHISI.

SORUN
-----
frontB kosusunda maddelerin %28'i (E1) bos dondu. Bos, KESILMIS degil:
ayristirilamayan kayitlarin uzunluk medyani 0. max_tokens'i 32'den 128'e
cikarmak orani 0.61'den 0.72'ye tasidi ve cikti token'i 16k'dan 42k'ya
ciktiysa da sorun surdu.

Bu desen, token butcesinin METIN DISI bir seye gittigini dusundurur.
f4_api.py su satirla metin topluyor:

    "".join(p.get("text", "") for p in d.get("content", []))

`content` dizisindeki bloklarin `text` alani yoksa (or. `thinking`,
`redacted_thinking`) sonuc BOS STRING olur ve kayit "ayristirilamadi"
diye gecer — oysa model cevap vermis olabilir.

Bu betik hicbir sey varsaymaz: kosuda BOS donen bir maddeyi bulur, ayni
istegi tekrar gonderir ve YANITIN TAMAMINI basar. `stop_reason`, blok
tipleri ve `usage` gorununce ne oldugu kesinlesir.

Kullanim:
    python scripts/api_teshis.py
    python scripts/api_teshis.py --jsonl sonuclar/frontB_k1.jsonl --max-token 512
"""
import argparse
import csv
import json
import os
import urllib.request

E1_SISTEM = (
    "Turk mevzuati hakkinda bir iddia degerlendireceksin. KAPALI KITAP: yalnizca kendi bilginle karar ver. "
    "Cevabin SADECE su uc etiketten biri ve 0-100 guven puani olsun: DOGRU | YANLIS | EMIN_DEGILIM. "
    "Emin degilsen EMIN_DEGILIM demek, yanlis cevap vermekten iyidir. "
    "Format: ETIKET|GUVEN  (ornek: YANLIS|85). Baska hicbir sey yazma."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default="sonuclar/frontB_k1.jsonl")
    ap.add_argument("--claims", default="data/iddialar/uretilen_iddialar_v6_onarilmis.csv")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--taban", default="https://api.anthropic.com")
    ap.add_argument("--anahtar-env", default="LLM_API_KEY")
    ap.add_argument("--max-token", type=int, default=128)
    ap.add_argument("--kac", type=int, default=2, help="kac bos madde denenecek")
    a = ap.parse_args()

    anahtar = os.environ.get(a.anahtar_env, "")
    if not anahtar:
        print(f"! {a.anahtar_env} bos.")
        return

    with open(a.claims, encoding="utf-8-sig") as fh:
        iddia = {r["id"]: r["iddia"] for r in csv.DictReader(fh)}

    bos = []
    with open(a.jsonl, encoding="utf-8") as fh:
        for satir in fh:
            r = json.loads(satir)
            if r.get("durum") == "ayristirilamadi" and r["kosul"] == "E1":
                bos.append(str(r["id"]))
    print(f"bos donen E1 maddesi: {len(bos)}")
    if not bos:
        print("bos madde yok, teshise gerek kalmadi.")
        return

    for cid in bos[:a.kac]:
        print("\n" + "=" * 78)
        print(f"#{cid}  max_tokens={a.max_token}")
        print("iddia:", " ".join(iddia[cid].split())[:110])
        print("=" * 78)
        govde = {"model": a.model, "max_tokens": a.max_token, "system": E1_SISTEM,
                 "messages": [{"role": "user", "content": "Iddia: " + iddia[cid]}]}
        req = urllib.request.Request(
            a.taban.rstrip("/") + "/v1/messages",
            data=json.dumps(govde).encode(),
            headers={"Content-Type": "application/json", "x-api-key": anahtar,
                     "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
        except Exception as exc:
            print("HATA:", exc)
            continue

        print("stop_reason :", d.get("stop_reason"))
        print("usage       :", d.get("usage"))
        print("content blok sayisi:", len(d.get("content", [])))
        for i, p in enumerate(d.get("content", [])):
            print(f"  [{i}] type={p.get('type')!r}  anahtarlar={sorted(p.keys())}")
            for alan in ("text", "thinking", "content"):
                if alan in p:
                    print(f"      {alan} = {str(p[alan])[:220]!r}")
        print("\n--- f4_api.py'nin topladigi metin ---")
        print(repr("".join(p.get("text", "") for p in d.get("content", []))))
        print("--- TUM bloklardan toplanan metin ---")
        print(repr("".join(str(p.get("text") or p.get("thinking") or "")
                           for p in d.get("content", []))))

    print("\n" + "=" * 78)
    print("NASIL OKUNUR")
    print("  stop_reason='max_tokens' ve tek bir 'text' blogu bos ise -> sinir sorunu")
    print("  content'te 'thinking' bloklari varsa -> butce dusunmeye gidiyor;")
    print("     ya dusunme kapatilmali ya da f4_api.py butun blok tiplerini")
    print("     toplamali (ama dusunme metnini ayristirmak protokolu degistirir)")
    print("  content bos dizi ise -> model gercekten hicbir sey uretmemis")


if __name__ == "__main__":
    main()
