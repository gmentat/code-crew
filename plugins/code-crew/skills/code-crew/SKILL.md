---
name: code-crew
description: Use when the user explicitly asks for Code Crew, K+H+T, famous-programmer review lenses, or an independent multi-lens engineering review. Runs Knuth+Hickey+Torvalds blind passes, a diff-grounded verifier, and synthesis for code review, design critique, and refactoring judgment. Do not auto-invoke for an ordinary review request that does not ask for this workflow.
license: MIT
metadata:
  author: Code Crew contributors
  version: "0.2.4"
  tags: code-review, software-engineering, multi-agent, critique
---

# Code Crew

Use Code Crew when the user explicitly requests the crew, its named lenses, famous-programmer perspectives, or an independent multi-lens review. Do not silently turn every ordinary code review into a multi-agent run.

Formal crew runs require a host that can dispatch independent subagents. Other hosts can run a clearly labelled single-context approximation.

Invocation note: when a user selects this skill or writes `$code-crew ...`, Code Crew is already invoked. Do not search for a separate Code Crew callable tool, and do not report "no callable Code Crew tool" as a blocker. Use the host's native subagent facility when one exists. If the host lacks independent subagent dispatch, label the result as a single-context approximation and continue with the verifier and synthesis rules that can be applied locally.

Code Crew uses reasoning archetypes inspired by famous programmers and computer scientists. These are not impersonations, endorsements, or claims to represent the real people. They are named review contracts: each lens focuses attention on a different kind of engineering failure.

## How To Run A Review

```
1. triage      -> references/triage.md                     <- which crew?
2. discipline  -> references/implementation-discipline.md <- only when changing code
3. lenses      -> references/<persona>.md                  <- per-persona blind passes
4. verify      -> references/verify.md                     <- check candidates against the diff
5. synth       -> references/synthesis.md                  <- decision-changing findings only
6. artifact    -> references/artifact-format.md            <- only if asked
```

Each step is in a file. Load it when you reach that step. Do not skip the verifier: prior runs measured about 64% of unverified K+H+T synthesis findings as fabricated by the judge on SWE-PRBench. The verifier is a defensive precision gate; its incremental effect has not yet been measured independently.

## Default Crew

Once Code Crew is invoked, use **K+H+T** when the user does not name a lens:

- **Knuth** — algorithmic rigor, invariants, complexity, data structures, literate clarity.
- **Hickey** — simplicity vs ease, value/identity/time semantics, incidental complexity.
- **Torvalds** — maintainer-grade patch review, scope control, working systems.

In our SWE-PRBench experiments (n=50 PRs, paired binomial test) this 3-persona crew outperformed the full 6-persona sextet on raw recall (+6.4pp, p=0.047), precision (0.106 vs 0.084), and fabrication rate (0.645 vs 0.679). It also held its lead against 8 other tested triples. Treat that as evidence for this preset, not proof famous names alone improve outputs.

## Bundled Files

The skill ships these files; load them on demand, not always-on:

**Persona references** (`references/`): the full archetypes used in the experiments.

- `references/knuth.md`
- `references/hickey.md`
- `references/torvalds.md`
- `references/dijkstra.md`
- `references/liskov.md`
- `references/pike.md`

**Workflow references** (`references/`): the steps of a review.

- `references/triage.md` - pick the crew before any pass runs
- `references/implementation-discipline.md` - scope, assumptions, and verification loop for code-changing follow-ups
- `references/verify.md` - diff-grounded gate; **mandatory** between blind passes and synthesis
- `references/synthesis.md` - final review writeup with severity ranking
- `references/artifact-format.md` - `runs/YYYY-MM-DD-topic_host/` layout if persistence is requested

**Examples** (`examples/`): optional calibration material.

- `examples/review-examples.md` — good/bad examples for crew runs, findings, verifier output, and implementation follow-up

For a default K+H+T run, load `triage.md` briefly, the three persona references, `verify.md`, and `synthesis.md`. Keep the remaining files out of context unless the request needs them.

## Hard Gates

These are not stylistic guidance — they are conditions for calling the output a Code Crew review.

