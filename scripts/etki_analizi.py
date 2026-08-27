# -*- coding: utf-8 -*-
"""
RUHSAT-Bench — ALTIN DUZELTMESI ETKI ANALIZI  (v6 -> v7a / v7b)

AMAC
----
EK-5 duzeltmeleri ve uzlasi sonuclarinin MEVCUT kosu sonuclarina etkisini
olcer. "Kusur avina devam mi, dondurup yazim mi" kararinin dayanagidir:
hicbir hucrede niteliksel sonuc degismiyorsa av biter (durma kurali,
02.08.2026).

OLCULEN REFERANS SONUC (ilk kosum)
----------------------------------
  32 hucre:  |dBAcc| ort 0.0046, maks 0.0347
             |dlambda| ort 0.0277, maks 0.1143
  sonnet E1: BAcc 0.697->0.692, lambda 0.334->0.325
  v7a ile v7b arasindaki fark ihmal edilebilir (BAcc ort ~0.0003)
  -> HICBIR NITELIKSEL SONUC DEGISMEDI

KULLANIM
--------
    python -u scripts\\etki_analizi.py ^
        --v6 data\\iddialar\\uretilen_iddialar_v6_onarilmis.csv ^
        --v7a data\\iddialar\\uretilen_iddialar_v7a.csv ^
        --v7b data\\iddialar\\uretilen_iddialar_v7b.csv ^
        --sonuclar sonuclar\\f4_sonuclar.jsonl,sonuclar\\f4_frontier_cogunluk.jsonl:claude-sonnet-5,sonuclar\\f4_haiku_cogunluk.jsonl:claude-haiku-4.5

--sonuclar: virgulle ayrilmis jsonl listesi; "yol:modeladi" bicimi, model
alani bos dosyalara ad atar. f4_sonuclar.jsonl'den yalniz varyant A alinir.
"""
import argparse
import collections
import csv
import json
import statistics as st
import sys

for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                       # noqa: BLE001
        pass

GECERLI = ("DOGRU", "YANLIS", "EMIN_DEGILIM")


def altin(p):
    with open(p, encoding="utf-8-sig") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


def oku(p, model_adi=None, varyant="A"):
    out = []
    with open(p, encoding="utf-8-sig") as fh:
        for s in fh:
            if not s.strip():
                continue
            r = json.loads(s)
            if r.get("varyant", "A") != varyant:
                continue
            if model_adi:
                r["model"] = model_adi
            out.append(r)
    return out


def bacc(pr):
    p = [x for x in pr if x[1] == "DOGRU"]
    n = [x for x in pr if x[1] == "YANLIS"]
    if not p or not n:
        return float("nan")
    return (sum(a == "DOGRU" for a, _ in p) / len(p)
            + sum(a == "YANLIS" for a, _ in n) / len(n)) / 2


def lam(v, G):
    p1 = [(x["karar"], G[x["id"]]["gold"]) for x in v
          if G[x["id"]]["probe"] == "P1_dogrudan" and x.get("karar") in ("DOGRU", "YANLIS")]
    p5 = [(x["karar"], G[x["id"]]["gold"]) for x in v
          if G[x["id"]]["probe"] == "P5_capraz" and x.get("karar") in ("DOGRU", "YANLIS")]
    if not p1 or not p5:
        return float("nan")
    return (sum(a == g for a, g in p1) / len(p1)
            + sum(a == g for a, g in p5) / len(p5) - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v6", required=True)
    ap.add_argument("--v7a", required=True)
    ap.add_argument("--v7b", required=True)
    ap.add_argument("--sonuclar", required=True)
    ap.add_argument("--rapor", default="sonuclar/etki_analizi.txt")
    a = ap.parse_args()

    V = {"v6": altin(a.v6), "v7a": altin(a.v7a), "v7b": altin(a.v7b)}
    tum = []
    for parca in a.sonuclar.split(","):
        yol, _, ad = parca.partition(":")
        tum += oku(yol.strip(), ad.strip() or None)

    hucre = collections.defaultdict(list)
    for r in tum:
        hucre[(r["model"], r["kosul"])].append(r)

    R = []
    def y(s=""):
        print(s)
        R.append(s)

    y(f"{'model / kosul':<34}{'BAcc v6':>9}{'v7a':>8}{'v7b':>8}"
      f"{'  |':>3}{'lam v6':>9}{'v7a':>8}{'v7b':>8}")
    sat = []
    for k, v in sorted(hucre.items()):
        yan = sum(1 for x in v if x.get("karar") in GECERLI) / len(v)
        if yan < 0.80:
            continue
        row = [k]
        for ad in ("v6", "v7a", "v7b"):
            G = V[ad]
            com = [(x["karar"], G[x["id"]]["gold"]) for x in v
                   if x.get("karar") in ("DOGRU", "YANLIS")]
            row.append(bacc(com) if len(com) >= 30 else float("nan"))
        for ad in ("v6", "v7a", "v7b"):
            row.append(lam(v, V[ad]))
        sat.append(row)
        if row[1] == row[1]:
            y(f"{k[0][:26]+' / '+k[1]:<34}{row[1]:>9.3f}{row[2]:>8.3f}{row[3]:>8.3f}"
              f"{'':>3}{row[4]:>9.3f}{row[5]:>8.3f}{row[6]:>8.3f}")

    ok = [r for r in sat if r[1] == r[1]]
    y(f"\nn hucre: {len(ok)}")
    for i, ad in ((1, "BAcc"), (4, "lambda")):
        d7a = [abs(r[i + 1] - r[i]) for r in ok]
        d7b = [abs(r[i + 2] - r[i]) for r in ok]
        y(f"  {ad:<8} |v7a-v6| ort {st.mean(d7a):.4f} maks {max(d7a):.4f}   "
          f"|v7b-v6| ort {st.mean(d7b):.4f} maks {max(d7b):.4f}")
    ab = [abs(r[3] - r[2]) for r in ok if r[2] == r[2] and r[3] == r[3]]
    y(f"  v7a-v7b  |dBAcc| ort {st.mean(ab):.4f} maks {max(ab):.4f}")

    y("\nNITELIKSEL KONTROL:")
    yb = [r[1] for r in ok if not r[0][0].startswith("claude")]
    ya = [r[2] for r in ok if not r[0][0].startswith("claude")]
    if yb:
        y(f"  yerel BAcc araligi  v6 {min(yb):.3f}-{max(yb):.3f}"
          f"  ->  v7a {min(ya):.3f}-{max(ya):.3f}")
    for r in ok:
        if r[0][0] == "claude-sonnet-5":
            y(f"  sonnet {r[0][1]}  BAcc {r[1]:.3f}->{r[2]:.3f}"
              f"   lambda {r[4]:.3f}->{r[5]:.3f}")

    import os
    os.makedirs(os.path.dirname(a.rapor) or ".", exist_ok=True)
    with open(a.rapor, "w", encoding="utf-8-sig") as fh:
        fh.write("\n".join(R) + "\n")
    print(f"\nyazildi: {a.rapor}")


if __name__ == "__main__":
    main()
