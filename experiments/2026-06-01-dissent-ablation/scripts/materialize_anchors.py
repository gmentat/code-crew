"""Extract framing-ablation workflow result into runs/framing/."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import RUNS

WF_OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin")
text = WF_OUT.read_text()


def extract_final_result(s: str) -> dict:
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            if "result" in obj and isinstance(obj["result"], dict) and "passes" in obj["result"]:
                return obj["result"]
            if "passes" in obj:
                return obj
    except Exception:
        pass
    start = s.find('{"passes"')
    if start < 0:
        raise SystemExit("Could not locate `passes` root.")
    depth, i, in_str, esc = 0, start, False, False
    while i < len(s):
        ch = s[i]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0: return json.loads(s[start:i+1])
        i += 1
    raise SystemExit("unbalanced root")


result = extract_final_result(text)
root = RUNS / "anchored"


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


passes = result.get("passes", {})
for tid, by_persona in passes.items():
    for persona, review in by_persona.items():
        if review is None: continue
        write(root / tid / "passes" / f"{persona}_anchored.json",
              {"persona": persona, "anchored": "anchored", "task_id": tid, "review": review})

syntheses = result.get("syntheses", {})
for tid, synth in syntheses.items():
    if synth is None: continue
    write(root / tid / "syntheses" / "anchored.json",
          {"task_id": tid, "anchored": "anchored", "synthesis": synth})

scores = result.get("scores", {})
for tid, judgement in scores.items():
    if judgement is None: continue
    verdicts = judgement.get("verdicts", []) or []
    confirmed  = sum(1 for v in verdicts if v.get("label") == "CONFIRMED")
    plausible  = sum(1 for v in verdicts if v.get("label") == "PLAUSIBLE")
    fabricated = sum(1 for v in verdicts if v.get("label") == "FABRICATED")
    flagged_total = max(1, confirmed + plausible + fabricated)
    gt = judgement.get("ground_truth_recall", {}) or {}
    total_human = max(1, int(gt.get("total_human_comments") or 1))
    matched = int(gt.get("comments_matched_by_ai") or 0)
    write(root / tid / "scores" / "anchored.json", {
        "task_id": tid, "anchored": "anchored",
        "metrics": {
            "flagged_total": flagged_total,
            "confirmed": confirmed, "plausible": plausible, "fabricated": fabricated,
            "precision_raw": confirmed / flagged_total,
            "fabrication_rate": fabricated / flagged_total,
            "recall_raw": matched / total_human,
            "total_human_comments": total_human,
        },
        "verdicts": verdicts, "ground_truth_recall": gt,
    })

n_pr = len(passes)
n_pass = sum(len(v) for v in passes.values())
n_synth = sum(1 for v in syntheses.values() if v)
n_score = sum(1 for v in scores.values() if v)
print(f"materialized: {n_pr} PRs, {n_pass} passes, {n_synth} syntheses, {n_score} scores → {root}")
