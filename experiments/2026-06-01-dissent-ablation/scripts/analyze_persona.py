"""Analyze the persona-ablation run: per-arm summary, paired tests, write ANALYSIS_PERSONA.json.

Includes a comparison to the main run's naive single-agent baseline (read from runs/main/).
"""

from __future__ import annotations

import json
from statistics import mean, median

import click

from lib import PERSONAS, RUNS, iter_selected_prs, read_json

ARMS = [
    *(f"solo-{p}" for p in PERSONAS),
    "named-6",
    "generic-6",
    "triple-A",
    "triple-B",
    "pair-TL",
]


def collect_metrics(task_ids: list[str]) -> dict:
    per_arm: dict[str, list[dict]] = {a: [] for a in ARMS}
    for tid in task_ids:
        base = RUNS / "personas" / tid
        for a in ARMS:
            p = base / "scores" / f"{a}.json"
            if not p.exists():
                continue
            rec = read_json(p)
            per_arm[a].append({"task_id": tid, **rec["metrics"]})
    return per_arm


def collect_main_naive(task_ids: list[str]) -> list[dict]:
    rows = []
    for tid in task_ids:
        p = RUNS / "main" / tid / "scores" / "naive.json"
        if p.exists():
            rec = read_json(p)
            rows.append({"task_id": tid, **rec["metrics"]})
    return rows


def summarize_arm(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "mean_recall_raw": mean(r["recall_raw"] for r in rows),
        "median_recall_raw": median(r["recall_raw"] for r in rows),
        "mean_precision_raw": mean(r["precision_raw"] for r in rows),
        "mean_fabrication_rate": mean(r["fabrication_rate"] for r in rows),
        "mean_flagged_total": mean(r["flagged_total"] for r in rows),
    }


def paired(rows_a: list[dict], rows_b: list[dict], a: str, b: str) -> dict:
    by_a = {r["task_id"]: r for r in rows_a}
    by_b = {r["task_id"]: r for r in rows_b}
    common = sorted(set(by_a) & set(by_b))
    deltas = [by_a[t]["recall_raw"] - by_b[t]["recall_raw"] for t in common]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)
    p_one_sided = p_two_sided = None
    if wins + losses > 0:
        try:
            from scipy.stats import binomtest

            p_one_sided = binomtest(
                wins, wins + losses, p=0.5, alternative="greater"
            ).pvalue
            p_two_sided = binomtest(
                wins, wins + losses, p=0.5, alternative="two-sided"
            ).pvalue
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


def h3_summary(task_ids: list[str]) -> dict:
    """Read both H3 matrices: named-6 (from main run) and generic-6 (this run)."""

    def matrix_distance(mat_obj):
        m = mat_obj.get("matrix") or []
        ds = []
        for i in range(len(m)):
            for j in range(i + 1, len(m)):
                ds.append(1.0 - max(0.0, min(1.0, float(m[i][j]))))
        return mean(ds) if ds else 0.0

    named_dists, generic_dists = [], []
    for tid in task_ids:
        nh = RUNS / "main" / tid / "h3_similarity.json"
        gh = RUNS / "personas" / tid / "h3_generic.json"
        if nh.exists():
            named_dists.append(matrix_distance(read_json(nh)))
        if gh.exists():
            generic_dists.append(matrix_distance(read_json(gh)))
    return {
        "named_6_mean": mean(named_dists) if named_dists else None,
        "named_6_n": len(named_dists),
        "generic_6_mean": mean(generic_dists) if generic_dists else None,
        "generic_6_n": len(generic_dists),
    }


