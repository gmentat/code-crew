# Code Crew — Empirical Findings

This is the review-oriented overview of every experiment run in this directory. Per-run SUMMARYs have the full numbers; this document is for stepping back and looking at the whole picture.

**Status as of 2026-06-02:** three runs complete, one in progress.

---

## What was tested, in order

| # | Experiment | n | Status | Headline |
|---|---|---|---|---|
| 1 | Pilot (DA-PRB) | 3 PRs | ✅ committed `1c44030` | Dissent crew dominates, +20pp recall. *Did not replicate.* |
| 2 | Main run (DA-PRB) | 50 PRs | ✅ committed `d70a58e` | Pilot reversed. Dissent ≠ better; multi-pass beats naive single by +7pp. |
| 3 | Persona ablation | 50 PRs | ✅ committed `944ab2c` | 3-persona crew (K+H+T) beats the full 6-crew by +6.4pp. Named archetypes don't improve recall vs generic, but produce 18% more semantic divergence. |
| 4 | Triple composition search | 40-50 PRs per tested triple | ✅ partial coverage | 10 of 20 triples tested. **K+H+T remains the best point estimate**, but several challengers are statistical ties and 10 triples remain untested. |

---

## Cumulative findings, ranked by confidence

### HIGH confidence (n=50, paired sign test p<0.05, large effect)

1. **A 3-persona crew of Knuth + Hickey + Torvalds beats the full 6-crew on PR review recall.**
   - +6.4pp recall (0.215 vs 0.151), 16-7 wins out of 50, p=0.047
   - Also wins on precision (0.106 vs 0.084) and fabrication rate (0.645 vs 0.679)
   - Source: `runs/personas/SUMMARY.md`

2. **Named archetypes do NOT improve recall over generic numbered reviewers.**
   - Δ = 0.000, 12-11 wins, p=0.50
   - Names are not the active ingredient for output quality
   - Source: `runs/personas/SUMMARY.md`

3. **Multi-perspective review beats a naive single Claude call.**
   - +7.4pp recall (named-6 0.270 vs naive 0.196 in main run), 24-8 wins, p=0.004
   - The headline OSS-pitch claim that survives
   - Source: `runs/main/SUMMARY.md`

4. **Personas DO diverge semantically.**
   - Named-6 mean Jaccard distance: 0.565 (LLM-classified)
   - Generic-6: 0.477 (~18% less divergent)
   - Named-6's higher divergence is the auditable-disagreement UX product
   - Source: `runs/main/SUMMARY.md` + `runs/personas/SUMMARY.md`

### MEDIUM confidence (n=50, borderline significance)

5. **The choice of which 3 personas matters; don't substitute arbitrarily.**
   - Triple K+H+T > Triple D+L+P by +5.4pp, 17-8 wins, p=0.054 (borderline)
   - Likely cause: D+L+P has Liskov+Pike overlap on architectural lens; K+H+T spans 3 orthogonal axes
   - Source: `runs/personas/SUMMARY.md`

### NULL / NOT VALIDATED

6. **Preserved-dissent synthesis does NOT improve recall over consensus synthesis.**
   - Δ = +0.012, 10-8 wins, p=0.41 (NULL)
   - Pilot's +20pp dominance was an artifact (judge bias + n=3 noise)
   - Dissent visibility is still kept in docs as a transparency feature, not a quality claim
   - Source: `runs/main/SUMMARY.md`

7. **A single persona alone is statistically indistinguishable from the full 6-crew on recall.**
   - Best solo (Dijkstra) at 0.175 vs named-6 at 0.151, NS
   - All 6 solo personas within ±2pp of the crew synthesis
   - Implication: 1-persona is a defensible budget mode, but doesn't win
   - Source: `runs/personas/SUMMARY.md`

### MEDIUM confidence (added 2026-06-02 by run #4)

