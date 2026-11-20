"""Shared loaders for the post hoc scripts. Run every script from the repository root:
    python analysis_posthoc/<script>.py
All inputs are the frozen August 8, 2026 snapshot and the saved pipeline outputs in data/. Nothing is downloaded."""
import gzip, json, os, sys
from math import sqrt
import numpy as np, pandas as pd

ROOT = os.getcwd()
assert os.path.exists(os.path.join(ROOT, "snapshot", "SNAPSHOT.json")), "run from the repository root"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "design_arm"))
OUT = os.path.join(ROOT, "data", "posthoc"); os.makedirs(OUT, exist_ok=True)
END = pd.Timestamp("2026-07-24")        # last clearance in the snapshot (end of observation for citation timing)
D = lambda s: pd.to_datetime(s, errors="coerce")

def j(path):
    with gzip.open(os.path.join(ROOT, path), "rt") as f:
        x = json.load(f)
    return x if isinstance(x, list) else x.get("results", x)

def csv(name, **kw):
    return pd.read_csv(os.path.join(ROOT, "data", name), **kw)

def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]

def km_curve(t, e):
    """Kaplan-Meier cumulative incidence with log-log Greenwood CIs. Returns DataFrame time, cuminc, lo, hi (percent)."""
    t, e = np.asarray(t, float), np.asarray(e, int); S, V, rows = 1.0, 0.0, [(0.0, 0.0, 0.0, 0.0)]
    for u in np.unique(t[e == 1]):
        d = ((t == u) & (e == 1)).sum(); n = (t >= u).sum(); S *= 1 - d / n
        V += d / (n * (n - d)) if n > d else 0
        if 0 < S < 1:
            se = np.sqrt(V) / abs(np.log(S)); sl, sh = S ** np.exp(1.959964 * se), S ** np.exp(-1.959964 * se)
        else:
            sl = sh = S
        rows.append((u, 100 * (1 - S), 100 * (1 - sh), 100 * (1 - sl)))
    return pd.DataFrame(rows, columns=["time", "cuminc", "lo", "hi"])

def km_at(t, e, a):
    """Cumulative incidence at time a; None (not estimable) if a is beyond the cohort's maximum follow-up."""
    if np.max(t) < a: return None
    c = km_curve(t, e); r = c[c.time <= a].iloc[-1]
    return [round(r.cuminc, 1), round(r.lo, 1), round(r.hi, 1)]

def save(name, obj):
    def conv(o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.bool_,)): return bool(o)
        raise TypeError(type(o))
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump(obj, f, indent=1, default=conv)
    print(json.dumps(obj, indent=1, default=conv))

# common objects
corpus = csv("corpus.csv", dtype=str)
corpus["decision_year"] = pd.to_numeric(corpus.decision_year, errors="coerce")
V = set(corpus.k_number)
year = dict(zip(corpus.k_number, corpus.decision_year))
raw510 = j("snapshot/510k_raw.json.gz")
recv = {r["k_number"]: D(r.get("date_received")) for r in raw510 if r.get("k_number")}
edges = csv("predicate_edges.csv", dtype=str)
recnodes = csv("recalled_nodes.csv", dtype=str)
recset = set(recnodes.k_number) & V
pubdf = csv("recall_public_dates.csv")
pub = dict(zip(pubdf.k_number, D(pubdf.recall_public_date)))
ct = csv("citation_timing.csv")
for c in ["recall_initiated", "recall_public", "b_received"]:
    ct[c] = D(ct[c])
A = ct[ct.category == "A"].copy()       # post-recall citations by never-recalled devices (primary)
