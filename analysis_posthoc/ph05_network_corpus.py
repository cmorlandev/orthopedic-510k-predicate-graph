"""Corpus and network descriptions (Results, eResults, eMethods 1 and 2, eTable 2): connectivity of recalled devices,
chronology of links, De Novo records, product codes with devices, readable summaries by clearance period, text-file
sizes, coverage categories, and H2 devices by predicate clearance era.
Origin: red-team r1_compute.py (sections 4, 5, 8), r2_compute.py (sections 3, 5), r4_compute.py (R4-6)."""
from _common import *
import networkx as nx

es = set(zip(edges.predicate_knumber, edges.device_knumber))
G = nx.DiGraph(); G.add_edges_from(es)
U = G.to_undirected(); U.add_nodes_from(corpus.k_number)
lcc = max(nx.connected_components(U), key=len)
nonrec = U.number_of_nodes() - len(recset)
dd = dict(zip(corpus.k_number, D(corpus.decision_date)))
inverted = [(p, d) for p, d in es if dd.get(p) > dd.get(d)]
mutual = [(p, d) for p, d in es if (d, p) in es]
den = corpus[corpus.k_number.str.startswith("DEN")]
pc = corpus.product_codes.fillna("").str.split(r"[;,| ]+").explode(); pc = pc[pc != ""]; vc = pc.value_counts()
snapcodes = json.load(open(os.path.join(ROOT, "snapshot", "SNAPSHOT.json")))["product_codes"]
pd.DataFrame({"product_code": snapcodes, "devices": [int(vc.get(x, 0)) for x in snapcodes]}).to_csv(
    os.path.join(OUT, "etable2_product_code_counts.csv"), index=False)
ts = pd.read_csv(os.path.join(ROOT, "TEXT_SNAPSHOT_files.csv"))
by = dict(zip(ts.k_number, ts.bytes)); readable = corpus.k_number.map(lambda k: by.get(k, 0) > 10)
periods = {f"{lo}-{hi}": [int(readable[(corpus.decision_year >= lo) & (corpus.decision_year <= hi)].sum()),
                          int(((corpus.decision_year >= lo) & (corpus.decision_year <= hi)).sum())]
           for lo, hi in [(1976, 2000), (2001, 2005), (2006, 2026)]}
cov = csv("coverage_diagnostic.csv")
h2 = [a for a, p in pub.items() if a in G and pd.notna(p)
      and (s := [b for b in G.successors(a) if pd.notna(recv.get(b))]) and all(recv[b] > p for b in s)]

save("ph05_network_corpus", {
    "devices": len(V), "links": len(es),
    "largest_component": len(lcc), "recalled_with_link": sum(1 for k in recset if U.degree(k) > 0),
    "recalled_in_largest_component": len(recset & lcc),
    "nonrecalled_in_largest_component": [len(lcc - recset), nonrec, round(100 * len(lcc - recset) / nonrec, 1)],
    "links_predicate_cleared_after_citing": len(inverted), "mutual_links": len(mutual),
    "de_novo_records": len(den), "de_novo_in_links": int(edges.predicate_knumber.isin(den.k_number).sum() + edges.device_knumber.isin(den.k_number).sum()),
    "de_novo_recalled": len(set(den.k_number) & recset),
    "product_codes_registered": len(snapcodes), "product_codes_with_devices": len(set(vc.index) & set(snapcodes)),
    "devices_with_more_than_1_code": int(corpus.product_codes.fillna("").str.contains(r"[;,| ]").sum()),
    "readable_by_clearance_period": periods,
    "text_files": {"zero_bytes": int((ts.bytes == 0).sum()), "le_10_bytes": int((ts.bytes <= 10).sum()), "files": len(ts)},
    "coverage_categories": cov.coverage.value_counts().to_dict(),
    "H2_devices": len(h2), "H2_predicate_cleared_2000_or_earlier": sum(year[a] <= 2000 for a in h2),
    "H2_predicate_cleared_2001_or_later": sum(year[a] >= 2001 for a in h2),
})
