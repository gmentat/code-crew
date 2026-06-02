# Verify Candidate Findings

Run this gate between the K+H+T blind passes and synthesis. Prior runs on SWE-PRBench showed high judged fabrication rates in K+H+T synthesis output (~64% of final flagged issues labelled FABRICATED by the judge); this verifier is a proposed precision gate designed to attack that, but its own empirical effect on the fabrication rate has not yet been independently measured on this substrate. Default to reject when uncertain; recall is cheaper to recover in synthesis than precision is.

## Mode selection

The verifier runs in one of two modes depending on what the review is about:

- **diff-mode** (default for "review this PR / diff / patch"): each finding must be anchored to a specific `+`/`-` line in the unified diff. The six-question rubric below applies as written.
- **source-mode** (for "review this file / design / architecture"): there is no diff. Each finding must instead be anchored to a specific quoted span in the reviewed source file(s), design document, or architecture brief. Apply the rubric with Q4 ("Diff-caused?") relaxed to "Tied to a specific quoted span in the reviewed material?", and reject anything that depends on code not under review.

If the input is ambiguous, ask which mode applies before running the verifier. Do not silently run diff-mode on a non-diff review — that will reject everything.

## I/O contract (diff-mode)

**Input:**
- `candidates`: 5-7 findings from K+H+T passes, each `{id, persona, file, line_hint, claim, severity}`.
- `diff`: the unified diff under review, already in context.

**Output:** one verdict line per candidate, in input order, nothing else:

```
K1  KEEP      path/file.py:42   <one-sentence reason citing the line>
H2  REJECT    path/file.py:?    fails Q2 (symbol not in diff)
T3  HEDGE     src/api.ts:103    mechanism present, trigger depends on callers
```

Synthesis consumes this directly. Do not add new findings here — verifier only filters.

## Procedure

For each candidate, in order:

1. **Locate.** Find the cited `file:line` in the diff. If the file is not in the diff, or the line is unchanged context (not `+`/`-`), reject.
2. **Quote.** Copy the 1-5 diff lines the claim depends on into a scratch buffer. No quote, no finding.
3. **Restate.** Rewrite the claim as a falsifiable statement about the quoted lines: "Line N does X, which causes Y."
4. **Rubric.** Answer six questions as hard YES/NO against the quoted lines. Any NO rejects:
   1. **Locatable?** Cites a specific `path:line` present in the diff.
   2. **Present?** Cited symbol/construct visible in the quoted lines — not inferred from surrounding files.
   3. **Concrete?** Describes what the code *does*, not what it *might/could/may* do.
   4. **Diff-caused?** Introduced or meaningfully changed by THIS diff (not pre-existing, untouched).
   5. **Falsifiable?** Confirmable from the quoted lines plus named in-repo context (no "depends on caller").
   6. **Non-duplicative?** Materially distinct from already-kept findings.
5. **Hedge exception.** If Q1-Q4 pass but Q5 fails only because the *trigger* lives off-diff while the *mechanism* is present in the quoted lines, emit `HEDGE` with the conditional ("if any caller passes POST..."). Do not assert the consequence as fact.
6. **Severity sanity.** If kept at `high`/`critical` but the quoted mechanism only supports `low`/`info`, downgrade in the reason.
7. **Emit** one verdict line. `reason` ≤ 140 chars. KEPT/HEDGE: present tense, no further hedging beyond step 5. REJECT: cite the failing question number plus 3-8 word explanation; do not argue the merits.

## Worked example

**Candidate T3 (from Torvalds):** "`load_config` silently swallows `yaml.YAMLError`, hiding malformed configs."

**Diff:**
```python
+def load_config(path):
+    with open(path) as f:
+        return yaml.safe_load(f)
```

No `try`, no `except` in the added lines. Claim describes an error handler that does not exist — fabricated from a common pattern.

```
T3  REJECT    src/config.py:12   fails Q2 (no except block in diff)
```

## Source-mode adaptation

When the review target is a file, module, or design doc rather than a diff:

- The **anchor** is a quoted span from the reviewed material (function definition, class, paragraph), not a `+`/`-` line.
- **Q4** becomes: "Is this finding about a specific quoted span in the reviewed material, not about hypothetical code or off-scope concerns?"
- **Q5** still applies: the finding must be confirmable from the quoted span plus named in-repo context. If it depends on callers outside the reviewed scope, HEDGE.
- Otherwise the rubric and verdict format are unchanged.

Use the same `KEEP / HEDGE / REJECT` verdict block. Cite span identifiers (`auth.py:AuthMiddleware.validate` or `design.md:§3.2`) in place of `path:line`.

## Hard rules

- Anchor-only gate (diff-mode: diff lines; source-mode: quoted spans). No code execution, URL fetches, or MCP calls.
- Do not invent line numbers or fabricate quoted spans to rescue a finding. If Q1 fails, reject.
- Do not re-read the candidate's prose to steelman it. Check it against the anchor, verbatim.
- Split multi-site findings before verifying; verify each site independently.
- Typical outcome: 1-3 KEPT out of 5-7. Keeping 5+ means you are being too lenient — re-run the rubric.
