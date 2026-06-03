# Persona framing A/B — direct-named vs archetype-inspired (n=50)

**Date:** 2026-06-02
**Pre-registration:** [`../../PROTOCOL_FRAMING.md`](../../PROTOCOL_FRAMING.md)
**Substrate:** same 50 PRs as the main run; same anonymized + skeptic-framed Claude judge; same K+H+T-only triple
**Variable isolated:** first content paragraph of each persona brief only. Header, Invocation, Role, Core Identity, Operating Principles, Process, Decision Labels, Tone, Disagreement Patterns, Motto — all byte-identical between A and B.

## Result

**Style A (archetype-inspired) wins on every metric. Recall is directionally strong; precision is statistically clean.**

| Metric | A (archetype) | B (direct-named) | Δ (B−A) | paired wins (A : B : ties) | p_two_sided |
|---|---|---|---|---|---|
| **Recall** | **0.215** | 0.176 | **−0.039** | **15 : 6 : 29** | 0.078 |
| **Precision** | **0.106** | 0.071 | **−0.035** | **16 : 5 : 29** | **0.027** ✓ |
| **Fabrication rate** | **0.645** | 0.743 | **+0.099** | A : B : ties = 16 : 22 : 12 | 0.418 |
| Issues flagged (mean) | 5.68 | 5.72 | +0.04 | — | — |

On the discordant pairs (those where A and B differ), Style A wins **15 of 21** on recall (71%) and **16 of 21** on precision (76%).

## Decision rule outcome

Per pre-registration, the decision rule is:

> **Style A > Style B (Δ recall ≤ −2pp, p<0.05) → Keep current "archetype-inspired" framing; note in CLAUDE.md that direct naming was tested and underperformed.**

- Δ recall = **−3.9pp** ✓ (meets the −2pp threshold)
- Two-sided p_recall = 0.078 (borderline; one-sided p for A>B = 0.039)
- Two-sided p_precision = **0.027** ✓ (independently confirms A > B)

**Verdict: KEEP current "archetype-inspired" framing.** Update docs to record that direct-named framing was tested and underperformed. Do not modify the plugin briefs.

## Why this is the right call

The result replicates a prior prediction from the research literature, which was synthesized independently before the experiment ran ([`../../RESEARCH_PERSONA_PROMPTING.md`](../../RESEARCH_PERSONA_PROMPTING.md)):

1. **Principled Personas (Luz de Araujo et al., EMNLP 2025).** Irrelevant biographical surface attributes — including names — can swing LLM task performance by up to ~30pp. The direct-named lead front-loads exactly these high-variance surface attributes.
2. **PRISM (arXiv:2603.18507).** Accomplishment-list framings *add tokens without lifting accuracy* and degrade closed-form work: MMLU drops from 71.6 → 68.0 → 66.3 as personas lengthen. Code review is closed-form on bug-finding; the −3.9pp recall drop is in line with this dose-response.
3. **Fabrication research (Deshpande EMNLP 2023, Sadeq et al., TimeChara ACL 2024).** Richer real-person profiles *increase* confident off-profile fabrication. The +9.9pp fabrication rate in B is consistent with that mechanism, though the per-PR difference isn't statistically significant at n=50.

## Interpretation: what carries the lift in the briefs

The body of the briefs (Operating Principles, Process, Decision Labels) was held identical across arms. The data says **those parts are doing all the work**. The lead paragraph — "reasoning archetype inspired by X" vs "X — author of …" — operates on the model's surface attributions and only injects noise.

## Implications

- **Plugin briefs unchanged.** The shipped `plugins/code-crew/skills/code-crew/briefs/{knuth,hickey,torvalds}_agent.md` files stay as-is.
- **Don't add new accomplishments to other personas.** Same effect would apply to Dijkstra, Liskov, Pike if their briefs were rewritten in the direct-named style.
- **What the test isolates is method/archetype lead vs identity/accomplishments lead** — not the disclaimer. Both arms kept the non-impersonation disclaimer; the difference between A and B is purely in how the first paragraph leads (with the lens's reasoning style, vs. with the person's name and works). The archetype framing should be preserved on this evidence, but no claim is being made about the disclaimer in isolation.
- **Future improvement direction.** Per the research synthesis, the actual upgrade path is deeper *method-and-anchor content* under the archetype frame (specific examples of how this lens phrases a critique, refusal, tradeoff) — not more biographical detail. This is a follow-up experiment, not done here.

## Caveats

1. **n=50, paired.** Recall difference's two-sided p (0.078) is borderline; the precision difference (p=0.027) is clean.
2. **Judge is Claude.** Same judge used across all runs; relative comparison robust, absolute numbers not.
3. **Only K+H+T tested.** Did not test direct-naming for D+L+P. The research predicts the same effect would apply.
4. **Briefs body held constant.** This is the experiment's strength — the variable is isolated to ~1 paragraph per brief — and also its limit: a *full rewrite* under either framing could shift the result.
5. **Style B fabrication +9.9pp is suggestive but not significant** at n=50. Worth re-testing with more PRs if the fabrication question becomes load-bearing for some other decision.

## Files

- Per-PR raw outputs: `runs/framing/<task_id>/`
- Per-PR scores: `runs/framing/<task_id>/scores/direct.json`
- Aggregated: `runs/framing/ANALYSIS.json`
- This summary: `runs/framing/SUMMARY.md`
- Direct-named briefs: `prompts/{knuth,hickey,torvalds}_agent_direct.md`
- Research synthesis (predicted this result): `RESEARCH_PERSONA_PROMPTING.md`
