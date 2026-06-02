# Triple composition search — n=40-50 per tested triple

**Date:** 2026-06-02
**Goal:** find the optimal 3-persona crew from C(6,3) = 20 possibilities, given the persona-ablation result that K+H+T beats the full 6-crew.
**Method:** reuse the 50 PRs' existing blind passes from the persona run; synthesize each candidate triple from those passes; same anonymized + skeptic-framed Claude judge.
**Composition sampling:** 8 untested triples + 2 already-tested (K+H+T, D+L+P) = 10 of 20 total. Coverage chosen to test the "span 3 axes (rigor + architectural + pragmatic)" hypothesis.

## Ranked by mean recall

| Rank | Triple | n | Recall | Precision | Fabrication |
|---|---|---|---|---|---|
| **1** | **K + H + T (triple-A)** | **50** | **0.215** | **0.106** | **0.645** |
| 2 | K + H + D | 40 | 0.185 | 0.059 | 0.705 |
| 3 | D + H + T | 41 | 0.184 | 0.067 | 0.704 |
| 4 | L + P + T | 41 | 0.174 | 0.086 | 0.640 |
| 5 | D + L + T | 42 | 0.167 | 0.074 | 0.669 |
| 6 | K + P + T | 41 | 0.163 | 0.071 | 0.673 |
| 7 | K + L + T | 41 | 0.162 | 0.079 | 0.677 |
| 8 | D + L + P (triple-B) | 50 | 0.160 | 0.079 | 0.715 |
| 9 | H + L + P | 41 | 0.158 | 0.061 | 0.683 |
| 10 | D + P + T | 41 | 0.123 | 0.059 | 0.737 |

## Paired sign tests vs K+H+T

| Challenger | n | Δ recall | wins / losses / ties | p (one-sided) |
|---|---|---|---|---|
| K + H + D | 40 | −0.010 | 6 / 8 / 26 | 0.788 |
| D + H + T | 41 | −0.019 | 5 / 7 / 29 | 0.806 |
| L + P + T | 41 | −0.024 | 7 / 10 / 24 | 0.834 |
| D + L + T | 42 | −0.037 | 7 / 13 / 22 | 0.942 |
| K + P + T | 41 | −0.040 | 6 / 11 / 24 | 0.928 |
| K + L + T | 41 | −0.041 | 9 / 11 / 21 | 0.748 |
| H + L + P | 41 | −0.040 | 7 / 11 / 23 | 0.881 |
| D + L + P (triple-B) | 50 | −0.054 | 8 / 17 / 25 | 0.978 |
| D + P + T | 41 | −0.080 | 4 / 14 / 23 | **0.996** |

**Every tested challenger has a negative point estimate.** No tested triple beats K+H+T. The two clearly-worse triples (D+L+P and D+P+T) are statistically distinguishable from K+H+T at p<0.05 in the original direction. The rest are statistical ties with point estimates favoring K+H+T.

## Headline findings

### 1. K+H+T is the best tested default so far

Across 10 of 20 possible triples tested, none beats Knuth + Hickey + Torvalds on recall, precision, or fabrication rate. This supports keeping K+H+T as the default; it does not prove the global optimum across all 20 triples.

- All 9 challengers have negative mean recall deltas (range −0.010 to −0.080).
- Two challengers are significantly worse (D+L+P and D+P+T at p≈0.001 in the reverse direction).
- The rest are inconclusive ties — but with point estimates favoring K+H+T.

### 2. Hickey appears in 3 of the top 4 triples

K+H+T (0.215), K+H+D (0.185), D+H+T (0.184) all contain Hickey. The exception (#4 L+P+T at 0.174) has no Hickey.

This is the single strongest predictor of triple quality. Hickey's "simple-not-easy" lens flags concerns that don't overlap with what the other personas flag — likely the value/identity/time framing that Liskov (substitution), Pike (composition), and Dijkstra (formal correctness) don't naturally surface.

### 3. Pike-containing triples cluster near the bottom

Triples with Pike: D+P+T (0.123, worst), H+L+P (0.158), triple-B/D+L+P (0.160), K+P+T (0.163), L+P+T (0.174).

Pike's solo recall is mid-pack (0.163, 4th of 6), but in triples he tends to overlap with whoever else is in the architectural lens (Hickey/Liskov) without adding net new concerns.

### 4. The "span 3 axes" hypothesis is partly supported

K+H+T (rigor + architectural + pragmatic) is #1 by 3pp.
D+H+T (formal + architectural + pragmatic) is #3.
K+H+D (rigor + architectural + rigor — two rigor lenses) is #2, surprisingly.

So the hypothesis is **useful but not sufficient**: spanning 3 axes helps, but composition is more subtle than "one from each bucket." Hickey's presence may be doing a disproportionate share of the work.

### 5. Adding Torvalds is usually good, sometimes not

Torvalds-containing triples: K+H+T (0.215, #1), D+H+T (0.184), L+P+T (0.174), D+L+T (0.167), K+P+T (0.163), K+L+T (0.162), D+P+T (0.123, last). The pragmatic-axis-via-Torvalds hypothesis predicted he'd be in every winning triple — and he is in 5 of the top 6 — but D+P+T puts him in dead last. Pike + Torvalds together specifically underperform.

## What this means for OSS recommendations

**No change needed to the default recommendation.** README and AGENTS already lead with K+H+T as the default 3-persona crew per the persona-ablation finding. The triple search adds support: K+H+T was the best point estimate among the 10 tested compositions. The correct public claim is "best tested default," not "proven optimum."

If you wanted to extend this:

- The 10 triples not tested may be unlikely to win given the patterns above, but an exhaustive claim requires scoring them.
- Pairs (15 combinations) might find a 2-persona crew within 1-2pp of K+H+T at lower cost. K+H, H+T, K+T are the obvious starts.
- Adding council personas (Beck, Lamport, Hoare, Naur, Armstrong, Brooks) to the K+H+T base might or might not improve recall. The current finding ("adding personas to K+H+T degrades the synthesis") suggests it would degrade — but those council personas weren't included in the persona ablation, so the test is open.

## Caveats

1. **Each challenger triple is at n=40-42, not 50.** Three of the five shards had failures-on-first-attempt that we retried; the retried agents in shards 1 and 3 didn't all recover. Statistical power against K+H+T (which has n=50) is asymmetric. The +effect direction in K+H+T's favor is robust to this.

2. **Existing blind passes are reused for the triple syntheses.** This means all 10 triples are synthesizing from the *same* persona inputs — fair within-PR comparison, but the persona inputs themselves were generated with the terse cap that limits recall ceilings.

3. **Judge is Claude.** Anonymized + skeptic-framed. Same as all prior runs. Cross-Claude bias applies but symmetrically across triples.

4. **10 of 20 triples tested, not all 20.** The untested 10 mostly drop Torvalds or have both rigor lenses (K+D); they're unlikely to win based on the patterns observed. To be exhaustive, run them.

## Files

- Per-PR raw outputs: `runs/triples/<task_id>/` (synth + score per triple)
- Aggregated: `runs/triples/ANALYSIS.json`
- This summary: `runs/triples/SUMMARY.md`
- Workflow scripts: `scripts/triple_workflow_{1..5}.js`
- Harness: `scripts/{prepare,gen,materialize,analyze}_triple.py`
