"""The analysis exactly as preregistered (Rule 1 links and the calendar-year rule), with and without the K060694 date
correction (Table 2 note, eTables 1, 4, and 6). Also checks that the same code on the primary links (Rule 2 v2)
reproduces the Stage 6 year-rule values (910, 2,643, 1,762; H2 376).
Origin: red-team r2_compute.py (section 1) and r3_compute.py."""
from _common import *
import networkx as nx

r1 = csv("predicate_edges_rule1.csv", dtype=str)
rd = dict(zip(recnodes.k_number, D(recnodes.event_date_initiated)))
rcls = dict(zip(recnodes.k_number, recnodes.worst_class))
def graph(df):
    H = nx.DiGraph(); H.add_nodes_from(corpus.k_number)
    H.add_edges_from((p, d) for p, d in zip(df.predicate_knumber, df.device_knumber) if p in V and d in V); return H
def post(a, b): r = rd.get(a); y = year.get(b); return pd.notna(r) and pd.notna(y) and y > r.year
def an(H, S):
    P, c, Dn = set(), 0, set()
    for a in S:
        if pd.isna(rd.get(a)): continue
        for b in H.successors(a):
            if b not in recset and post(a, b): P.add(a); c += 1; Dn.add(b)
    return [len(P), c, len(Dn)]
def h2(H, S):
    n = 0
    for a in S:
        if pd.isna(rd.get(a)): continue
        cc = [b for b in H.successors(a) if pd.notna(year.get(b))]
        if cc and all(post(a, b) for b in cc): n += 1
    return n
def maxgap(H, S):
    m = 0
    for a in S:
        if pd.isna(rd.get(a)): continue
        cy = [year.get(b) for b in H.successors(a) if pd.notna(year.get(b))]
        if cy: m = max(m, max(cy) - rd[a].year)
    return int(m)
G1, G2 = graph(r1), graph(edges); Hn = graph(r1[r1.confidence == "NEAR_CUE"])
cii = {a for a in recset if rcls.get(a) in ("Class I", "Class II")}
out = {"check_rule2v2_year_rule": {"primary": an(G2, recset), "H2": h2(G2, recset)}}
for lab, S in [("as_registered", recset), ("as_registered_excluding_K060694", recset - {"K060694"})]:
    out[lab] = {"primary": an(G1, S), "H2": h2(G1, S), "H3_max_gap_years": maxgap(G1, S),
                "class_I_II": an(G1, S & cii), "near_cue": an(Hn, S), "both": an(Hn, S & cii)}
save("ph04_as_registered", out)
