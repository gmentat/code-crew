# Main run — DA-PRB n=50

**Date:** 2026-06-01
**n:** 50 PRs, stratified by language (Python 34 / Go 7 / JS 5 / TS 3 / Java 1)
**Substrate:** `foundry-ai/swe-prbench` eval_split, natural language distribution (no `has_requested_changes` filter)
**Cost:** ~24M subagent tokens across two sharded Workflow runs (~$0 against subscription)
**Wall-clock:** 2 × ~40 min in parallel
**Judge:** Claude (anonymized prompt, skeptic-framed) — see deviations
**Headline finding:** **The pilot did not replicate. Preserved-dissent synthesis is NOT the active ingredient.**

## Per-arm summary (n=50)

| Arm | Recall (raw) | Precision (raw) | Fabrication rate | Issues flagged (mean) |
|---|---|---|---|---|
| crew-dissent (A) | 0.270 | 0.044 | 0.738 | 17.1 |
| crew-consensus (B) | 0.259 | 0.067 | 0.631 | 10.0 |
| single-agent budget-matched (C) | 0.245 | 0.057 | 0.701 | 11.0 |
| single-agent naive (D) | 0.196 | 0.068 | 0.706 | 9.6 |

## Paired tests (paired sign / exact binomial)

| Comparison | Mean Δ recall | Wins | Ties | p (one-sided) | Verdict |
|---|---|---|---|---|---|
| **H1: dissent vs consensus** | **+0.012** | 10–8 | 32 | **0.407** | **NULL** |
| **H2: dissent vs budget single-agent** | **+0.025** | 20–13 | 17 | **0.148** | **NULL** |
| sanity: dissent vs naive single-agent | **+0.074** | 24–8 | 18 | **0.0035** | **CONFIRMED** |

## H3 — manipulation check

Mean Jaccard distance between persona issue-sets: **0.565** (LLM-classified, 50/50 PRs).
Pre-registered threshold ≥ 0.30 → **H3 PASSES**.

Personas *are* diverging semantically; the crew pattern is mechanically working as designed. Preserved dissent simply doesn't translate into better recall.

## What this means

Per the pre-registered decision rules in `PROTOCOL.md`:

> **H1 null + H2 null** → "At equal token budget, multi-persona review does not outperform single-agent extended-thinking on PR recall."

The honest reading is slightly more nuanced:

1. **Multi-pass crew beats naive single-agent** (+7.4pp recall, p=0.0035). Multi-perspective review *does* surface more concerns than asking one Claude instance once.

2. **Preserved-dissent synthesis does NOT beat consensus synthesis.** The +1.2pp delta is well within noise (32 of 50 PRs tied). Whatever value the crew has is captured by *running multiple passes*, not by *preserving dissent in synthesis*. The dissent-preservation clause in the synthesis prompt doesn't produce measurably different outputs from consensus collapse on this task.

3. **The pilot's +20pp dominance was largely an artifact** — Claude judging Claude without anonymization, no skeptic framing, and n=3 noise inflated the effect. Once those are controlled for, the headline collapses.

4. **Dissent flags more issues but mostly fabrications.** 17.1 flagged vs 10.0 for consensus, but precision is *lower* (0.044 vs 0.067) and fabrication rate is *higher* (0.74 vs 0.63). The extra issues the dissent synthesis preserves are concerns the consensus path correctly dropped.

5. **All fabrication rates are high** (60-74%). The skeptic-anonymized judge is much stricter than the pilot's judge. This affects absolute numbers but applies symmetrically across arms, so the *comparison* is still valid.

## Implications for the OSS pitch

This rules out the strongest empirical claim we had drafted.

- ✗ **Cannot claim:** "Preserved dissent improves PR review recall by Xpp over consensus synthesis at equal compute."
- ✓ **Can claim:** "Multi-perspective review with N specialist personas surfaces +7pp more reviewer concerns than a single naked Claude call on PR review, paired n=50 (p=0.004)."
- ◐ **Cannot yet decide:** Whether the value of the crew is in *outputs* (better issue lists) or in *process* (auditable disagreement, traceable provenance, dissent visible to a human reviewer). The latter is not captured by recall-against-human-comments and would need a different study (e.g. survey, blind A/B with engineers).

