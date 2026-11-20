"""Table 2 of the article and eMethods 7: recall status of the predicate when each post-recall citation was received
(open, all terminated, between recalls), open design-related recalls, corporate family of the citing company,
timing categories, device-level family split, and same-family matches via the family map vs the first-word fallback.
Origin: tables/t3.py (second part), red-team r4_compute.py R4-1, r2_compute.py, r2_family.py, r3_compute.py."""
from _common import *
import firm_families as ff
from cause_map import FDA_ROOT_CAUSE_MAP as M

rr = j("snapshot/recall_raw.json.gz")
L = {}
for r in rr:
    i, t = D(r.get("event_date_initiated")), D(r.get("event_date_terminated"))
    for k in r.get("k_numbers") or []:
        k = str(k).strip().upper()
        if k in V:
            L.setdefault(k, []).append((i, t, r.get("recall_status"), M.get(r.get("root_cause_description"), "other_unclear")))

def valid(i):   # pipeline rule (Stage 5, D8): a recall counts only if its initiation date is valid (1976 or later)
    return pd.notna(i) and i.year >= 1976

def status(p, b):
    recs = [x for x in L.get(p, []) if valid(x[0])]
    op = [x for x in recs if x[0] <= b and (pd.isna(x[1]) or x[1] >= b)]
    if op: return "open", any(x[3] == "design" for x in op)
    if any(x[0] > b for x in recs): return "between", False
    return "closed", False
st = [status(p, b) for p, b in zip(A.predicate, A.b_received)]
A["status"] = [s for s, _ in st]; A["open_design"] = [d for _, d in st]
A["same_fam"] = A.same_family.astype(str) == "True"

def open_undated_closed(p, b):   # sensitivity: undated Terminated/Completed records treated as closed
    for i, t, s, _ in L.get(p, []):
        if not valid(i) or i > b: continue
        if pd.notna(t) and t >= b: return True
        if pd.isna(t) and s == "Open, Classified": return True
    return False

tab = {s: {"citations": int((A.status == s).sum()), "pct": round(100 * (A.status == s).mean(), 1),
           "same_family": int(((A.status == s) & A.same_fam).sum()), "other": int(((A.status == s) & ~A.same_fam).sum()),
           "predicates": int(A[A.status == s].predicate.nunique()), "citing_devices": int(A[A.status == s].citing.nunique())}
       for s in ["open", "closed", "between"]}
fam = A.groupby("predicate").same_fam.agg(["any", "all"])
gap = (A.b_received - A.recall_public).dt.days
allc = ct
fam_dev = {"only_same_family": int(fam["all"].sum()), "no_same_family": int((~fam["any"]).sum()),
           "both": int((fam["any"] & ~fam["all"]).sum()), "at_least_1_other_family": int((~fam["all"]).sum()),
           "predicates": len(fam)}

# family map vs first-word fallback for the same-family citations
app = dict(zip(corpus.k_number, corpus.applicant))
firms = {}
for r in rr:
    for k in r.get("k_numbers") or []:
        k = str(k).strip().upper()
        if k in recset: firms.setdefault(k, set()).add(r.get("recalling_firm") or "")
def mapmatch(a, b, when):
    mb = ff.memberships(app.get(b))
    for n in [app.get(a)] + sorted(firms.get(a, set())):
        ma = ff.memberships(n)
        if ma and mb:
            ga = {g for g, s in ma if s is None or s <= when}; gb = {g for g, s in mb if s is None or s <= when}
            if ga & gb: return True
    return False
SF = A[A.same_fam]
via_map = sum(mapmatch(a, b, w) for a, b, w in zip(SF.predicate, SF.citing, SF.b_received))

save("ph02_recall_status_family", {
    "post_recall_citations": len(A), "predicates": int(A.predicate.nunique()), "citing_devices": int(A.citing.nunique()),
    "status": tab,
    "open_design_citations": int(A.open_design.sum()), "open_design_devices": int(A[A.open_design].citing.nunique()),
    "open_if_undated_terminated_closed": int(sum(open_undated_closed(p, b) for p, b in zip(A.predicate, A.b_received))),
    "same_family_citations": int(A.same_fam.sum()), "other_company_citations": int((~A.same_fam).sum()),
    "family_device_level": fam_dev,
    "same_family_via_map": int(via_map), "same_family_first_word_only": int(len(SF) - via_map),
    "timing": {"after_initiation_total": len(allc), "after_public": int((allc.category == "A").sum()),
               "before_public": int((allc.category == "B").sum()), "before_initiation": int((allc.category == "C").sum()), "unknown_order": int((allc.category == "U").sum()),
               "gt90d": int((gap > 90).sum()), "gt180d": int((gap > 180).sum()),
               "exactly_90d": int((gap == 90).sum()), "exactly_180d": int((gap == 180).sum())},
})
