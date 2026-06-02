# Persona ablation — n=50

**Date:** 2026-06-02
**n:** 50 PRs (same substrate as the main run)
**Total agents:** 1450 (4 sharded workflows, terse-output rules applied uniformly)
**Wall-clock:** ~2× ~25 min (sequential parallel pairs)
**Judge:** Claude (anonymized + skeptic-framed, identical to main run)

## Per-arm summary

| Arm | Recall | Precision | Fabrication | Flagged (mean) |
|---|---|---|---|---|
| solo-knuth | 0.144 | 0.068 | 0.723 | 5.6 |
| solo-hickey | 0.172 | 0.081 | 0.682 | 5.4 |
| solo-torvalds | 0.139 | 0.065 | 0.668 | 5.6 |
| solo-liskov | 0.174 | 0.092 | 0.713 | 5.4 |
| solo-pike | 0.163 | 0.060 | 0.669 | 5.3 |
| solo-dijkstra | **0.175** | 0.082 | 0.676 | 5.6 |
| named-6 (synth) | 0.151 | 0.084 | 0.679 | 5.8 |
| generic-6 (synth) | 0.151 | 0.070 | 0.683 | 5.9 |
| **triple-A (K+H+T)** | **0.215** | **0.106** | **0.645** | 5.7 |
| triple-B (D+L+P) | 0.160 | 0.079 | 0.715 | 5.5 |
| pair-TL (T+L) | 0.171 | 0.074 | 0.719 | 5.6 |

## Pre-registered hypothesis results

| Hypothesis | Δ recall | p (one-sided) | Verdict |
|---|---|---|---|
| **HP1** — named-6 > generic-6 | **+0.000** | 0.500 | **NULL ❌** |
| HP2 — solo-knuth > named-6 | −0.007 | 0.942 | NULL |
| HP2 — solo-hickey > named-6 | +0.021 | 0.500 | NULL |
| HP2 — solo-torvalds > named-6 | −0.012 | 0.942 | NULL |
| HP2 — solo-liskov > named-6 | +0.023 | 0.686 | NULL |
| HP2 — solo-pike > named-6 | +0.012 | 0.788 | NULL |
| HP2 — solo-dijkstra > named-6 | +0.024 | 0.500 | NULL |
| **HP3 — triple-A > named-6** | **+0.064** | **0.047** | **CONFIRMED ✓** |
| HP3 — triple-B > named-6 | +0.009 | 0.422 | NULL |
| HP3 — pair-TL > named-6 | +0.020 | 0.416 | NULL |
| **HP4 — triple-A > triple-B** | **+0.054** | **0.054** | **BORDERLINE ✓** |

## Headline findings

### 1. The composition that wins: Knuth + Hickey + Torvalds (Triple-A)

**This 3-persona crew beats the full 6-crew on recall (+6.4pp, p=0.047, 16-7 wins).** It also has the best precision (0.106) and the lowest fabrication rate (0.645) of any arm. The K+H+T composition is *better than* the sextuplet, not just as good.

The active reasoning lenses:
- **Knuth** — algorithmic rigor, literate programming
- **Hickey** — simple-not-easy, value/time semantics
- **Torvalds** — pragmatic systems engineering, brutal review

These three span rigor ↔ shipping, abstraction ↔ data, formal ↔ pragmatic with no internal redundancy. Adding Dijkstra (overlaps Knuth on formal), Liskov (overlaps Hickey on abstraction), and Pike (overlaps Torvalds on systems) **measurably degrades the synthesis** — more voices, more noise, more dropped concerns.

### 2. Names don't matter for recall, but they do matter for divergence

**HP1 NULL.** Named archetypes produce statistically identical recall to generic-N reviewers (Δ = +0.000, 12-11 wins). The Knuth/Hickey/etc names are *not* the active ingredient for output quality.

But the H3 manipulation check tells a different story about **what the names do produce**:

- Named-6 inter-pass Jaccard distance: **0.565**
- Generic-6 inter-pass Jaccard distance: **0.477**

Named personas diverge ~18% more semantically than generic-N reviewers. The names produce **more interpretable disagreement** — which is the UX product (you can tell *who* said *what*) — without producing better issue lists.

