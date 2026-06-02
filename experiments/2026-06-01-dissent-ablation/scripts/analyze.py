"""Aggregate run results: H1, H2, H3 tests + per-PR summary."""

from __future__ import annotations

import json
from statistics import mean, median

import click

from lib import PERSONAS, RUNS, iter_selected_prs, read_json


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    u = len(a | b)
    return 1 - (len(a & b) / u) if u else 0.0


def issue_key(iss: dict) -> str:
    # Coarse fingerprint: severity + first 80 chars of description + file (if any)
    desc = (iss.get("description") or "")[:80].strip().lower()
    f = (iss.get("file") or "").strip().lower()
    sev = (iss.get("severity") or "").upper()
    return f"{sev}|{f}|{desc}"


def manipulation_check(run_dir: str, task_ids: list[str]) -> dict:
    """H3: mean Jaccard distance on flagged-issue sets between persona pairs.

    If a per-PR `h3_similarity.json` LLM-classified matrix exists (main run),
    use that. Otherwise fall back to the coarse exact-string fingerprint
    (pilot mode; known too strict and recorded as a deviation).
    """
    per_pr = []
    used_llm = 0
    used_fingerprint = 0
    for tid in task_ids:
        base = RUNS / run_dir.split("runs/")[-1] / tid
        h3_path = base / "h3_similarity.json"
        if h3_path.exists():
            mat_obj = read_json(h3_path)
            matrix = mat_obj.get("matrix") or []
            distances = []
            n = len(matrix)
            for i in range(n):
                for j in range(i + 1, n):
                    sim = float(matrix[i][j])
                    distances.append(1.0 - max(0.0, min(1.0, sim)))
            per_pr.append(
                {
                    "task_id": tid,
                    "mean_jaccard_distance": mean(distances) if distances else 0.0,
                    "source": "llm_matrix",
                }
            )
            used_llm += 1
        else:
            sets = {}
            for p in PERSONAS:
                rec = read_json(base / "passes" / f"{p}.json")
                sets[p] = {issue_key(i) for i in rec["review"].get("issues", [])}
            ds = []
            keys = list(sets.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    ds.append(jaccard(sets[keys[i]], sets[keys[j]]))
            per_pr.append(
                {
                    "task_id": tid,
                    "mean_jaccard_distance": mean(ds) if ds else 0.0,
                    "source": "exact_fingerprint",
                }
            )
            used_fingerprint += 1
    overall = mean(p["mean_jaccard_distance"] for p in per_pr) if per_pr else 0.0
    return {
        "overall_mean": overall,
        "per_pr": per_pr,
        "h3_pass": overall >= 0.3,
        "source_breakdown": {
            "llm_matrix": used_llm,
            "exact_fingerprint": used_fingerprint,
        },
    }


def collect_metrics(run_dir: str, task_ids: list[str]) -> dict:
    arms = ["dissent", "consensus", "budget", "naive"]
    per_arm: dict[str, list[dict]] = {a: [] for a in arms}
    for tid in task_ids:
        base = RUNS / run_dir.split("runs/")[-1] / tid
        for a in arms:
            score_path = base / "scores" / f"{a}.json"
            if not score_path.exists():
                continue
            rec = read_json(score_path)
            per_arm[a].append({"task_id": tid, **rec["metrics"]})
    return per_arm


def summarize_arm(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}

    def m(k: str) -> float:
        return mean(r[k] for r in rows)

    return {
        "n": len(rows),
        "mean_precision_raw": m("precision_raw"),
        "mean_recall_raw": m("recall_raw"),
        "mean_fabrication_rate": m("fabrication_rate"),
        "mean_flagged_total": m("flagged_total"),
    }


def paired_recall_delta(per_arm: dict, a: str, b: str) -> dict:
    """Per-PR paired recall delta a - b + paired sign test (exact binomial)."""
    by_pr_a = {r["task_id"]: r for r in per_arm.get(a, [])}
    by_pr_b = {r["task_id"]: r for r in per_arm.get(b, [])}
    common = sorted(set(by_pr_a) & set(by_pr_b))
    deltas = [by_pr_a[t]["recall_raw"] - by_pr_b[t]["recall_raw"] for t in common]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)
    # Paired sign test on discordant pairs (one-sided: a > b).
    p_one_sided = None
    p_two_sided = None
    if wins + losses > 0:
        try:
            from scipy.stats import binomtest

            res_g = binomtest(wins, wins + losses, p=0.5, alternative="greater")
            res_t = binomtest(wins, wins + losses, p=0.5, alternative="two-sided")
            p_one_sided = res_g.pvalue
            p_two_sided = res_t.pvalue
        except Exception:
            pass
    return {
        "a": a,
        "b": b,
        "n": len(common),
        "mean_delta": mean(deltas) if deltas else 0.0,
        "median_delta": median(deltas) if deltas else 0.0,
        "wins_a": wins,
        "wins_b": losses,
        "ties": ties,
        "p_one_sided_a_gt_b": p_one_sided,
        "p_two_sided": p_two_sided,
    }


@click.command()
@click.option(
    "--run", default="pilot", help="Subdirectory under runs/ (pilot or full)."
)
def main(run: str) -> None:
    prs = list(iter_selected_prs(run=run))
    task_ids = [r["task_id"] for r in prs]
    run_dir = f"runs/{run}"

    print(f"# Analysis — {run_dir} (n={len(task_ids)})\n")

    h3 = manipulation_check(run_dir, task_ids)
    print("## H3 — manipulation check (persona divergence)")
    print(
        f"Overall mean Jaccard distance between persona pairs: {h3['overall_mean']:.3f}"
    )
    print(f"H3 threshold (≥ 0.30): {'PASS' if h3['h3_pass'] else 'FAIL'}\n")
    for r in h3["per_pr"]:
        print(
            f"  {r['task_id']:30s}  mean_jaccard_dist={r['mean_jaccard_distance']:.3f}"
        )

    per_arm = collect_metrics(run_dir, task_ids)
    print("\n## Per-arm summary")
    for a in ("dissent", "consensus", "budget", "naive"):
        s = summarize_arm(per_arm.get(a, []))
        print(f"  {a:9s}  {s}")

    print("\n## Paired recall deltas")
    for a, b, name in [
        ("dissent", "consensus", "H1: dissent vs consensus"),
        ("dissent", "budget", "H2: crew vs budget-matched single agent"),
        ("dissent", "naive", "sanity: crew vs naive single agent"),
    ]:
        d = paired_recall_delta(per_arm, a, b)
        p_str = (
            f"p1={d['p_one_sided_a_gt_b']:.4f}"
            if d.get("p_one_sided_a_gt_b") is not None
            else "p=n/a"
        )
        print(
            f"  {name:48s}  n={d['n']:2d}  mean_delta={d['mean_delta']:+.3f}  "
            f"wins({a})={d['wins_a']}  wins({b})={d['wins_b']}  ties={d['ties']}  {p_str}"
        )

    out = {
        "run": run,
        "n": len(task_ids),
        "h3": h3,
        "per_arm_summary": {a: summarize_arm(per_arm.get(a, [])) for a in per_arm},
        "paired_deltas": {
            "dissent_vs_consensus": paired_recall_delta(
                per_arm, "dissent", "consensus"
            ),
            "dissent_vs_budget": paired_recall_delta(per_arm, "dissent", "budget"),
            "dissent_vs_naive": paired_recall_delta(per_arm, "dissent", "naive"),
        },
    }
    summary_path = RUNS / run / "ANALYSIS.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {summary_path}")


if __name__ == "__main__":
    main()
