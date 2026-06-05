# Triage — picking the right crew size

Loaded when the host first invokes Code Crew on a review request. Decides which crew to dispatch before any persona pass runs.

## Decision rule

| Request shape | Crew | Why |
|---|---|---|
| "review this PR / diff" (default) | **K+H+T** | Empirically the best tested triple (n=50, +6.4pp raw recall vs the full sextet, p=0.047). Read `briefs/{knuth,hickey,torvalds}_agent.md`. |
| "should I land this patch" / "is this ready to merge" | **Torvalds solo** (or T+K if architecture is in scope) | Patch-acceptance is Torvalds's specific lens. |
| "is this algorithm correct" / "is the complexity claim right" | **Knuth solo** | Algorithmic rigor and invariant analysis. |
| "is this design overcomplicated" / "what's the simple version" | **Hickey solo** | Simple-not-easy, value/identity/time, incidental complexity. |
| "audit for correctness" / "what's structurally wrong" | **Dijkstra solo** | Formal-correctness style brutal critique. Best individual solo raw recall in our experiments (0.175). |
| "audit abstractions / contracts / subtypes" | **Liskov solo** | Substitution discipline, contract review. |
| "could this be smaller / more composable" | **Pike solo** | Unix-philosophy decomposition. |
| "exhaustive sextet" / "council review" / explicit user ask | **K+H+T+D+L+P** | Available; in our experiments it scored 0.151 vs K+H+T at 0.215, so use only when the user wants maximum interpretive diversity, not for better recall. |
| Cross-team or organizational tradeoff | escalate to council (`agents/council/`) — Brooks for conceptual integrity, Lamport for distributed, Hoare for concurrency, Beck for testability, Naur for theory, Armstrong for fault tolerance | Council briefs are in the parent repo, not bundled with this skill. |

## When in doubt

- Default to **K+H+T**. It is the documented recommendation and the empirically best-tested option.
- Do not auto-escalate to the sextet "just to be thorough." Adding personas to K+H+T measurably degrades the synthesis on our data.
- Do not invent personas not in `briefs/`. Single-lens shortcuts must use a brief we ship.

## Hard limits

- A formal "crew run" requires **independent passes**. If the host cannot dispatch subagents in parallel or otherwise isolate contexts, label the output as a "single-context approximation," not a crew run.
- If the user asks for a persona not in `briefs/` (e.g. Beck, Lamport, Naur), say so and offer either (a) using a related brief we do ship, or (b) producing the answer from your own knowledge with the lens clearly labelled as not a Code Crew formal pass.

## Output

Triage produces only a routing decision and a short justification. It does not produce findings. Once the crew is picked, proceed to the per-persona pass step in `SKILL.md`, then `procedures/verify.md`, then `procedures/synthesis.md`.
