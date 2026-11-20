"""Link validation and MAUDE values (Results, Table 1 of eMethods 3, eMethods 6): precision of the primary rule (Rule 2 v2)
on the second-round 199-link sample, validation-sample composition and overlap, the preregistered MAUDE two-proportion
z test, and the MAUDE unlabeled-family sum.
Origin: red-team r1_compute.py (sections 1, 2), r2_compute.py (section 4), r3_compute.py (R3-4)."""
from _common import *
import random
from scipy.stats import norm

adj_all = pd.read_csv(os.path.join(ROOT, "verification", "round2", "adjudication_266_corrected.csv"))
adj = adj_all[adj_all["sample"] == "validation_199"].copy()
es = set(zip(edges.predicate_knumber, edges.device_knumber))
tier = dict(zip(zip(edges.predicate_knumber, edges.device_knumber), edges.confidence))
adj["in_v2"] = [(p, d) in es for p, d in zip(adj.predicate_knumber, adj.device_knumber)]
s = adj[adj.in_v2].copy(); s["tier"] = [tier[(p, d)] for p, d in zip(s.predicate_knumber, s.device_knumber)]
k, n = int((s.verdict == "YES").sum()), len(s)
by_tier = {t: [int((g.verdict == "YES").sum()), len(g), round(100 * (g.verdict == "YES").mean(), 1), wilson((g.verdict == "YES").sum(), len(g))]
           for t, g in s.groupby("tier")}
vs = csv("validation_sample.csv")
ts = pd.read_csv(os.path.join(ROOT, "TEXT_SNAPSHOT_files.csv"))
random.seed(42); samp = random.sample(list(ts.k_number), 60)
no = adj[adj.verdict != "YES"]

r = csv("maude_recalled.csv"); m = csv("maude_nonrecalled.csv")
x1, x2, n1, n2 = int((r.events > 0).sum()), int((m.events > 0).sum()), len(r), len(m)
p = (x1 + x2) / (n1 + n2); z = (x1 / n1 - x2 / n2) / sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
mf = csv("maude_family.csv")

save("ph06_validation_maude", {
    "rule2v2_precision_199": {"surviving_links": n, "confirmed": k, "pct": round(100 * k / n, 1), "wilson": wilson(k, n), "by_tier": by_tier},
    "rule1_on_sample": [int((adj.verdict == "YES").sum()), len(adj)],
    "round2_sample": {"links": len(adj), "documents": int(adj.device_knumber.nunique())},
    "round1_sample": {"links": len(vs), "documents": int(vs.device_knumber.nunique())},
    "round1_round2_shared_documents": len(set(adj.device_knumber) & set(vs.device_knumber)),
    "seed42_draw_overlap": {"round1": len(set(samp) & set(vs.device_knumber)), "round2": len(set(samp) & set(adj.device_knumber))},
    "rejections": {"links": len(no), "documents": int(no.device_knumber.nunique()), "by_document": no.device_knumber.value_counts().to_dict()},
    "adjudication_composition": {smp: [len(g), int(g.device_knumber.nunique())] for smp, g in adj_all.groupby("sample")},
    "maude_z_test": {"recalled_with_reports": [x1, n1], "nonrecalled_with_reports": [x2, n2], "z": round(z, 2),
                     "p_two_sided": float(2 * norm.sf(abs(z))), "median_clearance_year": [float(r.year.median()), float(m.year.median())]},
    "maude_other_reports": int(mf["other"].sum()), "maude_unlabeled_reports": int(mf.iloc[:, 5].sum()),
    "maude_other_plus_unlabeled": int(mf["other"].sum() + mf.iloc[:, 5].sum()),
})