8. **K+H+T is the best tested triple so far.**
   - All 9 challengers have negative point estimates vs K+H+T (range −0.010 to −0.080 recall)
   - 2 challengers are clearly worse; the other 7 are statistical ties with negative point estimates
   - Challenger triples have n=40-42 materialized scores, while K+H+T and D+L+P have n=50
   - Only 10 of 20 possible triples were tested, so this supports the default but does not prove a global optimum
   - **Hickey appears in 3 of the top 4 triples** — the single strongest predictor
   - **Pike-containing triples cluster near the bottom** (4 of bottom 5)
   - Source: `runs/triples/SUMMARY.md`

---

## Per-persona profile (the basis for the triple search)

Measured across the main run (verbose) and persona run (terse cap, n=50 each):

| Persona | Brief size | Solo recall (terse) | Solo P0 rate | Role in K+H+T |
|---|---|---|---|---|
| **Knuth** | 8,127 chars | 0.144 (worst solo) | 5.4% | rigor + literate |
| **Hickey** | 8,862 chars | 0.172 | 5.8% | simplicity + data |
| **Torvalds** | 7,774 chars | 0.139 (2nd-worst) | **12.6% (high)** | pragmatic + bugs |
| Liskov | 8,355 chars | 0.174 | 7.3% | abstraction (overlaps Hickey) |
| Pike | 8,484 chars | 0.163 | 4.0% | composition (overlaps Hickey) |
| Dijkstra | 8,046 chars | **0.175 (best solo)** | **16.0% (highest)** | formal (overlaps Knuth) |

**Surprising:** The "extended roster" (D, L, P) personas are individually STRONGER as solos than the default (K, H, T). The winning Triple-A is not made of the strongest individuals — it's made of the most *orthogonal* ones. This is the ensemble-learning lesson: decorrelated errors > strong individuals.

**Per-axis breakdown of the 6 personas:**
- Rigor / formal: **Knuth, Dijkstra** (2)
- Architectural / abstract: **Hickey, Liskov, Pike** (3)
- Pragmatic / shipping: **Torvalds** (1)

K+H+T uniquely spans all three axes with no internal redundancy. D+L+P has rigor (D) + 2 architectural (L+P) — missing the pragmatic axis and doubling on architectural.

---

## What the user asked + how we responded

| User request | Response | Result |
|---|---|---|
| "Test the crew on a real benchmark" | Built DA-PRB harness on `foundry-ai/swe-prbench` | Pilot ran, gave optimistic n=3 result |
| "Put it in the OSS repo as tests" | Committed full harness + pilot at `1c44030` | Reproducible from clone |
| "What's left — should we drop dissent?" | Ran n=50 with bias-mitigated judge | Pilot null; pivoted OSS framing |
| "Drop dissent if it doesn't work; play with personas" | Persona ablation: solos vs sextuplet vs triples vs generic | Triple K+H+T wins; names don't help recall |
| "Maybe some personas are weaker?" | Profile + triple composition search (in progress) | Profile says individuals are fine; testing if K+H+T is optimal among C(6,3) |

---

## The harness (so you can re-run anything)

- **No API keys needed.** Everything dispatches via the Workflow tool using Claude Code credentials.
- Substrate: `foundry-ai/swe-prbench` (eval_split, 100 PRs)
- Sample: stratified by language, seed=42, deterministic
  - Pilot: 3 PRs (`data/prs_pilot.json`)
  - Main + persona + triple: same 50 PRs (`data/prs_main.json`)
- Judge: Claude (anonymized + skeptic-framed, identical across all runs)
  - Recorded as a deviation; the protocol calls for GPT-5.1 with `OPENAI_API_KEY`
- All runs use the same persona briefs (`prompts/{persona}_agent.md`) and the consensus-style synthesis (`prompts/synthesis_consensus.md`)

To reproduce any run from scratch:

