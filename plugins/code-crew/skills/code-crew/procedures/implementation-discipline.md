# Implementation Discipline

Loaded when the user asks Code Crew to change code, not just review it. This procedure applies to Forge-led implementation, refactoring, bug fixing, and any follow-up patch after a crew review.

This file is intentionally separate from the persona briefs. Do not paste these rules into Knuth, Hickey, Torvalds, or any other brief; the persona prompts are already saturated by experiment.

## Goal

Turn a vague coding request into a small, reversible, verified change.

## Before editing

1. **Name the goal.** One sentence: what should be true when the work is done?
2. **State assumptions that affect the design.** If ambiguity changes public behavior, data exposure, compatibility, or security, ask before editing.
3. **Define success criteria.** Prefer concrete checks: failing test made passing, validator output, typecheck, build, CLI command, or exact doc diff.
4. **Pick the smallest useful scope.** No speculative APIs, no future-proofing knobs, no extra workflows unless the user asked.
5. **Identify files you expect to touch.** If the touched set expands, re-check scope before continuing.

## While editing

- Make surgical changes tied to the request.
- Match local style even when another style is personally preferable.
- Do not refactor adjacent code just because you noticed it.
- Remove only unused imports, variables, or files made unused by this change.
- If unrelated dead code or cleanup is visible, mention it in the final notes; do not delete it unless asked.
- Keep new abstractions out until there are at least two real call sites or a clear existing local pattern.
- Prefer source-of-truth docs over duplicated prose when updating install or usage instructions.

## Verification loop

Run the narrowest meaningful check first, then broaden only when the touched surface warrants it.

Examples:

| Change shape | Minimum check |
|---|---|
| Plugin manifest or skill metadata | manifest JSON parse + host plugin validator |
| Skill/procedure markdown | YAML frontmatter parse where applicable + spelling of referenced files |
| Review verifier or synthesis rule | smoke test on a known-buggy diff |
| Experiment script behavior | rerun the relevant analysis command and compare headline numbers |
| Code change | reproduce failing case, make it pass, then run nearby tests |

If a check cannot be run, say exactly why in `Verification`. Never imply tests passed from inspection alone.

## Output for implementation work

```text
## Goal
<one sentence>

## Scope
Files changed and why.

## Verification
Commands actually run, with pass/fail. Include "Not run" reasons.

## Remaining Risk
Only material risks that survive verification.
```

## Hard gates

- No silent interpretation of an ambiguous request when the interpretation affects behavior or safety.
- No drive-by refactors.
- No invented verification.
- No external or irreversible action without explicit approval.
- No formal "crew implementation" label unless Foreman dispatched independent roles for review/plan/verification.
