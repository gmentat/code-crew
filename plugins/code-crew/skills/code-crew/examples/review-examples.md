# Code Crew Examples

Loaded only when the user asks how Code Crew should behave or when a host needs examples for calibration. These examples are not part of the default persona prompts.

## Example 1: Proper crew run vs single-context roleplay

### Bad

```text
Knuth says the algorithm looks fine.
Hickey says the design is probably complected.
Torvalds says ship it.
```

Problems:

- One context wrote all voices.
- No blind passes.
- No file:line evidence.
- No verifier.
- No actionable recommendation.

### Good

```text
Foreman selected K+H+T for a PR-review scope.
Knuth, Hickey, and Torvalds each reviewed the diff in separate contexts.
The verifier rejected two uncited claims and kept one diff-grounded finding.

## Findings
- [High] src/cache.py:88 - The new cache key omits `tenant_id`, so data can be reused across tenants. Evidence: `key = f"{user_id}:{resource_id}"`. Lens: Torvalds/Hickey.

## Recommendation
REQUEST CHANGES

## Verification
Ran verifier against the unified diff. Tests not run; review-only pass.
```

## Example 2: Review finding vs vague advice

### Bad

```text
Add tests around this path and consider simplifying the abstraction.
```

Problems:

- No cited code.
- No falsifiable failure.
- Reads as generic advice, not a finding.

### Good

Fictional example:

```text
- [Medium] plugins/example-review/.claude-plugin/plugin.json:8 - The plugin manifest does not declare its skill path, so marketplace readers must infer where the skill lives. Evidence: manifest has `license` but no `skills` field. Lens: Torvalds.
```

The good version names a file, a specific missing contract, and the consequence.

## Example 3: Implementation after review

### Bad

```text
The review found a weak manifest, so I rewrote the plugin layout, renamed the skill, changed all install docs, and added a command system.
```

Problems:

- Scope expanded beyond the finding.
- Renaming risks breaking installs.
- Command support was not necessary to fix metadata.

### Good

```text
Goal: make the declared skill path explicit.
Scope: edit only `plugins/code-crew/.claude-plugin/plugin.json`.
Verification: parse JSON and run `claude plugin validate --strict plugins/code-crew`.
```

The good version fixes the issue with the smallest reversible change and a concrete check.

## Example 4: Verifier behavior

Candidate:

```text
T2 High - `load_config` swallows YAML parse errors.
```

Diff:

```diff
+def load_config(path):
+    with open(path) as f:
+        return yaml.safe_load(f)
```

Verifier output:

```text
T2  REJECT    src/config.py:?    fails Q2 (no exception handler in diff)
```

The verifier does not rescue plausible-sounding claims. If the mechanism is not visible in the reviewed lines, reject it.