@click.command()
def main() -> None:
    prs = list(iter_selected_prs(run="main"))
    task_ids = [r["task_id"] for r in prs]
    per_arm = collect_metrics(task_ids)
    main_naive = collect_main_naive(task_ids)

    print(f"# Persona ablation — n={len(task_ids)} PRs (matches main run)\n")
    print("## Per-arm summary\n")
    for a in ARMS:
        s = summarize_arm(per_arm.get(a, []))
        print(
            f"  {a:15s}  n={s.get('n', 0):2d}  "
            f"recall={s.get('mean_recall_raw', 0):.3f}  "
            f"precision={s.get('mean_precision_raw', 0):.3f}  "
            f"fabrication={s.get('mean_fabrication_rate', 0):.3f}  "
            f"flagged={s.get('mean_flagged_total', 0):.1f}"
        )

    print("\n## Hypothesis tests (paired sign / binomial)\n")
    paired_tests = {}
    # HP1: named-6 vs generic-6
    paired_tests["HP1_named6_vs_generic6"] = paired(
        per_arm["named-6"], per_arm["generic-6"], "named-6", "generic-6"
    )
    # HP2: each solo vs named-6
    for p in PERSONAS:
        paired_tests[f"HP2_solo-{p}_vs_named6"] = paired(
            per_arm[f"solo-{p}"], per_arm["named-6"], f"solo-{p}", "named-6"
        )
    # HP3: triple-A vs named-6, triple-B vs named-6, pair-TL vs named-6
    paired_tests["HP3_tripleA_vs_named6"] = paired(
        per_arm["triple-A"], per_arm["named-6"], "triple-A", "named-6"
    )
    paired_tests["HP3_tripleB_vs_named6"] = paired(
        per_arm["triple-B"], per_arm["named-6"], "triple-B", "named-6"
    )
    paired_tests["HP3_pairTL_vs_named6"] = paired(
        per_arm["pair-TL"], per_arm["named-6"], "pair-TL", "named-6"
    )
    # HP4: triple-A vs triple-B
    paired_tests["HP4_tripleA_vs_tripleB"] = paired(
        per_arm["triple-A"], per_arm["triple-B"], "triple-A", "triple-B"
    )
    # Sanity vs main-run naive
    for arm in ["named-6", "generic-6", "triple-A", "triple-B", "pair-TL"]:
        paired_tests[f"sanity_{arm}_vs_naive"] = paired(
            per_arm[arm], main_naive, arm, "naive(main)"
        )
    # Best single-persona check
    solos = [
        (p, summarize_arm(per_arm[f"solo-{p}"])["mean_recall_raw"]) for p in PERSONAS
    ]
    solos.sort(key=lambda x: -x[1])
    best_persona, best_recall = solos[0]
    paired_tests["HP2_best_persona_vs_named6"] = paired(
        per_arm[f"solo-{best_persona}"],
        per_arm["named-6"],
        f"solo-{best_persona}",
        "named-6",
    )
    print(f"Strongest single persona: {best_persona} (mean recall {best_recall:.3f})\n")

    for k, t in paired_tests.items():
        p1 = (
            f"{t['p_one_sided_a_gt_b']:.4f}"
            if t["p_one_sided_a_gt_b"] is not None
            else "n/a"
        )
        print(
            f"  {k:42s} n={t['n']:2d}  Δ={t['mean_delta']:+.3f}  "
            f"wins {t['wins_a']}-{t['wins_b']}  ties={t['ties']}  p1={p1}"
        )

    h3 = h3_summary(task_ids)
    print("\n## H3 manipulation check")

    def fmt(x):
        return f"{x:.3f}" if x is not None else "n/a"

    print(
        f"  named-6   mean Jaccard distance: "
        f"{fmt(h3['named_6_mean'])} (n={h3['named_6_n']})"
    )
    print(
        f"  generic-6 mean Jaccard distance: "
        f"{fmt(h3['generic_6_mean'])} (n={h3['generic_6_n']})"
    )

    out = {
        "n": len(task_ids),
        "per_arm_summary": {a: summarize_arm(per_arm.get(a, [])) for a in ARMS},
        "main_naive_summary": summarize_arm(main_naive),
        "best_persona": {"name": best_persona, "mean_recall": best_recall},
        "paired_tests": paired_tests,
        "h3": h3,
    }
    out_path = RUNS / "personas" / "ANALYSIS.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
