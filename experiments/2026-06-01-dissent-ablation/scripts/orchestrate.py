"""Orchestrates the full 4-arm protocol across selected PRs.

Pilot mode: 3 PRs, judge falls back to Claude if no OPENAI_API_KEY (deviation recorded).
Full mode: 80 PRs, requires both keys.
"""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import click

from lib import (
    PERSONAS,
    RUNS,
    iter_selected_prs,
    read_json,
)

SCRIPTS = Path(__file__).resolve().parent


def sh(cmd: list[str]) -> None:
    print("$ " + " ".join(cmd))
    r = subprocess.run(cmd, check=False)
    if r.returncode != 0:
        print(f"  ! exited {r.returncode}", file=sys.stderr)


def run_pass(task_id: str, persona: str, run_dir: str) -> None:
    sh(
        [
            "uv",
            "run",
            "python",
            str(SCRIPTS / "crew_pass.py"),
            "--task-id",
            task_id,
            "--persona",
            persona,
            "--run-dir",
            run_dir,
        ]
    )


def run_synthesis(task_id: str, mode: str, run_dir: str) -> None:
    sh(
        [
            "uv",
            "run",
            "python",
            str(SCRIPTS / "synthesize.py"),
            "--task-id",
            task_id,
            "--mode",
            mode,
            "--run-dir",
            run_dir,
        ]
    )


def run_single(task_id: str, variant: str, run_dir: str, budget: int) -> None:
    args = [
        "uv",
        "run",
        "python",
        str(SCRIPTS / "single_agent.py"),
        "--task-id",
        task_id,
        "--variant",
        variant,
        "--run-dir",
        run_dir,
    ]
    if variant == "budget":
        args.extend(["--budget", str(budget)])
    sh(args)


def run_score(task_id: str, arm: str, run_dir: str, judge: str) -> None:
    sh(
        [
            "uv",
            "run",
            "python",
            str(SCRIPTS / "score.py"),
            "--task-id",
            task_id,
            "--arm",
            arm,
            "--run-dir",
            run_dir,
            "--judge",
            judge,
        ]
    )


def median_crew_tokens(run_dir: str, task_ids: list[str]) -> int:
    """Compute realized median total tokens (in+out) across crew personas+synthesis."""
    totals: list[int] = []
    for tid in task_ids:
        base = RUNS / run_dir.split("runs/")[-1] / tid
        s = 0
        for p in PERSONAS:
            rec = read_json(base / "passes" / f"{p}.json")
            s += rec.get("input_tokens", 0) + rec.get("output_tokens", 0)
        synth = read_json(base / "syntheses" / "dissent.json")
        s += synth.get("input_tokens", 0) + synth.get("output_tokens", 0)
        totals.append(s)
    totals.sort()
    n = len(totals)
    return totals[n // 2] if n else 8000


@click.command()
@click.option("--pilot", is_flag=True, help="Run on data/prs_pilot.json (3 PRs).")
@click.option("--full", is_flag=True, help="Run on data/prs.json (80 PRs).")
@click.option("--workers", default=4, type=int, help="Parallel API calls.")
def main(pilot: bool, full: bool, workers: int) -> None:
    if pilot == full:
        raise SystemExit("Pass exactly one of --pilot / --full")
    run_dir = "runs/pilot" if pilot else "runs/full"
    judge = "openai" if os.environ.get("OPENAI_API_KEY") else "anthropic"
    if judge == "anthropic" and not pilot:
        raise SystemExit("Full run requires OPENAI_API_KEY for the primary judge.")
    prs = list(iter_selected_prs(pilot))
    print(f"Orchestrating {len(prs)} PRs, judge={judge}, workers={workers}")
    task_ids = [r["task_id"] for r in prs]

    # Phase 1: crew passes (6 personas × N PRs in parallel)
    print("\n=== PHASE 1: crew passes ===")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(run_pass, tid, p, run_dir) for tid in task_ids for p in PERSONAS
        ]
        for f in as_completed(futures):
            f.result()

    # Phase 2: syntheses (dissent + consensus per PR)
    print("\n=== PHASE 2: syntheses ===")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(run_synthesis, tid, m, run_dir)
            for tid in task_ids
            for m in ("dissent", "consensus")
        ]
        for f in as_completed(futures):
            f.result()

    # Phase 3: single-agent baselines. budget cap = realized median crew tokens / N.
    print("\n=== PHASE 3: single-agent baselines ===")
    budget = max(2000, median_crew_tokens(run_dir, task_ids) // 4)
    print(f"  budget cap for single-budget arm: {budget} tokens")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(run_single, tid, v, run_dir, budget)
            for tid in task_ids
            for v in ("budget", "naive")
        ]
        for f in as_completed(futures):
            f.result()

    # Phase 4: scoring all four arms
    print("\n=== PHASE 4: scoring ===")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(run_score, tid, a, run_dir, judge)
            for tid in task_ids
            for a in ("dissent", "consensus", "budget", "naive")
        ]
        for f in as_completed(futures):
            f.result()

    print(f"\nDone. Inspect runs/{('pilot' if pilot else 'full')}/")


if __name__ == "__main__":
    main()
