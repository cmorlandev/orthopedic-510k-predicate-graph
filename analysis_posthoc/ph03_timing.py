"""Timing of post-recall reuse (Results, eMethods 5, eTable 7 note): the split of the 356 devices first cited only after
recall, time from public date to the last citing submission, devices still cited near the end of observation,
post-recall citations excluded because the citing device was itself recalled, and recall initiation to public date.
Origin: red-team r1_compute.py (section 3), r2_compute.py (section 2), r4_compute.py (R4-2, R4-4)."""
from _common import *
import networkx as nx

G = nx.DiGraph(); G.add_edges_from(zip(edges.predicate_knumber, edges.device_knumber))
first_after, persist, last = [], {}, {}
for a, p in pub.items():
    if a not in G or pd.isna(p): continue
    succ = list(G.successors(a))
    if not succ: continue
    if all(pd.notna(recv.get(b)) and recv[b] > p for b in succ): first_after.append(a)
    nr = [recv[b] for b in succ if b not in recset and pd.notna(recv.get(b)) and recv[b] > p]
    if nr: persist[a] = len(nr); last[a] = max(nr)
fa = set(first_after)
gap = np.array([(last[a] - pub[a]).days / 365.25 for a in persist])
lastA = A.groupby("predicate").b_received.max()

# post-recall citations by citing devices that were themselves recalled
e = edges[edges.predicate_knumber.isin(pub)].copy()
e["pub"] = e.predicate_knumber.map(pub); e["rec"] = e.device_knumber.map(recv)
post = e[e.rec > e.pub]; pa = post[~post.device_knumber.isin(recset)]; pr = post[post.device_knumber.isin(recset)]
ini = dict(zip(recnodes.k_number, D(recnodes.event_date_initiated)))
own_after = [ini.get(b) > recv.get(b) for b in pr.device_knumber.unique() if pd.notna(ini.get(b))]

npred = edges.groupby("device_knumber").size().reindex(A.citing.unique())
ip = (ct.recall_public - ct.recall_initiated).dt.days
ipp = ct.assign(ip=ip).groupby("predicate").ip.first()

save("ph03_timing", {
    "persistent": len(persist), "citations": int(sum(persist.values())),
    "first_cited_only_after_recall": len(fa), "of_which_in_persistent": len(fa & set(persist)),
    "of_which_not_persistent": len(fa - set(persist)),
    "years_to_last_citation": {"median": round(float(np.median(gap)), 2), "iqr": [round(float(x), 2) for x in np.percentile(gap, [25, 75])],
                               "max": round(float(gap.max()), 2), "over_10y": int((gap > 10).sum()), "over_10y_pct": round(100 * (gap > 10).mean(), 1)},
    "still_cited": {"last_on_or_after_2024_07_24": int((lastA >= pd.Timestamp("2024-07-24")).sum()),
                    "last_on_or_after_2025_07_24": int((lastA >= pd.Timestamp("2025-07-24")).sum()),
                    "last_in_2025_or_2026": int((lastA.dt.year >= 2025).sum())},
    "recalled_citers": {"citations": len(pr), "citing_devices": int(pr.device_knumber.nunique()),
                        "predicates": int(pr.predicate_knumber.nunique()),
                        "predicates_cited_only_by_recalled": len(set(pr.predicate_knumber) - set(pa.predicate_knumber)),
                        "own_recall_after_receipt": [int(sum(own_after)), len(own_after)]},
    "initiation_to_public_days": {"per_citation_n": int(ip.notna().sum()), "median": float(ip.median()),
                                  "iqr": [float(ip.quantile(.25)), float(ip.quantile(.75))],
                                  "per_predicate_n": int(ipp.notna().sum()), "per_predicate_median": float(ipp.median()),
                                  "per_predicate_iqr": [float(ipp.quantile(.25)), float(ipp.quantile(.75))]},
    "later_devices_citing_2plus_predicates": [int((npred >= 2).sum()), len(npred), float(npred.median())],
    "not_cited_after_recall": [1689 - len(persist), round(100 * (1689 - len(persist)) / 1689, 1)],
})
