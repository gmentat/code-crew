"""Judge each arm's flagged issues against human review comments.

Per the rubric (adapted from SWE-PRBench): each flagged issue is classified as
CONFIRMED (matches a real human reviewer concern), PLAUSIBLE (raises a substantive
concern not in the ground truth but defensible on inspection), or FABRICATED
(does not correspond to anything in the diff or is wrong).

We use OpenAI GPT-5.1 as the primary judge (to avoid Claude-judging-Claude bias).
For the pilot we can fall back to Claude as judge; flag that in output metadata.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from lib import (
    RUNS,
    call_anthropic,
    call_openai,
    extract_json,
    load_pr_by_task_id,
    read_json,
    write_json,
)

JUDGE_PROMPT = """
You are scoring AI-generated code-review feedback against real human reviewer comments
on the same pull request. Be strict but fair.

For each flagged issue, classify as:

- **CONFIRMED**: substantively matches at least one human reviewer comment
  (paraphrase OK, same concern).
- **PLAUSIBLE**: not in the human comments, but a competent reviewer would consider
  it a real, defensible concern about this code on inspection of the diff.
- **FABRICATED**: does not correspond to anything in the diff, or misreads the code,
  or is a generic non-issue ("consider adding tests" with no specific gap).

Output JSON exactly:

```json
{
  "verdicts": [
    {
      "index": <int>,
      "label": "CONFIRMED" | "PLAUSIBLE" | "FABRICATED",
      "reason": "<one sentence>"
    }
  ],
  "ground_truth_recall": {
    "total_human_comments": <int>,
    "comments_matched_by_ai": <int>,
    "comments_missed": ["<short description of each missed concern>"]
  }
}
```
""".strip()


def build_judge_prompt(pr: dict, flagged_issues: list[dict]) -> tuple[str, str]:
    human_comments = pr.get("human_review_comments") or []
    # Truncate comments for cost
    hc_brief = []
    for c in human_comments[:20]:
        body = (c.get("body") or "")[:500]
        hc_brief.append(
            {
                "author": c.get("author"),
                "path": c.get("path"),
                "body": body,
            }
        )
    indexed_issues = []
    for i, iss in enumerate(flagged_issues):
        indexed_issues.append(
            {
                "index": i,
                "severity": iss.get("severity"),
                "description": iss.get("description"),
                "detail": iss.get("detail", "")[:600],
                "file": iss.get("file"),
                "lines": iss.get("lines"),
            }
        )
    diff = pr.get("diff_patch") or ""
    if len(diff) > 30_000:
        diff = diff[:30_000] + "\n[...truncated]"
    system = JUDGE_PROMPT
    user = (
        f"# PR\n{pr['repo']} / {pr['title']}\n\n"
        f"## Human review comments (ground truth)\n"
        f"```json\n{json.dumps(hc_brief, indent=2)}\n```\n\n"
        f"## AI-flagged issues to judge\n"
        f"```json\n{json.dumps(indexed_issues, indent=2)}\n```\n\n"
        f"## Diff (for verification)\n```diff\n{diff}\n```"
    )
    return system, user


def issues_from(arm: str, base: Path) -> list[dict]:
    if arm in ("dissent", "consensus"):
        rec = read_json(base / "syntheses" / f"{arm}.json")
        return rec["synthesis"].get("issues", [])
    if arm in ("budget", "naive"):
        rec = read_json(base / f"single_{arm}.json")
        return rec["review"].get("issues", [])
    raise ValueError(arm)


@click.command()
@click.option("--task-id", required=True)
@click.option(
    "--arm",
    type=click.Choice(["dissent", "consensus", "budget", "naive"]),
    required=True,
)
@click.option("--run-dir", default="runs/pilot")
@click.option("--judge", type=click.Choice(["openai", "anthropic"]), default="openai")
@click.option("--judge-model", default=None)
def main(
    task_id: str, arm: str, run_dir: str, judge: str, judge_model: str | None
) -> None:
    base = RUNS / run_dir.split("runs/")[-1] / task_id
    pr = load_pr_by_task_id(task_id)
    flagged = issues_from(arm, base)
    system, user = build_judge_prompt(pr, flagged)
    if judge == "openai":
        resp = call_openai(system, user, model=judge_model or "gpt-5.1")
    else:
        resp = call_anthropic(
            system, user, model=judge_model or "claude-sonnet-4-5", max_tokens=4096
        )
    parsed = extract_json(resp["text"])
    # Compute headline metrics
    verdicts = parsed.get("verdicts", [])
    confirmed = sum(1 for v in verdicts if v["label"] == "CONFIRMED")
    plausible = sum(1 for v in verdicts if v["label"] == "PLAUSIBLE")
    fabricated = sum(1 for v in verdicts if v["label"] == "FABRICATED")
    flagged_total = max(1, confirmed + plausible + fabricated)
    gt = parsed.get("ground_truth_recall", {})
    total_human = max(1, int(gt.get("total_human_comments", 1)))
    matched = int(gt.get("comments_matched_by_ai", 0))
    out = {
        "task_id": task_id,
        "arm": arm,
        "judge": judge,
        "judge_model": resp["model"],
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
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
        "raw": resp["text"],
    }
    out_path = base / "scores" / f"{arm}.json"
    write_json(out_path, out)
    print(f"wrote {out_path}")
    m = out["metrics"]
    print(
        f"  arm={arm:9s} flagged={m['flagged_total']:2d} "
        f"confirmed={m['confirmed']:2d} fabricated={m['fabricated']:2d} "
        f"precision={m['precision_raw']:.2f} recall={m['recall_raw']:.2f}"
    )


if __name__ == "__main__":
    main()
