"""09_figures.py — manuscript figures. Run from the repo root after Stage 6:  python 09_figures.py
Writes figures/fig_lineages.{png,pdf} and figures/fig_structure.{png,pdf}.
2026-10-28: uses the current definitions (Rule 2 v2 edges; post-recall = citing 510(k) received after the
recall was public, as in Stage 6) and repo-relative paths."""
import gzip, json, os
import pandas as pd, numpy as np, networkx as nx, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import deque
D = "data/"
OUT = "figures"; os.makedirs(OUT, exist_ok=True)
corpus=pd.read_csv(D+"corpus.csv",dtype=str); corpus["decision_year"]=pd.to_numeric(corpus.decision_year,errors="coerce")
edges=pd.read_csv(D+"predicate_edges.csv",dtype=str)      # Rule 2, primary
rec=pd.read_csv(D+"recalled_nodes.csv",dtype=str,keep_default_na=False)
rd=pd.to_datetime(rec.event_date_initiated,errors="coerce"); rd[rd.dt.year<1900]=pd.NaT
rdate=dict(zip(rec.k_number,rd)); rclass=dict(zip(rec.k_number,rec.worst_class))
year=dict(zip(corpus.k_number,corpus.decision_year))
recalled=set(rec.k_number)&set(corpus.k_number)
pub=dict(zip(*[pd.read_csv(D+"recall_public_dates.csv",dtype=str)[c] for c in ("k_number","recall_public_date")]))
pub={k:pd.Timestamp(v) for k,v in pub.items()}
received={r["k_number"]:pd.to_datetime(r.get("date_received"),errors="coerce")
          for r in json.load(gzip.open("snapshot/510k_raw.json.gz","rt"))}
EXPECTED=json.load(open(D+"expected_values.json"))
G=nx.DiGraph(); G.add_nodes_from(corpus.k_number)
for a,b in zip(edges.predicate_knumber,edges.device_knumber):
    if a in G and b in G: G.add_edge(a,b)
print("edges",G.number_of_edges())

# palette (dataviz reference): grey neutral for still-valid, red for recalled, root = filled triangle
GREY="#9a9993"; RED="#e34948"; INK="#0b0b0b"; INK2="#52514e"; EDGE="#d9d8d3"

# ---------- persistent recalled predicates & downstream reach ----------
persistent={}
for A in recalled:
    r=rdate.get(A)
    if A not in G or pd.isna(r): continue
    P=pub.get(A)
    if P is None: continue
    cites=[B for B in G.successors(A) if B not in recalled and pd.notna(received.get(B)) and received[B]>P]
    if cites: persistent[A]=len(cites)
assert len(persistent)==EXPECTED["persistent_predicates"], "figure set differs from Stage 6's persistent predicates"
def descendants_by_gen(root,maxgen=40):
    gen={root:0}; q=deque([root])
    while q:
        u=q.popleft()
        for v in G.successors(u):
            if v not in gen: gen[v]=gen[u]+1; q.append(v)
    return gen
reach={A:len(descendants_by_gen(A))-1 for A in persistent}
ranked=sorted(reach,key=lambda a:-reach[a])
top=ranked[:2]+[next(a for a in ranked if rclass.get(a)=="Class II")]+[next(a for a in ranked if rclass.get(a)=="Class I")]
print("top 4 by downstream reach:",[(a,reach[a],rclass.get(a),rdate[a].year) for a in top])

