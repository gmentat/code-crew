# Persona Ablation Protocol

**Pre-registered:** 2026-06-02. Builds on the same substrate (`foundry-ai/swe-prbench` eval_split, n=50 PRs from `data/prs_main.json`, seed=42) and reuses the blind passes already produced by the main dissent-ablation run, so this study has zero substrate noise vs that run.

## Question

The dissent ablation showed multi-perspective review beats naive single-pass on PR review recall, but didn't isolate *what makes the crew work*. This study tests:

- **Q1 — Does the named-archetype framing matter?** Or is six independent identical "review this carefully" passes from the same model equally good?
- **Q2 — Which single persona is best alone?** Could we ship a one-persona crew?
- **Q3 — Are smaller crews competitive?** Pairs and triples vs the full sextuplet, on recall.
- **Q4 — Does the choice of personas matter?** Two hand-picked triples with different reasoning emphases — do they perform differently?

## Hypotheses (pre-registered)

### HP1 — Named personas vs generic reviewers

Six **named** personas with distinct briefs (Knuth, Hickey, Torvalds, Liskov, Pike, Dijkstra) → consensus synthesis produces ≥3pp higher mean recall than six **generic** reviewers with the same instruction template ("review this PR; flag concerns specific to this diff") → consensus synthesis. Paired sign test, one-sided, p<0.05.

- **Falsifies:** Generic-6 ≈ Named-6 → name + brief is just costume; multi-pass independence is the active ingredient.
- **Confirms:** named archetypes carry reasoning style that survives sampling and improves outputs.

### HP2 — Single best persona

At least one of the six named personas alone (judged on its blind-pass output) achieves mean recall within 2pp of the full named-6 synthesis. If so → a one-persona crew may be defensible; we ship that persona's brief as a recommended single-lens shortcut.

### HP3 — Smaller crew competitiveness

A 3-persona crew (either hand-picked triple) achieves mean recall within 2pp of named-6. If so → cap recommended crew size at 3; sextuplet is overkill.

### HP4 — Persona composition matters

Triple A (Knuth + Hickey + Torvalds, "rigor + simplicity + pragmatism") differs from Triple B (Dijkstra + Liskov + Pike, "formal + abstract + composition") by ≥3pp recall on at least one direction. If null → which 3 personas you pick doesn't matter for recall; pick by other criteria (UX, taste).

## Arms

All scored on the same 50 PRs as the main run.

| Arm | Composition | Reuses main-run data? |
|---|---|---|
| **naive** | Single Claude, naked prompt | YES (existing single_naive.json) |
| **named-6** | Knuth+Hickey+Torvalds+Liskov+Pike+Dijkstra → consensus synthesis | YES (existing syntheses/consensus.json) |
| **generic-6** | 6 identical "Reviewer N" passes (same prompt) → consensus synthesis | NO — all new |
| **solo-knuth** | Just Knuth's blind pass, judged alone | YES (existing passes/knuth.json) |
| **solo-hickey** | Just Hickey's blind pass, judged alone | YES |
| **solo-torvalds** | Just Torvalds's blind pass, judged alone | YES |
| **solo-liskov** | Just Liskov's blind pass, judged alone | YES |
| **solo-pike** | Just Pike's blind pass, judged alone | YES |
| **solo-dijkstra** | Just Dijkstra's blind pass, judged alone | YES |
| **triple-A** | Knuth + Hickey + Torvalds → consensus synthesis | YES (passes); new synthesis |
| **triple-B** | Dijkstra + Liskov + Pike → consensus synthesis | YES (passes); new synthesis |
| **pair-TL** | Torvalds + Liskov → consensus synthesis | YES (passes); new synthesis |

Twelve arms. Per PR new work: 6 generic passes + 1 generic synthesis + 1 generic judge + 3 new syntheses (triple-A, triple-B, pair-TL) + 3 new judges + 6 solo judges + 1 H3 manipulation check on generic-6 = **21 new agents per PR**.

50 PRs × 21 = 1050 agents. Sharded into 3 workflow scripts (≤17 PRs each) to stay under Workflow's 524KB script-size cap.

## Judge

Same anonymized + skeptic-framed prompt as the main run. Judge sees only "AI-flagged issues" with `flagged_by` stripped — cannot identify arm.

## Statistical procedure

- Per-PR raw recall on each arm (recall = comments_matched_by_ai / total_human_comments, judged).
- Pairwise sign test (exact binomial) for each named hypothesis pair.
- Primary outcomes:
  - HP1: paired delta recall(named-6) − recall(generic-6), one-sided p.
  - HP2: max single-persona recall − recall(named-6); reported with all 6 deltas.
  - HP3: delta recall(triple-A) − recall(named-6); delta recall(triple-B) − recall(named-6).
  - HP4: delta recall(triple-A) − recall(triple-B).
- Secondary: precision, fabrication rate per arm.

## Decision rules (pre-committed)

| Outcome | Action on docs |
|---|---|
| **HP1 confirmed** (named > generic) | Keep current docs; named archetypes are validated as carrying real reasoning style. |
| **HP1 null** (generic ≈ named) | Reframe README: "the value is multi-pass independence, not persona naming." Personas become an interpretability layer, not an output-quality layer. |
| **HP2 confirmed** (1 persona ≈ 6) | Ship that persona as a recommended single-lens shortcut in README. |
| **HP2 null** | Keep multi-persona recommendation. |
| **HP3 confirmed** (3 ≈ 6) | Recommend triple as default in docs; deprecate the sextuplet as default. |
| **HP3 null** | Keep named-6 as default. |
| **HP4 confirmed** (A ≠ B) | Document which composition is stronger and why. |
| **HP4 null** | Note in docs: "any 3 of the core 6 produce equivalent recall; pick by domain fit." |

## Cost

- Already paid: main-run blind passes for named-6.
- New: ~1050 subagents across 3 shards. Estimated ~30M tokens, ~80 min wall-clock with parallel shards.
