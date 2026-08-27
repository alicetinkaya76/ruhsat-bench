# -*- coding: utf-8 -*-
import sys, json, csv
from collections import defaultdict

jsonl_path = sys.argv[1] if len(sys.argv) > 1 else "sonuclar/yerel_sonuclar.jsonl"
claims_path = sys.argv[2] if len(sys.argv) > 2 else "data/iddialar/MEVZUAT-Bench-pilot_iddialar.csv"

gold = {}
probe = {}
for c in csv.DictReader(open(claims_path, encoding="utf-8-sig")):
    gold[c["id"]] = c["altin_etiket"]
    probe[c["id"]] = c["probe_tipi"]
n_total = len(gold)

runs = defaultdict(dict)
for line in open(jsonl_path, encoding="utf-8"):
    r = json.loads(line)
    runs[(r["model"], r["kosul"])][r["id"]] = (r["karar"], r["guven"])

out_rows = []
hdr = f"{'model':30s} {'kosul':5s} {'kapsam':>7s} {'genel':>7s} {'taahhut':>8s} {'hata':>5s} {'gHata80':>8s} {'parseX':>7s}"
print(hdr); print("-" * len(hdr))
for (model, kosul), answers in sorted(runs.items()):
    ans = cor = ce80 = err = parse_fail = 0
    pp = defaultdict(lambda: [0, 0, 0])
    for cid, g in gold.items():
        karar, guven = answers.get(cid, (None, None))
        if karar is None:
            parse_fail += 1
            continue
        if karar == "EMIN_DEGILIM":
            pp[probe[cid]][2] += 1
            continue
        ans += 1
        pp[probe[cid]][1] += 1
        if karar == g:
            cor += 1; pp[probe[cid]][0] += 1
        else:
            err += 1
            if (guven or 0) >= 80:
                ce80 += 1
    kapsam = ans / n_total
    genel = cor / n_total
    taahhut = cor / ans if ans else 0.0
    print(f"{model:30s} {kosul:5s} {kapsam:7.2f} {genel:7.2f} {taahhut:8.2f} {err:5d} {ce80:8d} {parse_fail:7d}")
    row = dict(model=model, kosul=kosul, kapsam=round(kapsam, 3), genel_dogruluk=round(genel, 3),
               taahhut_dogrulugu=round(taahhut, 3), hata=err, yuksek_guvenli_hata80=ce80, parse_hatasi=parse_fail)
    for p, (d, t, k) in sorted(pp.items()):
        row[f"{p}_dogru/cevap(+kacinma)"] = f"{d}/{t}(+{k})"
    out_rows.append(row)

if out_rows:
    keys = []
    for r in out_rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open("sonuclar/yerel_metrikler.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(out_rows)
    print("kaydedildi: sonuclar/yerel_metrikler.csv")
