"""Build the prompt bundle for the triple-composition search.

Reuses the named persona blind-passes already in runs/personas/ — no
regeneration needed. The bundle includes per-PR passes for all 6
personas so any triple can be synthesized from existing data.

Output: data/triple_prompts.json
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (
    DATA,
    PERSONAS,
    PROMPTS,
    REVIEW_OUTPUT_INSTRUCTION,
    format_pr_for_review,
    load_pr_by_task_id,
    read_json,
    RUNS,
)


def main() -> None:
    prs = read_json(DATA / "prs_main.json")
    bundle = {
        "synthesis_template": (PROMPTS / "synthesis_consensus.md").read_text(),
        "review_output_instruction": REVIEW_OUTPUT_INSTRUCTION,
        "prs": [],
    }
    for rec in prs:
        tid = rec["task_id"]
        pr = load_pr_by_task_id(tid)
        hc = pr.get("human_review_comments") or []
        hc_brief = [
            {
                "author": c.get("author"),
                "path": c.get("path"),
                "body": (c.get("body") or "")[:500],
            }
            for c in hc[:20]
        ]
        # Load the existing blind-passes for this PR from the persona run.
        passes = {}
        for p in PERSONAS:
            path = RUNS / "personas" / tid / "passes" / f"{p}.json"
            if not path.exists():
                raise SystemExit(f"missing pass: {path}")
            d = read_json(path)
            # Strip raw text + keep just the review payload
            passes[p] = d["review"]
        bundle["prs"].append(
            {
                "task_id": tid,
                "repo": pr["repo"],
                "title": pr["title"],
                "language": pr.get("language"),
                "formatted_for_review": format_pr_for_review(pr, diff_max_chars=20_000),
                "human_review_comments": hc_brief,
                "passes": passes,
            }
        )
    out_path = DATA / "triple_prompts.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    print(
        f"wrote {out_path} ({out_path.stat().st_size:,} bytes; {len(bundle['prs'])} PRs)"
    )


if __name__ == "__main__":
    main()
