"""Run every post hoc script and check its output against the values reported in the manuscript and supplement.
    python analysis_posthoc/run_all.py          (from the repository root, about 2 minutes)
Prints PASS/FAIL for each reported value and exits non-zero if any value differs."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["ph01_table1_figure2", "ph02_recall_status_family", "ph03_timing", "ph04_as_registered",
           "ph05_network_corpus", "ph06_validation_maude", "ph07_severity_dating", "ph08_design_validation_frame"]
for s in SCRIPTS:
    r = subprocess.run([sys.executable, os.path.join(HERE, s + ".py")], capture_output=True, text=True)
    if r.returncode: print(r.stderr); sys.exit(f"{s} failed")
    print(f"ran {s}")
R = {s: json.load(open(os.path.join("data", "posthoc", s + ".json"))) for s in SCRIPTS}
T1 = {row["group"]: row for row in R["ph01_table1_figure2"]["table1"]}

def get(path):
    s, *keys = path.split("."); x = R[s]
    for k in keys: x = x[int(k)] if isinstance(x, list) else x[k]
    return x
EXPECTED = json.load(open(os.path.join(HERE, "reported_values.json")))
fails = 0
for path, want in EXPECTED.items():
    if path.startswith("T1|"):
        _, group, col = path.split("|"); got = T1[group][col]
        if col == "km5": got = got[0]
    else:
        got = get(path)
    ok = got == want; fails += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {path:70} reported={want!s:22} computed={got}")
print(f"\n{len(EXPECTED) - fails} of {len(EXPECTED)} reported values reproduced")
sys.exit(1 if fails else 0)