1. **No "crew run" label without independent passes.** If the host cannot dispatch subagents in parallel or otherwise isolate per-persona contexts, the output is a "single-context approximation" — say so. One agent writing "Knuth says..., Hickey says..., Torvalds says..." in one transcript is consensus-by-author, not a crew run.
2. **No finding without a citation.** Every Findings entry must include `file:line` and a quote (or visible diff line). Bare claims like "consider adding tests" are not findings.
3. **No finding without surviving `verify.md`.** Candidate findings from the persona passes do not appear in the final review unless they pass the verifier. Default to reject when uncertain.
4. **No dissent preservation by default.** Our experiments tested preserved-dissent synthesis against consensus-collapse synthesis. Preserved dissent did **not** improve recall (Δ=+0.012, p=0.41) and **increased fabrication rate** (0.74 vs 0.63). Show disagreement only when the lenses disagree on the *decision* (land vs block), not on severity-by-one-step.
5. **No verification claim without action.** If you did not run the test, type-check, or build, the Verification block must say "Not run" with a reason. Do not claim "tests pass" you didn't run.
6. **No recommendation in conflict with findings.** Listing 2 Critical findings precludes a LAND recommendation. Reconcile before emitting.
7. **No silent personas.** If a single lens carries the entire review (all findings from one persona, others empty), say so explicitly in the output — that is a data point about the diff, not a hiding-the-disagreement moment.
8. **Use the highest reasoning budget the active host and model expose.** Inspect the current dispatch tool or host settings instead of assuming a fixed token such as `xhigh`, `max`, or `ultra`; supported levels change by model and release. If the host exposes no control, proceed at the default and note "ran at host-default reasoning budget" in the Verification block. The original experiment artifacts did not record an exact reasoning-effort setting, so report the runtime setting as execution metadata, not as an experimentally validated requirement.
9. **No implementation scope creep.** When the user asks Code Crew to change code, load `references/implementation-discipline.md` before editing. The implementation must state assumptions, keep the diff tied to the request, and verify with concrete checks.

## Single-Lens Shortcuts

When the user explicitly asks for one persona:

- "Knuth only" → algorithm/performance review
- "Hickey only" → simplify a design / expose incidental complexity
- "Torvalds only" → patch acceptance review
- "Dijkstra only" → formal correctness / structured-programming critique
- "Liskov only" → abstraction, substitution, contract review
- "Pike only" → Unix-style decomposition, data-structures-first critique

Solo passes still run the verifier. Label single-lens output clearly; do not present it as a crew synthesis.

## Output Format

The final review emitted by `references/synthesis.md`:

```text
## Findings
- [Critical] file:line — Finding. Evidence: <quoted line or citation>. Lens: Knuth/Hickey/Torvalds.
- [High] file:line — ...

## Disagreement
Material disagreement only. Omit when the lenses agree.

## Recommendation
LAND / LAND WITH FIXES / REQUEST CHANGES / REDESIGN / NEEDS MORE EVIDENCE

## Verification
What was actually checked. "Not run" with reason if nothing ran.
```

## Safety And Scope

This skill does not authorize destructive operations, commits, pushes, deploys, external comments, or package publication. Ask for explicit user approval before any irreversible or external action.

This skill contains no executable payload, dependencies, hooks, or network integrations. The host may still read files, run tests, or edit code when the user asks; its normal permissions and approval boundaries continue to apply.

## Scope And Evidence Boundary

Empirically tested scope: PR / diff review. The K+H+T result and the 64%-fabrication number both come from SWE-PRBench experiments at n=50 PRs with paired sign tests, all on PR-review tasks. The reported recall numbers are raw recall; the pre-registered fixed-precision metric was not computable because all arms scored far below the 0.70 precision threshold under the skeptic judge. K+H+T is the best tested default we have for PR review, not a proven global optimum (10 of 20 possible triples were tested).

Broader uses (design critique, file review, refactoring judgment) are supported by the persona briefs and run in source-mode of the verifier, but **the empirical claims do not transfer**. We have no measurement of K+H+T vs other crews on design critique or file review, and the source-mode verifier is a logical adaptation of the diff-mode rubric, not an independently tested procedure.

The verifier procedure is recommended on the basis of the same experiments showing a 64% fabrication rate without it; the empirical effect of adding this verifier on that rate has not yet been independently measured in this repo.
