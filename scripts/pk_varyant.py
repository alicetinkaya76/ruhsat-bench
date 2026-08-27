# POZITIF KONTROL: frontCB gercekten farkli bir kosul mu?
# Mantik: A istemi gonderildiyse, CB kolu C kolunun 4-6. kosusundan ibarettir.
#         O halde KOLLAR ARASI uyusma = KOL ICI uyusma olmali.
import json, itertools, statistics as st

def yukle(p):
    d = {}
    with open(p, encoding="utf-8-sig") as f:
        for s in f:
            r = json.loads(s)
            d[(r["kosul"], r["id"])] = (r["karar"], r["guven"])
    return d

C  = {k: yukle(f"arsiv/sonuclar/frontC_k{k}.jsonl")  for k in (1,2,3)}
CB = {k: yukle(f"arsiv/sonuclar/frontCB_k{k}.jsonl") for k in (1,2,3)}

def uyusma(a, b):
    ort = set(a) & set(b)
    ayni = sum(a[k][0] == b[k][0] for k in ort)
    dg   = st.mean(abs((a[k][1] or 0) - (b[k][1] or 0)) for k in ort)
    return ayni/len(ort), dg, len(ort)

ici_C  = [uyusma(C[i],  C[j])  for i,j in itertools.combinations((1,2,3),2)]
ici_CB = [uyusma(CB[i], CB[j]) for i,j in itertools.combinations((1,2,3),2)]
arasi  = [uyusma(C[i], CB[j])  for i in (1,2,3) for j in (1,2,3)]

def yaz(ad, xs):
    k = [x[0] for x in xs]; g = [x[1] for x in xs]
    print(f"{ad:<28} etiket uyusma {st.mean(k):.4f}  [{min(k):.4f}-{max(k):.4f}]   "
          f"|guven farki| {st.mean(g):.2f}   n cift={len(xs)}")

print("=== POZITIF KONTROL: A ve B kollari ayni kosul mu? ===\n")
yaz("KOL ICI  C  (A vs A)",  ici_C)
yaz("KOL ICI  CB (B vs B)",  ici_CB)
yaz("KOLLAR ARASI C vs CB",  arasi)
print()

# Kosul bazinda ayrim
for kos in ("E1","E2"):
    def f(d): return {k:v for k,v in d.items() if k[0]==kos}
    i1 = [uyusma(f(C[i]),  f(C[j]))  for i,j in itertools.combinations((1,2,3),2)]
    i2 = [uyusma(f(CB[i]), f(CB[j])) for i,j in itertools.combinations((1,2,3),2)]
    a  = [uyusma(f(C[i]),  f(CB[j])) for i in (1,2,3) for j in (1,2,3)]
    print(f"[{kos}] kol ici A {st.mean([x[0] for x in i1]):.4f} | "
          f"kol ici B {st.mean([x[0] for x in i2]):.4f} | "
          f"kollar arasi {st.mean([x[0] for x in a]):.4f}")

# Kacinma oranlari
print("\n=== Kacinma orani (E1, EMIN_DEGILIM) ===")
for ad, D in (("A (frontC )", C), ("B (frontCB)", CB)):
    for k in (1,2,3):
        e1 = [v[0] for kk,v in D[k].items() if kk[0]=="E1"]
        print(f"{ad} k{k}: {sum(x=='EMIN_DEGILIM' for x in e1)/len(e1):.4f}  (n={len(e1)})")
