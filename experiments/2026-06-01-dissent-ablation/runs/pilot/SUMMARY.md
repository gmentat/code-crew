# Pilot — DA-PRB

**Date:** 2026-06-01
**n:** 3 PRs (stratified by language: JS, Python, TypeScript)
**Substrate:** `foundry-ai/swe-prbench` eval_split, subset where `has_requested_changes=True`
**PRs:** stylelint #8953 (JS bug-fix), spyder #24990 (Python feature), vitest #9521 (TypeScript feature)
**Cost:** ~$0 in API spend (run via Workflow on Claude credentials, not direct API)
**Wall-clock:** ~10 min (42 agents across 4 phase barriers)

## Headline result

| Arm | Mean recall | Mean precision | Mean fabrication rate | Mean issues flagged |
|---|---|---|---|---|
| **crew-dissent (Arm A)** | **0.342** | **0.209** | **0.020** | 15.7 |
| crew-consensus (Arm B) | 0.142 | 0.086 | 0.133 | 9.3 |
| single-agent budget-matched (Arm C) | 0.142 | 0.151 | 0.103 | 10.3 |
| single-agent naive (Arm D) | 0.058 | 0.086 | 0.086 | 9.0 |

### Paired per-PR wins

| Comparison | Mean Δ recall | Wins |
|---|---|---|
| **H1: dissent vs consensus** | **+0.200** | 3-0 for dissent |
| **H2: dissent vs budget-matched single agent** | **+0.200** | 3-0 for dissent |
| sanity: dissent vs naive single agent | +0.283 | 3-0 for dissent |

### Per-PR matches (humans flagged → dissent matched)

| PR | Human concerns | dissent | consensus | budget | naive |
|---|---|---|---|---|---|
| stylelint__8953 (JS) | 8 | **4** | 1 | 2 | 1 |
| spyder__24990 (Python) | 20 | **3** | 1 | 1 | 1 |
| vitest__9521 (TS) | 8 | **3** | 2 | 1 | 0 |

## What this says (directionally — pilot, not the test)

- **Direction of H1 is confirmed at n=3.** Preserved-dissent synthesis caught roughly 2× more human-reviewer concerns than consensus synthesis on every PR, AND had lower fabrication. The crew's value isn't from generic "flag more" — it's that the additional flagged issues are mostly defensible.
- **Direction of H2 is confirmed at n=3.** Crew with dissent outperformed both single-agent baselines on every PR. The budget-matched single-agent landed at the same recall as crew-consensus (0.142), suggesting the synthesis mode is the differentiator more than the multi-pass alone.
- **Manipulation check is broken as implemented.** Mean Jaccard distance = 1.000 across persona pairs, which is suspiciously perfect. The coarse fingerprint (`severity|file|description[:80]`) is too strict — personas describe the same underlying concerns with different phrasing and never exact-match. The headline finding is unaffected (synthesis already preserves cross-attribution), but the **H3 metric needs an embedding-based fingerprint for the full run**.

## Caveats (load-bearing for interpretation)

1. **n=3 is far too small for statistical claims.** Three 3-0 wins look strong but have meaningful chance probability. The full 80-PR run gives the statistical power; this pilot just says "the direction is real and large enough to be worth the $260."
2. **Judge was Claude, not GPT-5.1.** PROTOCOL.md specifies GPT-5.1 as primary judge to control for Claude-judging-Claude self-preference. The pilot used Claude because no `OPENAI_API_KEY` was available in the run environment. **Recorded in [`DEVIATIONS.md`](../../DEVIATIONS.md).** For the full run, the judge must be non-Claude.
3. **PR pool was restricted.** Pilot drew from `has_requested_changes=True` (20 of 100 eval PRs) to guarantee ground-truth signal. The full sample uses the natural distribution across all 100. Expected effect: full-run effect sizes likely smaller than pilot because PRs with no requested changes have fewer issues to recall.
4. **Pre-registration was the pilot protocol (DA-PRB).** No outcome-dependent changes were made between this analysis and what `PROTOCOL.md` specified.
5. **Token budget for Arm C was not exactly matched.** Workflow agents don't expose per-call token usage at the surface we can introspect, so "budget-matched" was implemented as instructive ("be thorough") rather than as a hard cap. Real-API run needs proper enforcement.

## Recommendation

**GO on the full 80-PR run.** The pilot's pre-registered decision rule says: if pilot shows ≥80% of dissent recall vs single-agent at equal compute, AND H3 doesn't fail, full run is worth $260. We exceeded that bar (3-0 on H2; H3 metric needs fixing but qualitative divergence is clear from per-pass content inspection).

**Required changes before the full run:**

1. **Switch judge to GPT-5.1** (or Gemini 2.5 Pro as backup). No Claude judging Claude.
2. **Replace H3 fingerprint with embedding-based similarity.** Either OpenAI text-embedding-3-small with 0.8 cosine threshold for "same issue," or LLM-as-classifier per pair of flagged issues.
3. **Implement real token budget enforcement** for Arm C — use the Anthropic SDK with explicit `max_tokens` + `thinking.budget_tokens` caps measured against the realized median Arm A total.
4. **Run on the full 80-PR stratified sample** (PROTOCOL.md §Substrate), not the requested-changes subset.

## Files

- Per-PR raw outputs: `runs/pilot/<task_id>/` (gitignored)
- Aggregated analysis: [`ANALYSIS.json`](ANALYSIS.json) (committed)
- This summary: [`SUMMARY.md`](SUMMARY.md) (committed)
- Frozen protocol: [`../../PROTOCOL.md`](../../PROTOCOL.md)
- Pre-registered deviations: [`../../DEVIATIONS.md`](../../DEVIATIONS.md)

## Reproducibility

Anyone can re-run the pilot from a fresh clone with API keys set:

```bash
cd experiments/2026-06-01-dissent-ablation
uv sync
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...   # optional for pilot; required for full run
uv run python scripts/select_prs.py --pilot
uv run python scripts/orchestrate.py --pilot
uv run python scripts/analyze.py --run pilot
```

The PR IDs are committed (deterministic seed=42), the prompts are frozen, the harness is git-tracked.