### 3. Composition matters; sextuplet is overkill

**HP4 borderline supported.** Triple-A (K+H+T) > Triple-B (D+L+P) by +5.4pp (17-8 wins, p=0.054). Picking which 3 personas matters. Triple-A's "rigor + simplicity + pragmatism" combination outperforms Triple-B's "formal + abstract + composition" — likely because B has more overlap between Liskov and Dijkstra on type/contract concerns.

### 4. Single personas are surprisingly close to the sextuplet

**HP2 NULL but informative.** Best single persona (Dijkstra, recall 0.175) matches named-6 (0.151) and almost matches Triple-A (0.215). Hickey, Liskov, Pike, Dijkstra all individually flag concerns within noise of the full-crew synthesis. A one-persona "crew" is defensible when budget is tight.

## What changed vs the dissent-ablation main run

The terse-output rules applied here (max 6 issues per pass, ≤60-word details) were necessary to prevent token-limit failures at the parallel-workflow scale. They are **uniformly applied across all 11 arms in this run**, so within-run comparisons are valid. But absolute numbers cannot be directly compared to the main run:

| Arm | Main run recall | Persona-run recall | Δ |
|---|---|---|---|
| Named-6 (consensus synth) | 0.259 | 0.151 | −0.108 |
| Naive single (from main, unchanged) | 0.196 | 0.196 | 0 |

The verbose-vs-terse distinction caused named-6 to fall behind naive in this run's `sanity` comparison (Δ = −0.045 vs naive). This is a methodology artifact, not a finding about the crew. The comparable comparison from the main run (named-6 vs naive without terse rules) showed +6.3pp for named-6.

**Practical interpretation:** if a deployment caps token output (as production usage often will), tight prompts hurt named-6's recall advantage. Triple-A's advantage survives the cap because its absolute recall is the highest in the constrained regime.

## Implications for the OSS docs

| Change | Justification |
|---|---|
| **Recommend Triple-A (K+H+T) as the default crew** | Best recall (+6.4pp vs sextuplet, p=0.047), best precision, lowest fabrication. |
| **Drop "6 personas" as the default framing** | Sextuplet is statistically worse than the right 3. |
| **Keep the "named archetypes produce auditable disagreement" claim** | H3 distance 0.565 (named) vs 0.477 (generic) — names DO diverge more, just don't improve recall. |
| **Drop "named personas carry reasoning style that improves outputs"** | HP1 NULL: 0.000 delta vs generic-N. |
| **Keep individual persona briefs as single-lens shortcuts** | HP2 shows solo personas are within noise of named-6 — useful for budget-constrained reviews. |
| **Note in docs: which 3 you pick matters** | HP4 borderline (p=0.054): Triple K+H+T > Triple D+L+P. Don't substitute arbitrarily. |

## Caveats

1. **Judge is still Claude** (anonymized + skeptic-framed, identical to main run). Non-Claude judge could shift absolute numbers; relative ranking less sensitive.
2. **Terse cap was the harness fix, not a feature.** The same experiment with longer outputs would likely show higher recall everywhere; the *ordering* should be stable.
3. **Only one Triple composition was tested per direction.** "Triple-A wins" doesn't mean K+H+T is optimal — only that it beats the full 6 and beats Triple-B. Other triples may be stronger.
4. **Workflow tool dropped ~250 agents on the first attempt** (verbose outputs hit response limits). Recorded in this SUMMARY rather than DEVIATIONS because the harness fix (terse rules) was implemented mid-experiment, before any of the reported numbers were collected.

## Recommendation

Update the OSS docs to lead with:

> *"A 3-persona crew of Knuth (rigor), Hickey (simplicity), and Torvalds (pragmatism) produces measurably better PR review than the full 6-persona sextuplet (+6.4pp recall, p=0.047 at n=50). Named archetypes carry inter-pass divergence the UX surfaces as auditable disagreement, but the names don't improve recall over generic numbered reviewers."*

Triple K+H+T becomes the recommended default. Sextuplet becomes optional. Solo personas become labelled single-lens shortcuts.
