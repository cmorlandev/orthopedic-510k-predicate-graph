"""Recall severity and dating checks (Limitations, eMethods 4): severity class by recall era, the start of the
Enforcement Report data, persistence and timing for devices without a class, devices whose earliest public date differs
from the public date of their earliest-initiated recall, and Class I or II devices with an earlier recall of another class.
Origin: red-team r3_compute.py (R3-3), r2_compute.py (section 6), r1 check section 7."""
from _common import *

rn = recnodes[recnodes.k_number.isin(V)].copy(); rn["init"] = D(rn.event_date_initiated); rn["y"] = rn.init.dt.year
nocls = rn.worst_class.isna() | rn.worst_class.astype(str).str.lower().isin(["nan", "n/a", "not available", ""])
na = set(rn.k_number[nocls])
lastA = A.groupby("predicate").b_received.max()
gap = pd.Series({k: (v - pub[k]).days / 365.25 for k, v in lastA.items()}); g_na = gap.index.isin(na)
enf = j("snapshot/enforcement_raw.json.gz")
rd = pd.Series([D(r.get("report_date")) for r in enf]).dropna()

report = {e.get("recall_number"): D(e.get("report_date")) for e in enf}
per = {}
for r in j("snapshot/recall_raw.json.gz"):
    dts = [D(r.get("event_date_posted")), report.get(r.get("product_res_number"), pd.NaT)]
    p = min([x for x in dts if pd.notna(x)], default=pd.NaT); i = D(r.get("event_date_initiated"))
    for k in r.get("k_numbers") or []:
        k = str(k).strip().upper()
        if k in recset: per.setdefault(k, []).append((i, p))
differ = 0
for k, Lk in per.items():
    allp = [p for _, p in Lk if pd.notna(p)]; valid = [(i, p) for i, p in Lk if pd.notna(i) and i.year >= 1976 and pd.notna(p)]
    if not allp or not valid: continue
    i0 = min(i for i, _ in valid)
    if min(p for i, p in valid if i == i0) != min(allp): differ += 1

rl = csv("recall_links_classified.csv"); rl = rl[rl.in_corpus.astype(str) == "True"] if "in_corpus" in rl else rl
rl["d"] = D(rl.event_date_initiated); rl = rl[rl.d.dt.year >= 1976]
s12 = set(recnodes[recnodes.worst_class.isin(["Class I", "Class II"])].k_number)
e_all = rl[rl.k_number.isin(s12)].groupby("k_number").d.min()
e12 = rl[rl.k_number.isin(s12) & rl.recall_class.isin(["Class I", "Class II"])].groupby("k_number").d.min()

save("ph07_severity_dating", {
    "worst_class": rn.worst_class.fillna("Not available").value_counts().to_dict(),
    "no_class_by_initiation": {"before_2002": int((rn.y[nocls] < 2002).sum()), "2002_2011": int(((rn.y >= 2002) & (rn.y <= 2011))[nocls].sum()),
                               "2012_or_later": int((rn.y[nocls] >= 2012).sum())},
    "initiated_2011_or_earlier": [int((rn.y <= 2011).sum()), int(((rn.y <= 2011) & nocls).sum())],
    "initiated_after_2011": [int((rn.y > 2011).sum()), int(((rn.y > 2011) & nocls).sum())],
    "persistent_without_class": int(g_na.sum()), "over_10y_without_class": [int((gap > 10).sum()), int(((gap > 10) & g_na).sum())],
    "median_years_to_last": {"no_class": round(float(gap[g_na].median()), 2), "classified": round(float(gap[~g_na].median()), 2)},
    "enforcement_report_date_min": str(rd.min().date()), "enforcement_records": len(rd),
    "earliest_public_differs_from_earliest_initiated": differ,
    "class_I_II_devices_with_earlier_other_recall": [int((e_all < e12).sum()), len(s12 & V)],
})
