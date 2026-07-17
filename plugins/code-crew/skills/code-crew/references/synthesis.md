# Synthesis — decision-changing findings only

Loaded after `verify.md` has run and the surviving findings are in hand. Produces the final review the user sees.

## What synthesis does

Takes verified findings (each tagged with the lens that raised it), groups them, ranks by severity, and writes the final review.

## What synthesis does NOT do

- Does **not** preserve every minority concern. Our experiments tested a "preserved-dissent" synthesis vs a consensus-collapse synthesis on n=50 PRs; preserved dissent did not improve recall (Δ=+0.012, p=0.41) and **increased fabrication rate** (0.738 vs 0.631). One reviewer flagging something is not load-bearing.
- Does **not** include findings without file:line evidence. If `verify.md` couldn't ground it in the diff, it doesn't appear in the output.
- Does **not** invent severity. Use the severity each lens assigned; only escalate when 2+ lenses agree on the same issue at the same line.

## Procedure

1. **Cluster** findings by file:line. Multiple lenses flagging the same line → one merged finding.
2. **Score severity** per merged finding:
   - Critical: correctness, security, data loss, production-outage risk. Block merge.
   - High: subtle correctness or maintainability risk. Should block unless consciously accepted.
   - Medium: real defect or design risk, not necessarily blocking.
   - Low: clarity, style, or future-cleanup.
3. **Order** by (severity, then file order). Critical first.
4. **Identify dissent**. Material disagreement = one lens says "land," another says "block." Cosmetic disagreement (severity differs by one step) is not dissent.
5. **Write the recommendation**. One of: `LAND`, `LAND WITH FIXES`, `REQUEST CHANGES`, `REDESIGN`, `NEEDS MORE EVIDENCE`.

## Output format

```text
## Findings
- [Critical] file:line — One-sentence claim. Evidence: <quoted diff line or actual citation>. Lens: Knuth/Hickey/Torvalds.
- [High] file:line — ...
- [Medium] file:line — ...

## Disagreement
Material disagreement only. Omit this section entirely if all lenses agree or differences are not decision-changing.

## Recommendation
LAND / LAND WITH FIXES / REQUEST CHANGES / REDESIGN / NEEDS MORE EVIDENCE

## Verification
What was actually checked: commands run, tests, types, builds. If none were run, say "Not run" with the reason. Do not claim verification you did not perform.
```

## Hard gates

- **No claim without citation.** Every Finding line includes a file:line and an evidence quote (or a `cited as inferred from <X>` qualifier).
- **No verification claim without action.** If you didn't run the test/typecheck/build, the Verification block must say "Not run."
- **No recommendation in conflict with findings.** If you list 2 Critical findings, you cannot recommend LAND.
- **No "minor nit" findings in the Findings block.** Move Low-severity, non-decision-changing items into a final "Notes" block or drop them. Our experiments found exhaustive listing inflates fabrication without improving recall.

## When the verify step found nothing

Output exactly:

```text
## Findings
(none surviving verification)

## Recommendation
LAND (subject to host's own gating — Code Crew did not surface decision-changing issues at this scope)

## Verification
<commands run, or "Not run" + reason>
```

Do not pad. The honest empty result is the right output.