Per `PROTOCOL.md`'s decision rule: "OSS framing shifts from 'better outputs' to 'auditable process / interpretable disagreement.' Pre-committing to this framing now so it isn't sour-grapes post-hoc." That framing is now active.

## Caveats (load-bearing for interpretation)

1. **Judge is still Claude.** Anonymized + skeptic-framed mitigates the most obvious bias vectors but does not eliminate Claude-judging-Claude effects. A non-Claude judge could shift absolute numbers in either direction; relative comparisons between arms are more robust because both arms are produced by Claude crews.

2. **Precision-at-0.70 metric not computable.** All arms run at precision 0.04-0.07 under this judge; the protocol's primary precision-controlled recall would require dropping nearly every flagged issue. Raw recall is the only usable metric at these precision levels. Future work: re-tune the judge OR change the metric.

3. **`PROTOCOL.md` specified n=80; we ran n=50.** Workflow agent cap limited shard size; recorded in `DEVIATIONS.md`. Additional power would tighten CIs but is unlikely to flip an H1 verdict where the point estimate is +0.012 with 32 ties out of 50.

4. **The synthesis prompts may be the active variable, not the dissent mechanism.** A different operationalization of "preserved dissent" (e.g. structured dissent-with-evidence section that the consumer must address) could produce different results. We tested *one* operationalization of dissent preservation; it didn't separate.

5. **Naive baseline is genuinely naive.** It's a single Claude call with no thinking budget and a short prompt. The +0.074 delta against it is the easiest comparison to win; the meaningful comparison is H2 (budget-matched single-agent with extended thinking), which is null.

## What changed vs the pilot

| | Pilot (n=3) | Main (n=50) |
|---|---|---|
| Judge | Claude, no anonymization, no skeptic frame | Claude, anonymized, skeptic-framed |
| PR pool | `has_requested_changes=True` only | Natural distribution |
| H3 metric | Exact-string fingerprint (broken; 1.0 always) | LLM-classified pairwise similarity |
| H1 result | +0.200 (3-0 wins) | +0.012 (10-8, p=0.41) |
| H2 result | +0.200 (3-0 wins) | +0.025 (20-13, p=0.15) |

The pilot's effect attenuated by ~95% after these three changes. Of those: judge anonymization + skeptic framing probably accounts for most of the gap (Claude-on-Claude with arm labels visible is a known bias path); PR pool change shifted absolute recall down by ~30% across all arms; n=50 made the noise visible.

## Files

- Per-PR raw outputs: `runs/main/<task_id>/` (committed)
- Aggregated analysis: [`ANALYSIS.json`](ANALYSIS.json)
- This summary: [`SUMMARY.md`](SUMMARY.md)
- Frozen protocol: [`../../PROTOCOL.md`](../../PROTOCOL.md)
- Deviations from protocol: [`../../DEVIATIONS.md`](../../DEVIATIONS.md)
- Pilot comparison: [`../pilot/SUMMARY.md`](../pilot/SUMMARY.md)

## Recommendation

1. **Drop the "preserved dissent improves recall" claim from the OSS README.** It does not survive at n=50 with bias-mitigated judging.
2. **Keep the "multi-perspective review > naive single agent" claim** — n=50, paired p=0.0035 is solid.
3. **Reframe the crew's value as *process*, not *outputs*.** Auditable disagreement, persona-attributed dissent, and traceable synthesis are the actual product. The recall delta doesn't load-bear.
4. **If the dissent mechanism is worth defending empirically**, design a stronger operationalization (e.g. dissent-with-evidence that the synthesizer cannot collapse without justification) and run a new pre-registered test. The current synthesis_dissent.md vs synthesis_consensus.md ablation was too subtle to separate.
