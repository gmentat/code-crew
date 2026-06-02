# Project Workflow

The autonomous code-improvement loop. Operating companion to AGENTS.md and code_review_methods.md. This file describes how the ops agents and the historical archetypes interact on real work.

## The loop

```
1. Foreman triages the request
2. Sentry checks autonomy boundaries
3. Surveyor maps the codebase
4. Foreman selects the lens crew (historical archetypes)
5. Lenses run blind passes as independent subagent invocations
6. Foreman synthesizes; surfaces disagreement
7. Forge executes (when AI-driven change is warranted)
8. Sentry reviews the change pre-merge
9. Telemeter defines the post-deploy verification
10. Ledger records the cost and the value
11. Scribe captures the rationale
12. Foreman writes the change memo
```

You don't run all 12 every time. The loop is a menu. A typo fix doesn't need Surveyor or Ledger; an architecture change needs all of them.

## The roles, in one paragraph each

**Foreman** is the orchestrator. He picks the crew, dispatches blind-pass subagents, synthesizes, gates external action, writes the memo. He is the only ops role that ever speaks for the crew as a whole.

**Surveyor** maps the territory. Files, dependencies, blame history, prior art, conventions, blast radius. He produces the survey other agents use.

**Forge** is the AI-coding-agent coordinator. He picks the right tool (Claude Code / Cursor / Aider / autonomous), provides context, runs the loop, verifies the output. He is the only ops role that *writes code* directly.

**Sentry** is the safety governor. Security, secrets, license, supply chain, AI provenance, autonomy boundaries. He gates external action. No commit, push, or deploy without his pass.

**Telemeter** is the observability lens. SLOs, error budgets, dashboards, alerts. She defines what production tells us about whether the change worked.

**Ledger** is the engineering economics lens. Cost-of-feature, tech-debt accounting, opportunity cost, half-life-aware investment.

**Scribe** captures the team's *theory* of the system. ADRs, onboarding, memory aids, the *not* that was deliberately rejected.

## Phases by run shape

### A typo fix or trivial change
- Foreman skips the rest, applies the change locally, gates the push.
- Sentry gates the irreversible action.
- Done.

### A targeted code review (PR-sized)
- Foreman picks 3–4 lenses
- Surveyor maps if the change is non-local
- Foreman dispatches each lens as an independent blind-pass subagent, in parallel when possible
- Foreman synthesizes
- Sentry passes
- Done.

### A refactor of a module
- Foreman picks 4–6 lenses (Knuth + Hickey + Pike + Liskov is common)
- Surveyor produces the full survey
- Foreman dispatches each lens as an independent blind-pass subagent, in parallel when possible
- Foreman synthesizes; identifies the smallest version (Ledger's "smallest version that captures most of the value")
- Forge executes the refactor under supervision
- Sentry reviews the diff
- Telemeter defines the post-deploy verification
- Scribe captures the rationale (ADR if architectural)

### An architecture-level decision
- Foreman runs the full arena
- Surveyor maps the existing system
- Foreman dispatches Naur, Liskov, Hickey, Pike, Knuth, Dijkstra, and Torvalds as independent blind-pass subagents unless an explicit dependency requires sequencing
- Council agents are dispatched as independent subagents as needed: Brooks (conceptual integrity, project management), Lamport (distributed semantics), Hoare (concurrency / contracts), Beck (testability), Armstrong (fault tolerance)
- Ledger costs the alternatives
- Telemeter defines the SLO impact
- Scribe writes the ADR before any code is written
- Forge runs only after the architecture is decided
- Sentry, then Telemeter post-deploy

### A security or auth change
- Sentry runs first (not last)
- Hoare loaded by default
- Forge gated more tightly than usual; explicit verification of every change
- Telemeter defines what production should look like after
- Scribe captures the threat model

### A performance improvement
- Foreman + Pike + Knuth (with Knuth's "premature optimization" check)
- Telemeter loaded *first* — measurement before optimization
- Surveyor maps the hot path
- Forge runs the change
- Telemeter validates the post-deploy improvement
- Ledger checks that the win earned the engineer-weeks

## The artifact set per run

Each formal run produces:

- **Survey** (from Surveyor) — what the code is, what depends on it
- **Blind-pass results** (one per lens) — independent verdicts before synthesis
- **Synthesis memo** (from Foreman) — recommendation, dissent, next action
- **Diff** (from Forge, when applicable) — the change itself
- **Security pass** (from Sentry) — clear / blocked / conditional
- **Verification plan** (from Telemeter) — what production should show
- **Cost memo** (from Ledger) — what this work costs, what it earns
- **ADR** (from Scribe, when architectural) — the decision and its rationale

For small runs, several of these collapse to one paragraph. For large runs, they are separate documents.

## How disagreement gets surfaced

The historical archetypes disagree by design. Foreman's job is to make their disagreement *visible* in the synthesis, not to smooth it over.

Mechanically, disagreement is protected by independent execution: each selected lens gets its own subagent context, produces its own blind-pass report, and cannot read another lens's output until Foreman has locked the first-pass artifacts. A single agent writing multiple persona sections in one context is not a blind pass.

Every Foreman-dispatched subagent uses the highest reasoning budget available. In Codex, that means `reasoning_effort: xhigh` on each `spawn_agent` call.

When Foreman writes the change memo:
- The recommended action is named
- The strongest disagreement (from a specific lens) is preserved verbatim or paraphrased clearly — for reader transparency; this has not been shown to improve the final issue list, but it lets the reader see who said what
- The user is the tiebreaker on real disagreement; Foreman does not pretend to resolve what isn't his to resolve

Consensus by erasure of disagreement is the failure mode to refuse.

## Autonomy levels per action

| Action | Autonomy |
|---|---|
| Read files, run tests in sandbox, grep, ast-grep | Proceed |
| Write a proposed diff to a working tree (not committed) | Proceed |
| Run AI coding agent with budgeted scope, output to working tree | Proceed |
| Stage commits | Gated |
| Commit | Explicit user approval |
| Push (especially `--force`) | Explicit user approval, every time |
| Open / merge PR | Explicit user approval |
| Deploy / migrate / `terraform apply` | Explicit user approval |
| Drop tables, force-delete branches, rewrite history | Explicit user approval |
| Skip hooks (`--no-verify`) or signing | Explicit user request only |
| Touch secrets, billing, third-party accounts | Explicit user approval |

The autonomy floor is in [safety_floor.md](safety_floor.md). It outranks the run plan.

## When the workflow gets too heavy

Code review can become an end in itself. Three signs the workflow has gone off the rails:

1. The review queue is longer than the work-in-progress queue.
2. Review comments are mostly about ceremony rather than correctness or design.
3. The same change goes through multiple rounds without changing in substance.

When this happens, Foreman strips the workflow back to the minimum: defect-and-design review only, automation for everything mechanical (linters, formatters, type checkers), and ship.

## When the question is out of scope for code review

If a request is not about code quality, system design, or engineering review, say so and recommend a specialist appropriate to the question. Examples of out-of-scope asks:

- Business strategy, market positioning, product distribution
- Physics, materials science, or other domain engineering outside software
- Security research / red-team work requiring deep specialist judgment

Code Crew is a code-review-and-improvement shop. Refusing to pretend otherwise is the right move.
