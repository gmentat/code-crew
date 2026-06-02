# Persona Framing Ablation Protocol

**Pre-registered:** 2026-06-02. Single-variable A/B on how the persona is introduced in the brief. Reuses the same n=50 PRs as the main run; only the K+H+T crew is tested.

## Question

Does directly naming the real person and listing concrete accomplishments — instead of the current "reasoning archetype inspired by X's public work" framing — change PR review quality?

Hypothesis prompted by the user's observation that briefs could be more concrete (e.g. "Edsger W. Dijkstra — originator of structured programming, author of 'Go To Statement Considered Harmful' (1968), Dijkstra's algorithm, semaphores, the THE multiprogramming system, ... Not an impersonation, endorsement, or claim to speak for him").

## Variable isolated

Only the **first content paragraph** of each persona brief differs. The header line (`# Knuth — Algorithmic Rigor & Literate Programming`), the Invocation section, the Role section, Core Identity, Operating Principles, Process, Decision Labels, Tone, Disagreement Patterns, and Motto — all are byte-identical across A and B. The diff is one paragraph per brief.

- **Style A (control)**: "Reasoning archetype inspired by the public work and operating style of Donald E. Knuth — author of *The Art of Computer Programming*, ... Not an impersonation, endorsement, or claim to speak for him."
- **Style B (treatment)**: "Donald E. Knuth — author of *The Art of Computer Programming* (seven-volume series begun in 1968), originator of literate programming (1984 paper 'Literate Programming'), creator of the TeX typesetting system (1978) and METAFONT, inventor of the Knuth–Morris–Pratt string-matching algorithm, of LR(k) parsing analysis, ... Recipient of the 1974 ACM Turing Award ... Not an impersonation, endorsement, or claim to speak for him."

Both styles end with the same non-impersonation disclaimer.

## Substrate

Same 50 PRs as the main run (`data/prs_main.json`, seed=42). Same anonymized + skeptic-framed judge as all prior runs. Same terse-output cap on the blind passes (max 6 issues, ≤60-word details).

## Arms

- **Arm A (control)**: K+H+T blind passes with the existing briefs, consensus synthesis, judged. **Reuses** existing scores from `runs/personas/<task_id>/scores/named-6.json` — wait, that's the sextet. The K+H+T-only arm is `runs/personas/<task_id>/scores/triple-A.json`. Reusing those scores.
- **Arm B (treatment)**: K+H+T blind passes with the **direct-named** briefs (`prompts/{knuth,hickey,torvalds}_agent_direct.md`), consensus synthesis, judged. All new generation.

Per PR new work for Arm B: 3 persona passes + 1 synthesis + 1 judge = **5 agents**. 50 PRs × 5 = 250 agents. Sharded into 2 workflows of 25 PRs each (125 agents/shard).

## Hypothesis

- **H_framing**: Style B (direct-named) produces ≥2pp higher mean recall than Style A on paired sign test (one-sided, α=0.05). Direction not pre-committed in the alternative — recall could go either way; this is exploratory.
- **Falsifies**: |Δ recall| < 2pp AND p>0.10.

Secondary measures:
- Mean precision per arm
- Mean fabrication rate per arm (high empirical interest: does named accomplishment increase risk of fabricated "Knuth said..." quotes?)
- Mean issues flagged per arm

## Decision rule

| Outcome | Action |
|---|---|
| Style B > Style A (Δ recall ≥ +2pp, p<0.05) | Update all bundled briefs in `plugins/code-crew/skills/code-crew/briefs/` to direct-named style; bump plugin to v0.3.0; reference this experiment in CLAUDE.md and SKILL.md. |
| Style A > Style B (Δ recall ≤ −2pp, p<0.05) | Keep current "archetype-inspired" framing; note in CLAUDE.md that direct naming was tested and underperformed. |
| Null (|Δ| < 2pp, p>0.10) | Keep current framing for stylistic / liability reasons (the disclaimer is clearer in archetype form); note in docs that framing has no measured effect on recall. |
| Mixed (e.g. recall ties, fabrication differs significantly) | Report both findings, choose framing optimizing the dominant secondary metric. |

## Cost

- Generation: ~250 subagents
- Total: well under one workflow's lifetime cap

## Out of scope

- This experiment does not test other personas (Dijkstra, Liskov, Pike) under both framings. If Style B wins for K+H+T, applying it to the other 3 is a follow-up.
- This experiment uses the same judge (Claude, anonymized + skeptic) as all prior runs. A non-Claude judge could shift absolute numbers; relative comparison should be robust.
- This experiment does not vary the body of the briefs (operating principles, process, etc.). Those stay identical so the only variable is the lead paragraph framing.
