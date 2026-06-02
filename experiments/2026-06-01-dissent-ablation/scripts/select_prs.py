"""Deterministic stratified sample of PRs from SWE-PRBench eval_split.

Run: `uv run python scripts/select_prs.py [--pilot]`
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

import click
from datasets import load_dataset

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEED = 42

# Natural distribution in eval_split — target counts for the 80-PR full sample.
FULL_TARGETS = {
    "Python": 55,
    "Go": 10,
    "JavaScript": 8,
    "TypeScript": 5,
    "Java": 2,
}
FULL_N = sum(FULL_TARGETS.values())  # 80

# Main run — 50 PRs (fits workflow agent cap with 15 agents/PR including H3 classifier).
MAIN_TARGETS = {
    "Python": 34,
    "Go": 7,
    "JavaScript": 5,
    "TypeScript": 3,
    "Java": 1,
}
MAIN_N = sum(MAIN_TARGETS.values())  # 50

PILOT_N = 3  # Used for harness validation


def stratified_sample(
    rows: list[dict],
    key: str,
    targets: dict[str, int],
    seed: int,
) -> list[dict]:
    rng = random.Random(seed)
    by_key: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_key[r[key]].append(r)
    out: list[dict] = []
    for k, target in targets.items():
        pool = by_key.get(k, [])
        if len(pool) < target:
            raise SystemExit(
                f"Not enough rows for {key}={k!r}: have {len(pool)}, need {target}"
            )
        rng.shuffle(pool)
        out.extend(pool[:target])
    return out


@click.command()
@click.option("--pilot", is_flag=True, help="Sample 3 PRs (pilot mode).")
@click.option(
    "--main",
    "main_run",
    is_flag=True,
    help="Sample 50 PRs stratified (main run, fits Workflow agent cap).",
)
def main(pilot: bool, main_run: bool) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    ds = load_dataset("foundry-ai/swe-prbench", "eval_split")["train"]
    all_rows = list(ds)

    if pilot and main_run:
        raise SystemExit("Pass at most one of --pilot / --main")

    if pilot:
        # Pilot pool: PRs where reviewers requested changes (richer ground truth)
        candidate = [r for r in all_rows if r["has_requested_changes"]]
        rng = random.Random(SEED)
        rng.shuffle(candidate)
        # Prefer language diversity across the 3 picks
        seen_langs: set[str] = set()
        selected: list[dict] = []
        for r in candidate:
            if r["language"] not in seen_langs:
                selected.append(r)
                seen_langs.add(r["language"])
            if len(selected) >= PILOT_N:
                break
        # Fall back to filling from the same pool if we ran out of distinct languages
        for r in candidate:
            if len(selected) >= PILOT_N:
                break
            if r not in selected:
                selected.append(r)
        out_path = DATA / "prs_pilot.json"
    elif main_run:
        selected = stratified_sample(all_rows, "language", MAIN_TARGETS, SEED)
        out_path = DATA / "prs_main.json"
    else:
        selected = stratified_sample(all_rows, "language", FULL_TARGETS, SEED)
        out_path = DATA / "prs.json"

    record = [
        {
            "task_id": r["task_id"],
            "repo": r["repo"],
            "pr_number": r["pr_number"],
            "language": r["language"],
            "pr_type": r["pr_type"],
            "difficulty": r["difficulty"],
            "has_requested_changes": r["has_requested_changes"],
        }
        for r in selected
    ]
    out_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Selected {len(record)} PR(s) → {out_path}")
    for r in record:
        print(
            f"  {r['task_id']:30s} {r['language']:12s} {r['pr_type']:10s} "
            f"requested_changes={r['has_requested_changes']}"
        )


if __name__ == "__main__":
    main()
