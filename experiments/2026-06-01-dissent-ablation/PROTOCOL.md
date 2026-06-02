# DA-PRB — Dissent Ablation on SWE-PRBench

**Pre-registered experimental protocol.** Frozen 2026-06-01. Any deviation from this document during execution must be recorded in `DEVIATIONS.md` and dated.

## Hypotheses

We test three pre-registered hypotheses about the code_crew pattern as applied to code review.

### H1 (headline) — Preserved dissent in synthesis improves recall

Arm A (crew with preserved-dissent synthesis) achieves recall-at-precision-0.70 of human-flagged P0+P1 issues that exceeds Arm B (same crew, same blind passes, identical synthesis prompt with dissent-preservation clause replaced by consensus-collapse clause) by ≥5 percentage points.

- Statistical test: paired McNemar on per-PR recall outcomes
- Significance threshold: p < 0.05
- Minimum detectable effect at n=80: ~5pp
- **Falsifying observation:** delta < 3pp, or p > 0.10

### H2 — Multi-pass crew beats single-agent at equal token budget

Arm A recall exceeds Arm C (single Claude agent with extended thinking, hard-capped at the realized median token count of Arm A) by ≥7pp at equal realized tokens (within 15%).

- **Falsifying:** delta < 3pp, OR token gap > 15% (comparison invalid)
- MDE: ~7pp

### H3 — Manipulation check (gating)

Inter-pass disagreement rate in Arm A exceeds 0.3 (mean Jaccard distance on flagged-issue sets between persona pairs). If < 0.3, personas have collapsed into one voice and the crew pattern is not actually being tested.

- **If H3 fails:** abort H1/H2 conclusions; publish methodology note only.

## Substrate

[`foundry-ai/swe-prbench`](https://huggingface.co/datasets/foundry-ai/swe-prbench) on HuggingFace.

- 350 PRs annotated; 100-PR canonical eval split (`eval_100.json`)
- Each PR has: diff, human reviewer comments (ground truth), severity labels, repo metadata
- License: CC BY 4.0

**Sample:** 80 PRs stratified by language to match the dataset's natural distribution:

| Language | Target | Source share |
|---|---|---|
| Python | 55 | 69% |
| JavaScript | 9 | 11% |
| Go | 8 | 10% |
| TypeScript | 5 | 6% |
| Java | 3 | 4% |

**Seed:** 42 (frozen).
**PR IDs:** committed to `data/prs.json` before any model is run on data outside the pilot 3.

## Conditions / modes

Four arms, every PR run through each one. Paired analysis.

### Arm A — crew-dissent
- 6 personas: Knuth, Hickey, Torvalds, Liskov, Pike, Dijkstra (frozen persona files in `prompts/`)
- Each persona runs as an **independent blind pass** — no persona sees another's draft
- Synthesis step uses `prompts/synthesis_dissent.md` (explicitly preserves dissent, cross-persona citations, no consensus-collapse)
- Output: structured list of flagged issues with cross-persona attribution

### Arm B — crew-consensus
- Identical to Arm A in personas and blind passes
- Synthesis step uses `prompts/synthesis_consensus.md` (identical prompt to Arm A's synthesis except the dissent-preservation clause is replaced with a consensus-collapse clause)
- **Diff between synthesis_dissent.md and synthesis_consensus.md must be ≤ 10 lines.** This is the synthesis-only control that isolates the dissent variable.

### Arm C — single-agent budget-matched
- Claude Sonnet 4.5 + extended thinking
- Hard cap on `max_tokens` and thinking budget set to the **realized median total token count of Arm A**, measured on a 10-PR pilot
- Prompt: `prompts/single_agent.md` — "Senior engineer review, enumerate dissenting views before concluding"

### Arm D — single-agent naive
- Same model, no extended thinking, naked prompt
- Floor sanity check; not the primary comparator

## Primary metric: recall-at-fixed-precision-0.70

The verbosity confound (longer outputs flag more issues and look better) is neutralized by fixing precision before measuring recall.

Procedure per PR:
1. Each arm produces a list of flagged issues
2. A judge classifies each flagged issue as CONFIRMED / PLAUSIBLE / FABRICATED against the PR's human review ground truth, using SWE-PRBench's published rubric
3. Compute per-PR precision = CONFIRMED / (CONFIRMED + PLAUSIBLE + FABRICATED)
4. If precision < 0.70 → drop the lowest-confidence flagged issues iteratively until precision ≥ 0.70
5. Compute per-PR recall = CONFIRMED / (P0+P1 ground-truth issues)

Aggregate: paired McNemar on per-PR recall comparison; bootstrap 95% CIs.

## Secondary metrics

- Raw recall@all (no precision filter) — comparability with prior work
- Fabrication rate (FABRICATED / total flagged)
- Length-controlled pairwise win rate (3-judge ensemble: GPT-5.1, Gemini 2.5 Pro, Llama-4; no Claude judge since the crew uses Claude) — controls for self-preference bias
- Realized token usage per arm (mean + median); if Arm C underspends Arm A by > 15%, comparison is invalid and we say so
- Inter-pass Jaccard distance distribution (manipulation check input)

## Judging

- Primary scoring judge: GPT-5.1 (separate from any model the crew uses)
- Validation: judge is run on 5 PRs against SWE-PRBench's published baseline scores. If our judge mismatches by > 10pp on those 5, we fix the judge prompt before any full run.
- Pairwise judge ensemble (secondary metric): GPT-5.1 + Gemini 2.5 Pro + Llama-4, both presentation orderings per PR pair, length-controlled instruction.

## Decision rules

| Outcome | Action |
|---|---|
| H1 confirmed + H3 passes | Publish: *"Preserved dissent improves PR review recall by Xpp over consensus synthesis at equal compute."* This is the OSS package's empirical backbone. |
| H1 null + H2 confirmed | Publish: *"Multi-pass review beats single-pass at equal compute, but dissent preservation is not the active ingredient."* Revise crew docs to drop preserved-dissent centrality; keep multi-pass. |
| H1 + H2 both null | Publish: *"At equal token budget, multi-persona review does not outperform single-agent extended-thinking on PR recall."* OSS framing shifts from "better outputs" to "auditable process / interpretable disagreement." **Pre-committing to this framing now so it isn't sour-grapes post-hoc.** |
| H3 fails (persona collapse) | Methodology note only: *"Personas collapsed under generation; crew pattern requires stronger persona enforcement to be testable."* Ship v2 with stronger enforcement and retest. |
| Token gap > 15% in C | Comparison invalid; rerun C with adjusted cap, or report H1 only. |

## What this protocol cannot test

- Named archetypes vs role-labels (Tangent 3) — substrate-contaminated at this budget
- Execute tasks (write the patch) — not what the crew is for
- Production-bug prediction (training contamination risk)
- Generalization beyond code review (acknowledged caveat in writeup)

## Pre-registration record

- Frozen date: 2026-06-01
- Protocol git SHA: *(committed at first commit of this directory)*
- Prompts directory git SHA: *(committed at first commit of this directory)*
- PR IDs file (`data/prs.json`): generated by `scripts/select_prs.py` with seed=42; committed before any full-run model invocation

Any deviation from this protocol made during execution is recorded in `DEVIATIONS.md` with date, change, rationale.
