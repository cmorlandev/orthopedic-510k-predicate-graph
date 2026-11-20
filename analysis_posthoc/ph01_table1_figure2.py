"""Table 1 of the article (persistence by recall class, body region, and year made public, with 5-year KM),
Figure 2 (KM cumulative incidence of a first post-recall citation by prior predicate use, numbers at risk),
and eTable 8 (cumulative incidence by year made public, not estimable beyond each cohort's follow-up).
Origin: tables/t.py, t3.py (first part) and fig2.py from the Nov 2026 manuscript work."""
from _common import *

def regnum(r):
    x = (r.get("openfda") or {}).get("regulation_number"); x = x[0] if isinstance(x, list) and x else x
    return x or ""
reg = {r["k_number"]: regnum(r) for r in raw510}
SPINE = {"888.3047", "888.3050", "888.3060", "888.3070", "888.3071", "888.3075", "888.3080", "888.3085"}
def region(rn):
    try: v = float(rn)
    except (TypeError, ValueError): return "Unknown"
    if rn in SPINE: return "Spine"
    if 888.3310 <= v <= 888.3400: return "Hip"
    if 888.3500 <= v <= 888.3610: return "Knee"
    if 888.3010 <= v <= 888.3046: return "Fracture fixation, cement, and bone fillers"
    return "Shoulder and other joints"

R = pubdf.copy(); R["pub"] = D(R.recall_public_date); R = R[R.pub.notna()]
R = R.merge(recnodes[["k_number", "worst_class"]], on="k_number", how="left")
R["region"] = R.k_number.map(lambda k: region(reg.get(k)))
R["cls"] = R.worst_class.fillna("Not available").replace({"": "Not available"})
R["era"] = pd.cut(R.pub.dt.year, [0, 2005, 2015, 2100], labels=["2005 or earlier", "2006 to 2015", "2016 to 2026"])
e2 = edges.copy(); e2["rec"] = e2.device_knumber.map(recv)
first_any = e2.groupby("predicate_knumber").rec.min()
R["first_cite"] = R.k_number.map(first_any)
R["first_after"] = R.first_cite.notna() & (R.first_cite > R.pub)
R["prior"] = R.first_cite.notna() & (R.first_cite < R.pub)
A["rec"] = A.b_received
g = A.groupby("predicate").agg(n=("citing", "size"), last=("rec", "max"), first=("rec", "min"))
R = R.merge(g, left_on="k_number", right_index=True, how="left")
R["persist"] = R.n.notna()
R["yrs_last"] = (R["last"] - R.pub).dt.days / 365.25
R["t"] = (R["first"].fillna(END) - R.pub).dt.days / 365.25
R["e"] = R["first"].notna().astype(int)
cit_dev = A.groupby("predicate").citing.apply(set)

def row(name, s):
    p = s[s.persist]; devs = set().union(*[cit_dev[k] for k in p.k_number]) if len(p) else set()
    q = p.yrs_last.quantile([.25, .5, .75]) if len(p) else None
    return dict(group=name, recalled=len(s), cited_after=len(p), pct=round(100 * len(p) / len(s), 1),
                citations=int(p.n.sum()), later_devices=len(devs),
                median_years_to_last=None if q is None else [round(q[.5], 1), round(q[.25], 1), round(q[.75], 1)],
                over_10y=int((p.yrs_last > 10).sum()), first_cited_after=int(s.first_after.sum()),
                km5=km_at(s.t.values, s.e.values, 5))
rows = [row("All recalled devices", R)]
rows += [row("Recall class: " + c, R[R.cls == c]) for c in ["Class I", "Class II", "Class III", "Not available"]]
rows += [row("Region: " + r_, R[R.region == r_]) for r_ in ["Hip", "Knee", "Spine", "Shoulder and other joints",
                                                             "Fracture fixation, cement, and bone fillers", "Unknown"]
         if (R.region == r_).any()]
rows += [row("Recall made public: " + e_, R[R.era == e_]) for e_ in ["2005 or earlier", "2006 to 2015", "2016 to 2026"]]
T1 = pd.DataFrame(rows); T1.to_csv(os.path.join(OUT, "table1.csv"), index=False)

# Figure 2 and eTable 8
groups = {"All recalled devices": R, "Cited as a predicate before recall": R[R.prior], "Not cited before recall": R[~R.prior]}
fig2 = {k: {"n": len(s), "events": int(s.e.sum()), **{f"{a}y": km_at(s.t.values, s.e.values, a) for a in (1, 5, 10)},
            "at_risk": {y: int((s.t >= y).sum()) for y in range(0, 16, 3)}} for k, s in groups.items()}
eras = {"All": R, **{e_: R[R.era == e_] for e_ in ["2005 or earlier", "2006 to 2015", "2016 to 2026"]}}
et8 = {k: {"n": len(s), "events": int(s.e.sum()), "max_followup_y": round(float(((END - s.pub).dt.days / 365.25).max()), 2),
           **{f"{a}y": km_at(s.t.values, s.e.values, a) for a in (1, 5, 10, 15)},
           "at_risk_10y": int((s.t >= 10).sum()), "at_risk_15y": int((s.t >= 15).sum())} for k, s in eras.items()}

try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7.4, 5.6)); ax = fig.add_axes([0.27, 0.36, 0.56, 0.58])
    for (name, s), col in zip(groups.items(), ["#3a3a38", "#2a78d6", "#eb6834"]):
        c = km_curve(s.t, s.e)
        ax.step(c.time, c.cuminc, where="post", color=col, lw=2, label=name)
        ax.fill_between(c.time, c.lo, c.hi, step="post", color=col, alpha=0.12, lw=0)
    ax.set_xlim(0, 15); ax.set_ylim(0, 80); ax.set_xticks(range(0, 16, 3))
    ax.set_xlabel("Years since recall was made public", fontsize=9); ax.set_ylabel("Cited as a predicate, %", fontsize=9)
    for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    tb = fig.add_axes([0.27, 0.04, 0.56, 0.2]); tb.axis("off"); tb.set_xlim(0, 15); tb.set_ylim(0, 4)
    tb.text(-0.6, 3.6, "No. at risk", fontsize=8, fontweight="bold")
    for i, (name, s) in enumerate(groups.items()):
        tb.text(-0.6, 2.6 - i, name.replace("Cited as a predicate before recall", "Cited before recall"), fontsize=7.5, ha="right")
        for y in range(0, 16, 3): tb.text(y, 2.6 - i, f"{int((s.t >= y).sum()):,}", fontsize=7.5, ha="center")
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    for ext in ["png", "pdf"]: fig.savefig(os.path.join(OUT, "figures", f"Figure2_cumulative_reuse.{ext}"), dpi=300)
except ImportError:
    print("matplotlib not installed; figure skipped")

save("ph01_table1_figure2", {"table1": rows, "figure2": fig2, "etable8": et8,
                            "prior_use": int(R.prior.sum()), "no_prior_use": int((~R.prior).sum())})
