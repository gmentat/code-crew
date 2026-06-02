"""Compare all 10 triples (8 new + K+H+T + D+L+P from persona run) head-to-head.

Reports per-triple recall, precision, fabrication.
Paired sign tests vs K+H+T (the current best) and vs the worst triple.
Identifies the optimal composition.
"""

from __future__ import annotations
import json
from statistics import mean

from lib import RUNS, iter_selected_prs


# All triples being compared. Keys for the new ones match the workflow's tripleKey() output.
NEW_TRIPLES = [
    ("knuth+liskov+torvalds", ["knuth", "liskov", "torvalds"]),
    ("knuth+pike+torvalds", ["knuth", "pike", "torvalds"]),
    ("dijkstra+hickey+torvalds", ["dijkstra", "hickey", "torvalds"]),
    ("dijkstra+liskov+torvalds", ["dijkstra", "liskov", "torvalds"]),
    ("dijkstra+pike+torvalds", ["dijkstra", "pike", "torvalds"]),
    ("knuth+hickey+dijkstra", ["knuth", "hickey", "dijkstra"]),
    ("hickey+liskov+pike", ["hickey", "liskov", "pike"]),
    ("liskov+pike+torvalds", ["liskov", "pike", "torvalds"]),
]
# Existing baselines from persona run (scored under same judge + same input passes)
EXISTING = [
    ("triple-A (knuth+hickey+torvalds)", "triple-A"),
    ("triple-B (dijkstra+liskov+pike)", "triple-B"),
]


def load_existing(arm_label, task_ids):
    rows = []
    for tid in task_ids:
        p = RUNS / "personas" / tid / "scores" / f"{arm_label}.json"
        if p.exists():
            rec = json.loads(p.read_text())
            rows.append({"task_id": tid, **rec["metrics"]})
    return rows


def load_new(triple_key, task_ids):
    rows = []
    for tid in task_ids:
        p = RUNS / "triples" / tid / "scores" / f"{triple_key}.json"
        if p.exists():
            rec = json.loads(p.read_text())
            rows.append({"task_id": tid, **rec["metrics"]})
    return rows


def summarize(rows):
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        "mean_recall": mean(r["recall_raw"] for r in rows),
        "mean_precision": mean(r["precision_raw"] for r in rows),
        "mean_fabrication": mean(r["fabrication_rate"] for r in rows),
        "mean_flagged": mean(r["flagged_total"] for r in rows),
    }


def paired(rows_a, rows_b, name_a, name_b):
    by_a = {r["task_id"]: r for r in rows_a}
    by_b = {r["task_id"]: r for r in rows_b}
    common = sorted(set(by_a) & set(by_b))
    deltas = [by_a[t]["recall_raw"] - by_b[t]["recall_raw"] for t in common]
    wins = sum(1 for d in deltas if d > 0)
    losses = sum(1 for d in deltas if d < 0)
    ties = sum(1 for d in deltas if d == 0)
    p_one = p_two = None
    if wins + losses > 0:
        try:
            from scipy.stats import binomtest

            p_one = binomtest(wins, wins + losses, p=0.5, alternative="greater").pvalue
            p_two = binomtest(
                wins, wins + losses, p=0.5, alternative="two-sided"
            ).pvalue
        except Exception:
            pass
    return {
        "a": name_a,
        "b": name_b,
        "n": len(common),
        "mean_delta": mean(deltas) if deltas else 0.0,
        "wins_a": wins,
        "wins_b": losses,
        "ties": ties,
        "p_one_sided_a_gt_b": p_one,
        "p_two_sided": p_two,
    }


def main():
    task_ids = [r["task_id"] for r in iter_selected_prs(run="main")]

    # Collect all arms' per-PR rows
    arms = {}
    for label, arm in EXISTING:
        arms[label] = load_existing(arm, task_ids)
    for label, _ in NEW_TRIPLES:
        arms[label] = load_new(label, task_ids)

    print(f"# Triple composition search — n={len(task_ids)} PRs (target)\n")
    print("## Per-triple summary\n")
    print(
        f"{'triple':45s} {'n':>3s} {'recall':>8s} {'prec':>6s} {'fab':>6s} {'flagged':>8s}"
    )
    rows_for_sort = []
    label_order = [label for label, _ in EXISTING] + [label for label, _ in NEW_TRIPLES]
    for label in label_order:
        s = summarize(arms[label])
        n = s.get("n", 0)
        if n == 0:
            print(f"{label:45s}  --- no data ---")
            continue
        print(
            f"{label:45s} {n:>3d} {s['mean_recall']:>8.3f} {s['mean_precision']:>6.3f} "
            f"{s['mean_fabrication']:>6.3f} {s['mean_flagged']:>8.1f}"
        )
        rows_for_sort.append((label, s["mean_recall"], n))

    rows_for_sort.sort(key=lambda x: -x[1])
    if rows_for_sort:
        print(
            f"\nBest triple by mean recall: {rows_for_sort[0][0]} ({rows_for_sort[0][1]:.3f})"
        )

    # Paired tests vs K+H+T baseline
    baseline_label = EXISTING[0][0]
    print(f"\n## Paired sign tests vs baseline ({baseline_label})\n")
    print(
        f"{'comparison':50s} {'n':>3s} {'Δrecall':>8s} {'wins-losses':>15s} {'p1':>8s}"
    )
    paired_summaries = {}
    for label in label_order:
        if label == baseline_label:
            continue
        d = paired(arms[label], arms[baseline_label], label, baseline_label)
        p1 = (
            f"{d['p_one_sided_a_gt_b']:.4f}"
            if d["p_one_sided_a_gt_b"] is not None
            else "n/a"
        )
        print(
            f"{label:50s} {d['n']:>3d} {d['mean_delta']:>+8.3f} "
            f"{d['wins_a']:>4d}-{d['wins_b']:<4d} ties={d['ties']:<3d} p1={p1}"
        )
        paired_summaries[label] = d

    # Write JSON
    out = {
        "n_target": len(task_ids),
        "per_triple": {label: summarize(arms[label]) for label in label_order},
        "paired_vs_baseline": paired_summaries,
        "best_triple": rows_for_sort[0][0] if rows_for_sort else None,
        "best_recall": rows_for_sort[0][1] if rows_for_sort else None,
    }
    out_path = RUNS / "triples" / "ANALYSIS.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
