"""Extract a persona-ablation workflow's final result and write it to runs/personas/.

Usage: uv run python scripts/materialize_persona.py <transcript-path>

Layout:
  runs/personas/<task_id>/passes/<name>.json    (named persona OR generic_N)
  runs/personas/<task_id>/syntheses/<arm>.json  (named-6 / generic-6 / triple-A / triple-B / pair-TL)
  runs/personas/<task_id>/scores/<arm>.json     (solo-* and synthesis arms)
  runs/personas/<task_id>/h3_generic.json       (generic-6 manipulation check)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import RUNS  # noqa

WF_OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin")
text = WF_OUT.read_text()


def extract_final_result(s: str) -> dict:
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            if (
                "result" in obj
                and isinstance(obj["result"], dict)
                and "passes" in obj["result"]
            ):
                return obj["result"]
            if "passes" in obj:
                return obj
    except Exception:
        pass
    start = s.find('{"passes"')
    if start < 0:
        raise SystemExit("Could not locate the `passes` root in the output.")
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
    raise SystemExit("Could not find balanced JSON root in output.")


result = extract_final_result(text)
root = RUNS / "personas"


def write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


passes = result.get("passes", {})
for tid, by_name in passes.items():
    for name, review in by_name.items():
        if review is None:
            continue
        write(
            root / tid / "passes" / f"{name}.json",
            {
                "name": name,
                "task_id": tid,
                "review": review,
            },
        )

syntheses = result.get("syntheses", {})
for tid, by_arm in syntheses.items():
    for arm, synth in by_arm.items():
        if synth is None:
            continue
        write(
            root / tid / "syntheses" / f"{arm}.json",
            {
                "task_id": tid,
                "arm": arm,
                "synthesis": synth,
            },
        )

scores = result.get("scores", {})
for tid, by_arm in scores.items():
    for arm, judgement in by_arm.items():
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
            root / tid / "scores" / f"{arm}.json",
            {
                "task_id": tid,
                "arm": arm,
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

h3 = result.get("h3", {})
for tid, mat in h3.items():
    if mat is None:
        continue
    write(root / tid / "h3_generic.json", mat)

n_pr = len(passes)
n_pass = sum(len(v) for v in passes.values())
n_synth = sum(len(v) for v in syntheses.values())
n_score = sum(len(v) for v in scores.values())
n_h3 = sum(1 for v in h3.values() if v)
print(
    f"materialized: {n_pr} PRs, {n_pass} passes, {n_synth} syntheses, "
    f"{n_score} scores, {n_h3} H3 matrices → {root}"
)
