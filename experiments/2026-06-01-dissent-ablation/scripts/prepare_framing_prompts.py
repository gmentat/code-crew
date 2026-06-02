"""Build prompt bundle for the persona-framing A/B (direct-named K+H+T).

Output: data/framing_prompts.json. Identical PR shape and synthesis template as
the persona run, but loads briefs from *_agent_direct.md instead of *_agent.md.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA, PROMPTS, REVIEW_OUTPUT_INSTRUCTION, format_pr_for_review, load_pr_by_task_id, read_json

TRIPLE = ["knuth", "hickey", "torvalds"]


def main() -> None:
    prs = read_json(DATA / "prs_main.json")
    bundle = {
        "personas_direct": {
            p: (PROMPTS / f"{p}_agent_direct.md").read_text() for p in TRIPLE
        },
        "synthesis_template": (PROMPTS / "synthesis_consensus.md").read_text(),
        "review_output_instruction": REVIEW_OUTPUT_INSTRUCTION,
        "prs": [],
    }
    for rec in prs:
        pr = load_pr_by_task_id(rec["task_id"])
        hc = pr.get("human_review_comments") or []
        hc_brief = [
            {"author": c.get("author"), "path": c.get("path"),
             "body": (c.get("body") or "")[:500]}
            for c in hc[:20]
        ]
        bundle["prs"].append({
            "task_id": pr["task_id"],
            "repo": pr["repo"],
            "title": pr["title"],
            "language": pr.get("language"),
            "formatted_for_review": format_pr_for_review(pr, diff_max_chars=20_000),
            "human_review_comments": hc_brief,
        })
    out_path = DATA / "framing_prompts.json"
    out_path.write_text(json.dumps(bundle, indent=2))
    print(f"wrote {out_path} ({out_path.stat().st_size:,} bytes; {len(bundle['prs'])} PRs)")


if __name__ == "__main__":
    main()
