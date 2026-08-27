# -*- coding: utf-8 -*-
import argparse, csv, json, re, time, urllib.request, os

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

TR_MAP = str.maketrans({
    "\u011e": "G", "\u011f": "g", "\u015e": "S", "\u015f": "s",
    "\u0130": "I", "\u0131": "i", "\u00dc": "U", "\u00fc": "u",
    "\u00d6": "O", "\u00f6": "o", "\u00c7": "C", "\u00e7": "c",
})

def ollama_chat(model, system, user, host="http://localhost:11434"):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "options": {"temperature": 0, "num_predict": 32},
    }).encode()
    req = urllib.request.Request(host + "/api/chat", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]["content"]

def parse(out, forced):
    t = out.translate(TR_MAP).upper()
    labels = []
    for m in re.finditer(r"EMIN[\s_\-]*DEGILIM", t):
        labels.append((m.start(), "EMIN_DEGILIM"))
    for m in re.finditer(r"\b(DOGRU|YANLIS)", t):
        labels.append((m.start(), m.group(1)))
    karar = sorted(labels)[-1][1] if labels else None
    if karar == "EMIN_DEGILIM" and forced:
        karar = None
    nums = [int(x) for x in re.findall(r"\d{1,3}", t) if int(x) <= 100]
    guven = nums[-1] if nums else None
    return karar, guven

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--claims", default="data/iddialar/MEVZUAT-Bench-pilot_iddialar.csv")
    ap.add_argument("--out", default="sonuclar/yerel_sonuclar.jsonl")
    ap.add_argument("--host", default="http://localhost:11434")
    args = ap.parse_args()

    claims = list(csv.DictReader(open(args.claims, encoding="utf-8-sig")))
    done = set()
    if os.path.exists(args.out):
        for line in open(args.out, encoding="utf-8"):
            r = json.loads(line)
            if r.get("karar") is not None:
                done.add((r["model"], r["kosul"], r["id"]))
    out = open(args.out, "a", encoding="utf-8")

    for model in args.models:
        for kosul, system, forced in [("E1", E1_SISTEM, False), ("E2", E2_SISTEM, True)]:
            for c in claims:
                key = (model, kosul, c["id"])
                if key in done:
                    continue
                t0 = time.time()
                try:
                    raw = ollama_chat(model, system, "Iddia: " + c["iddia"], args.host)
                    karar, guven = parse(raw, forced)
                except Exception as e:
                    raw, karar, guven = "HATA: " + str(e), None, None
                rec = {"model": model, "kosul": kosul, "id": c["id"], "karar": karar,
                       "guven": guven, "ham": raw.strip()[:160], "sure_sn": round(time.time() - t0, 2)}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
                print(model, kosul, c["id"], karar, guven)
    print("bitti:", args.out)

if __name__ == "__main__":
    main()
