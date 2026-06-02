"""Pre-build all pilot prompts as one JSON blob.

Used so the Workflow runner can dispatch agents in parallel without needing
filesystem access. Output: data/pilot_prompts.json
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
    pilot = read_json(DATA / "prs_pilot.json")
    bundle = {
        "personas": {p: load_persona_brief(p) for p in PERSONAS},
        "templates": {
            "synthesis_dissent": (PROMPTS / "synthesis_dissent.md").read_text(),
            "synthesis_consensus": (PROMPTS / "synthesis_consensus.md").read_text(),
            "single_agent": (PROMPTS / "single_agent.md").read_text(),
        },
        "review_output_instruction": REVIEW_OUTPUT_INSTRUCTION,
        "prs": [],
    }
    for rec in pilot:
        pr = load_pr_by_task_id(rec["task_id"])
        # Truncate review comments
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
    out_path = DATA / "pilot_prompts.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    total_chars = sum(len(json.dumps(p)) for p in bundle["prs"])
    print(
        f"wrote {out_path} ({out_path.stat().st_size:,} bytes; PR content ~{total_chars:,} chars)"
    )


if __name__ == "__main__":
    main()
