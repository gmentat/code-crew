"""Compare direct-named K+H+T (runs/framing/) vs archetype-inspired K+H+T (runs/personas/, triple-A)."""
from __future__ import annotations
import json
from statistics import mean, median

from lib import RUNS, iter_selected_prs


def load_a(task_ids):
    rows = []
    for tid in task_ids:
        p = RUNS / "personas" / tid / "scores" / "triple-A.json"
        if p.exists():
            rec = json.loads(p.read_text())
            rows.append({"task_id": tid, **rec["metrics"]})
    return rows


def load_b(task_ids):
    rows = []
    for tid in task_ids:
        p = RUNS / "framing" / tid / "scores" / "direct.json"
        if p.exists():
            rec = json.loads(p.read_text())
            rows.append({"task_id": tid, **rec["metrics"]})
    return rows


def summarize(rows):
    if not rows: return {"n": 0}
    return {
        "n": len(rows),
        "mean_recall":      mean(r["recall_raw"] for r in rows),
        "median_recall":    median(r["recall_raw"] for r in rows),
        "mean_precision":   mean(r["precision_raw"] for r in rows),
        "mean_fabrication": mean(r["fabrication_rate"] for r in rows),
        "mean_flagged":     mean(r["flagged_total"] for r in rows),
    }


def paired(rows_a, rows_b):
    by_a = {r["task_id"]: r for r in rows_a}
    by_b = {r["task_id"]: r for r in rows_b}
    common = sorted(set(by_a) & set(by_b))
    out = {}
    for metric in ("recall_raw", "precision_raw", "fabrication_rate"):
        deltas = [by_b[t][metric] - by_a[t][metric] for t in common]  # B - A
        wins_b = sum(1 for d in deltas if d > 0)
        wins_a = sum(1 for d in deltas if d < 0)
        ties   = sum(1 for d in deltas if d == 0)
        p_one_b = p_two = None
        if wins_a + wins_b > 0:
            try:
                from scipy.stats import binomtest
                p_one_b = binomtest(wins_b, wins_a + wins_b, p=0.5, alternative="greater").pvalue
                p_two = binomtest(wins_b, wins_a + wins_b, p=0.5, alternative="two-sided").pvalue
            except Exception:
                pass
        out[metric] = {
            "n_paired": len(common),
            "mean_delta_b_minus_a": mean(deltas) if deltas else 0.0,
            "median_delta_b_minus_a": median(deltas) if deltas else 0.0,
            "wins_b": wins_b, "wins_a": wins_a, "ties": ties,
            "p_one_sided_b_gt_a": p_one_b, "p_two_sided": p_two,
        }
    return out


def main():
    task_ids = [r["task_id"] for r in iter_selected_prs(run="main")]
    rows_a = load_a(task_ids)
    rows_b = load_b(task_ids)

    print(f"# Persona framing A/B — n_a={len(rows_a)} n_b={len(rows_b)}\n")
    print("## Style A (control, archetype-inspired): triple-A from runs/personas/")
    print(f"  {summarize(rows_a)}")
    print("\n## Style B (treatment, directly named): direct from runs/framing/")
    print(f"  {summarize(rows_b)}")

    print("\n## Paired sign tests (B − A per PR)\n")
    p = paired(rows_a, rows_b)
    for metric, d in p.items():
        p1 = f"{d['p_one_sided_b_gt_a']:.4f}" if d['p_one_sided_b_gt_a'] is not None else "n/a"
        p2 = f"{d['p_two_sided']:.4f}" if d['p_two_sided'] is not None else "n/a"
        print(f"  {metric:18s}  n={d['n_paired']:2d}  Δ(B−A)={d['mean_delta_b_minus_a']:+.4f}  "
              f"wins B={d['wins_b']:2d}  wins A={d['wins_a']:2d}  ties={d['ties']:2d}  "
              f"p1(B>A)={p1}  p2={p2}")

    out = {
        "n_a": len(rows_a), "n_b": len(rows_b),
        "style_a_summary": summarize(rows_a),
        "style_b_summary": summarize(rows_b),
        "paired": p,
    }
    out_path = RUNS / "framing" / "ANALYSIS.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