# ---------- Figure: lineages descending from four recalled predicates ----------
fig,axes=plt.subplots(1,4,figsize=(16,4.6))
for ax,A in zip(axes,top):
    gen=descendants_by_gen(A)
    sub=G.subgraph(gen).copy()
    bygen={}
    for n,g in gen.items(): bygen.setdefault(g,[]).append(n)
    pos={}
    for g,nodes in bygen.items():
        nodes=sorted(nodes,key=lambda n:(year.get(n) if pd.notna(year.get(n)) else 9999,n))
        k=len(nodes)
        ys=np.linspace(-1,1,k)*min(1,0.25*np.log1p(k)) if k>1 else [0]
        for n,y in zip(nodes,ys): pos[n]=(g,y)
    for u,v in sub.edges():
        x=[pos[u][0],pos[v][0]]; y=[pos[u][1],pos[v][1]]
        ax.plot(x,y,color=EDGE,lw=0.3,alpha=0.6,zorder=1)
    others=[n for n in sub if n!=A and n not in recalled]; recs=[n for n in sub if n!=A and n in recalled]
    ax.scatter([pos[n][0] for n in others],[pos[n][1] for n in others],s=6,color=GREY,zorder=2,lw=0)
    ax.scatter([pos[n][0] for n in recs],[pos[n][1] for n in recs],s=16,color=RED,zorder=3,lw=0)
    ax.scatter([0],[0],s=260,marker="^",color=RED,edgecolor=INK,lw=1.2,zorder=4)
    latest=max(year[n] for n in gen if n!=A and pd.notna(year.get(n)))
    cls=rclass.get(A,"n/a"); cls="class n/a" if cls=="n/a" else cls
    ax.set_title(f"{reach[A]:,} downstream devices\n{cls}; recalled {rdate[A].year}; cited through {int(latest)} (+{int(latest-rdate[A].year)} yr)",
                 fontsize=9,loc="left",color=INK)
    ax.set_xlabel("Generations downstream",fontsize=8,color=INK2)
    ax.set_xticks(range(0,max(gen.values())+1,5)); ax.tick_params(labelsize=7,colors=INK2)
    ax.set_yticks([]); 
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(EDGE)
fig.suptitle("Predicate lineages descending from recalled devices: the two with the largest downstream reach, and the largest-reach Class II and Class I recalls",x=0.01,ha="left",fontsize=11,color=INK,fontweight="bold")
from matplotlib.lines import Line2D
h=[Line2D([],[],marker="^",color=RED,markeredgecolor=INK,ls="",ms=11,label="recalled predicate (root)"),
   Line2D([],[],marker="o",color=RED,ls="",ms=6,label="descendant that was itself recalled"),
   Line2D([],[],marker="o",color=GREY,ls="",ms=4,label="descendant never recalled")]
fig.legend(handles=h,loc="lower left",bbox_to_anchor=(0.01,0.0),ncol=3,frameon=False,fontsize=8)
fig.text(0.99,0.02,"one column per citation generation; edges run predicate → citing device; within a column, devices are ordered by clearance year",ha="right",fontsize=8,color=INK2)
plt.tight_layout(rect=[0,0.06,1,0.93])
fig.savefig(f"{OUT}/fig_lineages.png",dpi=300); fig.savefig(f"{OUT}/fig_lineages.pdf")

# ---------- Figure: graph structure, three panels ----------
# a) chain depth: longest path from any root to each node (condensation)
C=nx.condensation(G); m=C.graph["mapping"]
order=list(nx.topological_sort(C)); depthC={}
for c in order: depthC[c]=max([depthC[p]+1 for p in C.predecessors(c)],default=0)
depth={n:depthC[m[n]] for n in G if G.degree(n)>0}
dvals=pd.Series(depth).value_counts().sort_index()
# b) out-degree of cited predicates
outdeg=pd.Series({n:G.out_degree(n) for n in G if G.out_degree(n)>0})
# c) decade coverage
corpus["decade"]=(corpus.decision_year//10*10).astype("Int64")
ingraph=set(n for n in G if G.degree(n)>0)
dec=corpus.groupby("decade").k_number.agg(total="count",ingraph=lambda s:s.isin(ingraph).sum())
fig,ax=plt.subplots(1,3,figsize=(15,4.4))
ax[0].bar(dvals.index,dvals.values,color=GREY,width=0.85)
ax[0].set_yscale("log"); ax[0].set_xlabel("Predicate-chain depth (hops from a root)"); ax[0].set_ylabel("Devices (log)")
ax[0].set_title(f"a  Chains reach {max(depth.values())} hops deep",loc="left",fontweight="bold")
ax[1].hist(outdeg.values,bins=range(1,outdeg.max()+2),color=GREY)
ax[1].set_yscale("log"); ax[1].set_xlabel("Times cited as a predicate (out-degree)"); ax[1].set_ylabel("Devices (log)")
ax[1].set_title("b  A few predicates are reused heavily",loc="left",fontweight="bold")
x=np.arange(len(dec)); ax[2].bar(x,dec.total,color=GREY,label="all devices"); ax[2].bar(x,dec.ingraph,color=RED,label="in graph (≥1 edge)")
ax[2].set_xticks(x); ax[2].set_xticklabels([f"{int(d)}s" for d in dec.index]); ax[2].set_xlabel("Decade of clearance"); ax[2].set_ylabel("Devices")
ax[2].set_title("c  Edge recovery improves after 2000",loc="left",fontweight="bold"); ax[2].legend(frameon=False,fontsize=8)
for a in ax:
    for s in ["top","right"]: a.spines[s].set_visible(False)
    a.tick_params(labelsize=8,colors=INK2)
plt.tight_layout(); fig.savefig(f"{OUT}/fig_structure.png",dpi=300); fig.savefig(f"{OUT}/fig_structure.pdf")
print("depth max",max(depth.values()),"| outdeg max",outdeg.max(),"| decades",dec.to_dict())
