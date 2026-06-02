"""Pre-build the prompts bundle for the persona-ablation run.

Extends the main-run bundle with:
  - the generic-reviewer brief
  - a consolidated 'synthesis' prompt (drops the dissent vs consensus distinction)

Output: data/persona_prompts.json
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
    load_persona_brief,
    load_pr_by_task_id,
    read_json,
)


def main() -> None:
    prs = read_json(DATA / "prs_main.json")
    bundle = {
        "personas": {p: load_persona_brief(p) for p in PERSONAS},
        "generic_reviewer": (PROMPTS / "generic_reviewer.md").read_text(),
        # Use the consensus synthesis (the survivor of the dissent ablation).
        # This is the consolidated synthesis prompt going forward.
        "synthesis_template": (PROMPTS / "synthesis_consensus.md").read_text(),
        "review_output_instruction": REVIEW_OUTPUT_INSTRUCTION,
        "prs": [],
    }
    for rec in prs:
        pr = load_pr_by_task_id(rec["task_id"])
        hc = pr.get("human_review_comments") or []
        hc_brief = []
        for c in hc[:20]:
            hc_brief.append(
                {
                    "author": c.get("author"),
                    "path": c.get("path"),
                    "body": (c.get("body") or "")[:500],
                }
            )
        bundle["prs"].append(
            {
                "task_id": pr["task_id"],
                "repo": pr["repo"],
                "title": pr["title"],
                "language": pr.get("language"),
                "pr_type": pr.get("pr_type"),
                "has_requested_changes": pr.get("has_requested_changes"),
                "formatted_for_review": format_pr_for_review(pr, diff_max_chars=30_000),
                "human_review_comments": hc_brief,
                "num_human_comments": len(hc),
            }
        )
    out_path = DATA / "persona_prompts.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    print(
        f"wrote {out_path} ({out_path.stat().st_size:,} bytes; {len(bundle['prs'])} PRs)"
    )


if __name__ == "__main__":
    main()
