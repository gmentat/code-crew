"""Extract the main-run workflow's final JSON result and write it to runs/main/.

Usage: uv run python scripts/materialize_main.py <path-to-workflow-output-file>

Layout matches what analyze.py expects:
  runs/main/<task_id>/passes/<persona>.json
  runs/main/<task_id>/syntheses/<mode>.json
  runs/main/<task_id>/single_<variant>.json
  runs/main/<task_id>/scores/<arm>.json
  runs/main/<task_id>/h3_similarity.json    (new in main run)
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
root = RUNS / "main"


def write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n")


passes = result.get("passes", {})
for tid, by_persona in passes.items():
    for persona, review in by_persona.items():
        if review is None:
            continue
        rec = {
            "persona": persona,
            "task_id": tid,
            "model": "claude-sonnet-via-workflow",
            "input_tokens": 0,
            "output_tokens": 0,
            "review": review,
            "raw": "",
        }
        write(root / tid / "passes" / f"{persona}.json", rec)

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
        write(root / tid / "syntheses" / f"{mode}.json", rec)

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
        write(root / tid / f"single_{variant}.json", rec)

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
        write(root / tid / "scores" / f"{arm}.json", rec)

# New in main run: H3 similarity matrix (LLM-classified pairwise persona divergence)
h3 = result.get("h3", {})
for tid, mat in h3.items():
    if mat is None:
        continue
    write(root / tid / "h3_similarity.json", mat)

n_pr = len(passes)
n_pass = sum(len(v) for v in passes.values())
n_synth = sum(len(v) for v in syntheses.values())
n_single = sum(len(v) for v in singles.values())
n_score = sum(len(v) for v in scores.values())
n_h3 = sum(1 for v in h3.values() if v)
print(
    f"materialized: {n_pr} PRs, {n_pass} passes, {n_synth} syntheses, "
    f"{n_single} single-agents, {n_score} scores, {n_h3} H3 matrices → {root}"
)
