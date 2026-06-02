"""Extract the workflow's final JSON result and write it to runs/pilot/ in
the per-PR layout analyze.py expects.

Usage: uv run python scripts/materialize_pilot.py <path-to-workflow-output-file>
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
    """Parse the workflow output. The top-level is a JSON object containing
    `result` (the script's return value)."""
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

    # Fallback: hunt for the `{"passes": ... }` substring spanning the document
    start = s.find('{"passes"')
    if start < 0:
        raise SystemExit("Could not locate the `passes` root in the output.")
    # Find the matching closing brace using a depth counter, tolerating strings.
    depth = 0
    i = start
    in_str = False
    esc = False
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
pilot_root = RUNS / "pilot"


def write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


# Passes: result["passes"][task_id][persona] -> review object (matches REVIEW_SCHEMA)
passes = result.get("passes", {})
for tid, by_persona in passes.items():
    for persona, review in by_persona.items():
        if review is None:
            continue
        rec = {
            "persona": persona,
            "task_id": tid,
            "model": "claude-sonnet-via-workflow",
            "input_tokens": 0,  # not measurable from workflow surface
            "output_tokens": 0,
            "review": review,
            "raw": "",
        }
        write(pilot_root / tid / "passes" / f"{persona}.json", rec)

# Syntheses
syntheses = result.get("syntheses", {})
for tid, by_mode in syntheses.items():
    for mode, synth in by_mode.items():
        if synth is None:
            continue
        rec = {
            "task_id": tid,
            "mode": mode,
            "model": "claude-sonnet-via-workflow",
            "input_tokens": 0,
            "output_tokens": 0,
            "synthesis": synth,
            "raw": "",
        }
        write(pilot_root / tid / "syntheses" / f"{mode}.json", rec)

# Singles
singles = result.get("singles", {})
for tid, by_variant in singles.items():
    for variant, review in by_variant.items():
        if review is None:
            continue
        rec = {
            "task_id": tid,
            "variant": variant,
            "model": "claude-sonnet-via-workflow",
            "input_tokens": 0,
            "output_tokens": 0,
            "review": review,
            "raw": "",
        }
        write(pilot_root / tid / f"single_{variant}.json", rec)

# Scores
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
        rec = {
            "task_id": tid,
            "arm": arm,
            "judge": "anthropic",
            "judge_model": "claude-sonnet-via-workflow",
            "input_tokens": 0,
            "output_tokens": 0,
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
            "raw": "",
        }
        write(pilot_root / tid / "scores" / f"{arm}.json", rec)


# Summary of what got written
n_pr = len(passes)
n_pass = sum(len(v) for v in passes.values())
n_synth = sum(len(v) for v in syntheses.values())
n_single = sum(len(v) for v in singles.values())
n_score = sum(len(v) for v in scores.values())
print(
    f"materialized: {n_pr} PRs, {n_pass} passes, {n_synth} syntheses, "
    f"{n_single} single-agents, {n_score} scores → {pilot_root}"
)
