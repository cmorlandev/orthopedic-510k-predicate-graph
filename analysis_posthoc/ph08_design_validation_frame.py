"""Sampling frame of the design-label validation sample (eMethods 8): recall events (initiated 1976 or later) linked to a
recalled predicate cited by at least 1 later device whose 510(k) was received after the recall was public, by FDA
category; and a check that the 120 sampled events in design_arm/validation/KEY_do_not_share.csv come from this frame
in the registered strata. Origin: validation/build_sample.py (seed 20261110)."""
from _common import *
from cause_map import FDA_ROOT_CAUSE_MAP as M

rows = []
for r in j("snapshot/recall_raw.json.gz"):
    ks = [k for k in (r.get("k_numbers") or []) if k in V]
    i = D(r.get("event_date_initiated"))
    if not ks or pd.isna(i) or i.year < 1976: continue
    rows.append(dict(event=str(r.get("res_event_number")), ks=ks, cause=r.get("root_cause_description") or ""))
R = pd.DataFrame(rows)
cited = {p for p, d in zip(edges.predicate_knumber, edges.device_knumber) if p in pub and pd.notna(recv.get(d)) and pub[p] < recv[d]}
R = R[R.ks.apply(lambda ks: any(k in cited for k in ks))]
E = R.groupby("event").cause.agg(lambda v: v.mode().iloc[0] if len(v.mode()) else "").reset_index()
E["fda_cat"] = E.cause.map(M).fillna("other_unclear")
out = {"frame_events": len(E), "frame_predicates": len(cited & set(R.ks.explode())), "by_category": E.fda_cat.value_counts().to_dict()}
kp = os.path.join(ROOT, "design_arm", "validation", "KEY_do_not_share.csv")
if os.path.exists(kp):
    K = pd.read_csv(kp, dtype={"event": str})
    out["sample_in_frame"] = int(K.event.isin(E.event).sum())
    out["sample_strata_match_frame"] = bool((K.set_index("event").fda_cat == E.set_index("event").fda_cat.reindex(K.event)).all())
    out["sample_by_category"] = K.fda_cat.value_counts().to_dict()
save("ph08_design_validation_frame", out)