```bash
cd experiments/2026-06-01-dissent-ablation
uv sync
uv run python scripts/select_prs.py --main           # → data/prs_main.json (deterministic)
uv run python scripts/prepare_main_prompts.py        # → data/main_prompts.json
uv run python scripts/gen_main_workflow.py           # → scripts/main_workflow_{a,b}.js
# inside Claude Code:
#   /workflow scripts/main_workflow_a.js
#   /workflow scripts/main_workflow_b.js
uv run python scripts/materialize_main.py <transcript-path>
uv run python scripts/analyze.py --run main
```

---

## Open questions / what we'd test next

- Is K+H+T the actual optimum among 6-persona triples? → run #4 supports it across 10 tested triples, but this remains open until the remaining 10 triples are scored or deliberately skipped.
- Could a **2-persona pair** (K+H, H+T, K+T) come within 1-2pp of K+H+T at lower cost? (not tested; obvious next test)
- Does a **larger crew (8+) with council additions** (Beck, Lamport, Hoare, Naur, Armstrong, Brooks) beat K+H+T? (current finding suggests adding personas degrades the synthesis, so probably no — but untested)
- Does the **active-ingredient pattern** (orthogonal lenses > strong individuals) replicate on a different task than PR review — say, design critique or debugging? (different substrate)
- **Non-Claude judge** (GPT-5.1 or Gemini 2.5 Pro): would absolute numbers shift, would the ordering change? (requires API key; deferred)
- **Would rewriting Dijkstra/Liskov/Pike briefs make them competitive replacements in the triple?** Probably not — the issue isn't their solo capability (they're individually strong) but their lens-overlap with the existing K+H+T members. A rewrite would need to invent net-new orthogonal axes, not just sharpen the current ones.

---

## Key methodology notes (load-bearing for interpreting numbers)

1. **Judge is Claude throughout.** Anonymized + skeptic-framed mitigates self-preference but doesn't eliminate it. Relative comparisons within a run are more robust than absolute numbers because both arms share any bias.

2. **Terse-output rules (`max 6 issues, ≤60-word details`)** were applied uniformly to all 11 arms of the persona run and the triple search, to prevent token-limit failures at parallel-workflow scale. Within-run comparisons remain valid; absolute numbers cannot be directly compared to the main run (which had verbose outputs).

3. **The sanity vs naive comparison in the persona run is methodologically loose** because the naive baseline was carried over from the main run (no terse cap). The headline "multi-pass beats naive" claim should be cited from the **main run**, not the persona run.

4. **Sample size:** All comparisons except the pilot are n=50. The protocol's n=80 wasn't run (would require splitting into more workflow shards). McNemar effective power at n=50 with the observed effect sizes: borderline for HP4, comfortable for HP1/HP3/main-run H1.

5. **Pre-registration:** PROTOCOL.md (frozen 2026-06-01) and PROTOCOL_PERSONA.md (2026-06-02) state hypotheses before any of the corresponding runs. Any deviations are dated in DEVIATIONS.md.

---

## Open items requiring a decision before final OSS release

- [ ] Decide whether to rerun/complete the triple search to full n=50 for every tested challenger and score the remaining 10 triples
- [ ] Decide whether to invest in a non-Claude judge run (cost: ~$260 + API keys) to retire the judge-bias caveat
- [ ] Decide whether the n=50 sample is enough, or if it should be expanded to 80 per the original protocol
- [ ] Decide whether to fold this dir's findings up into the top-level code_crew README, or keep the OSS pitch separate from the experimental record

---

## Files of record

- `PROTOCOL.md` — frozen pre-registration of the dissent ablation
- `PROTOCOL_PERSONA.md` — frozen pre-registration of the persona ablation
- `DEVIATIONS.md` — every methodology deviation, dated
- `runs/pilot/SUMMARY.md` — n=3 pilot writeup
- `runs/main/SUMMARY.md` — n=50 dissent ablation writeup
- `runs/personas/SUMMARY.md` — n=50 persona ablation writeup
- `runs/triples/SUMMARY.md` — partial triple composition search writeup
- `runs/{run}/ANALYSIS.json` — machine-readable stats for each run
- Raw per-PR outputs under `runs/{run}/<task_id>/` (committed; ~3-5MB per run)
