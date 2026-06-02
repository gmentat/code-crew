"""Extract triple-search workflow output into runs/triples/.

Layout:
  runs/triples/<task_id>/syntheses/<triple_key>.json
  runs/triples/<task_id>/scores/<triple_key>.json
"""

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
            if (
                "result" in obj
                and isinstance(obj["result"], dict)
                and "syntheses" in obj["result"]
            ):
                return obj["result"]
            if "syntheses" in obj:
                return obj
    except Exception:
        pass
    start = s.find('{"syntheses"')
    if start < 0:
        raise SystemExit("Could not locate `syntheses` root.")
    depth, i, in_str, esc = 0, start, False, False
    while i < len(s):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return json.loads(s[start : i + 1])
        i += 1
    raise SystemExit("unbalanced root")


result = extract_final_result(text)
root = RUNS / "triples"


def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


syntheses = result.get("syntheses", {})
for tid, by_key in syntheses.items():
    for key, synth in by_key.items():
        if synth is None:
            continue
        write(
            root / tid / "syntheses" / f"{key}.json",
            {"task_id": tid, "triple_key": key, "synthesis": synth},
        )

scores = result.get("scores", {})
for tid, by_key in scores.items():
    for key, judgement in by_key.items():
        if judgement is None:
            continue
        verdicts = judgement.get("verdicts", []) or []
        confirmed = sum(1 for v in verdicts if v.get("label") == "CONFIRMED")
        plausible = sum(1 for v in verdicts if v.get("label") == "PLAUSIBLE")
        fabricated = sum(1 for v in verdicts if v.get("label") == "FABRICATED")
        flagged_total = max(1, confirmed + plausible + fabricated)
        gt = judgement.get("ground_truth_recall", {}) or {}
        total_human = max(1, int(gt.get("total_human_comments") or 1))
        matched = int(gt.get("comments_matched_by_ai") or 0)
        write(
            root / tid / "scores" / f"{key}.json",
            {
                "task_id": tid,
                "triple_key": key,
                "metrics": {
                    "flagged_total": flagged_total,
                    "confirmed": confirmed,
                    "plausible": plausible,
                    "fabricated": fabricated,
                    "precision_raw": confirmed / flagged_total,
                    "fabrication_rate": fabricated / flagged_total,
                    "recall_raw": matched / total_human,
                    "total_human_comments": total_human,
                },
                "verdicts": verdicts,
                "ground_truth_recall": gt,
            },
        )

n_pr = len(syntheses)
n_synth = sum(len(v) for v in syntheses.values())
n_score = sum(len(v) for v in scores.values())
print(f"materialized: {n_pr} PRs, {n_synth} syntheses, {n_score} scores → {root}")
