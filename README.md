# Code Crew

A downloadable famous-programmer code review crew for Codex, Claude Code, Hermes, and AgentSkills-compatible agents.

Code Crew packages named software-engineering reasoning lenses for working through code quality, system design, and code improvement. Foreman dispatches the right persona specs as independent subagents, each follows its process, and Foreman synthesizes the returned reports.

This is a **review-and-improvement shop for software**. The crew is designed to attack a piece of code or a system from multiple angles, with built-in disagreement so you don't get a comfortable consensus that misses what's wrong.

## Install

The canonical distributable package is [`plugins/code-crew/`](plugins/code-crew/). It is prompt-only: no binaries, hooks, MCP servers, background processes, or network calls.

Codex:

```bash
codex plugin marketplace add gmentat/code-crew
codex plugin add code-crew@code-crew
```

Codex installs [`plugins/code-crew/`](plugins/code-crew/): a `.codex-plugin/plugin.json` manifest, the `code-crew` skill, and the full core persona briefs bundled under `skills/code-crew/briefs/`.

Claude Code:

```bash
claude plugin marketplace add gmentat/code-crew --sparse .claude-plugin plugins
claude plugin install code-crew
```

Hermes:

```bash
hermes skills install https://raw.githubusercontent.com/gmentat/code-crew/main/plugins/code-crew/skills/code-crew/SKILL.md \
  --category software-development \
  --name code-crew \
  --yes
```

OpenClaw-compatible runtimes: the package includes [`plugins/code-crew/openclaw.plugin.json`](plugins/code-crew/openclaw.plugin.json), but this repository does not yet publish a locally verified OpenClaw CLI install command.

For local development and fallback manual installs, see [`INSTALL.md`](INSTALL.md).

## After install

Installing Code Crew makes the `code-crew` skill available to the host agent. It does **not** install a daemon, background reviewer, git hook, MCP server, or custom slash command.

In Codex, use it in one of three ways:

- Type `/skills`, choose `code-crew`, then write the review request.
- Invoke it explicitly in the prompt: `$code-crew review the current diff`.
- Ask naturally: `Use Code Crew to review this PR with the default Knuth + Hickey + Torvalds crew`.

Codex may route clearly matching review or architecture prompts to the skill based on its `SKILL.md` name and description, but users should not rely on it running automatically for every coding task. The predictable path is explicit invocation.

Code Crew does not currently provide `/code-crew` commands. If command support becomes useful, it should be a thin convenience layer over the same skill, not a separate behavior path.

## What's measured

Headlines from [`experiments/`](experiments/) (read each run's `SUMMARY.md` for full details):

- **Multi-perspective beats naive single Claude** on PR review recall (+7pp, paired n=50, p=0.004).
- **Three personas beat six.** The K+H+T triple (Knuth + Hickey + Torvalds) beats the full sextuplet by +6.4pp recall at n=50 (p=0.047) with better precision and lower fabrication. **The default recommended crew is 3, not 6.**
- **Named archetypes don't improve recall over generic numbered reviewers** (Δ ≈ 0, p=0.50). What they do is produce ~18% more semantic divergence between passes, which surfaces as auditable disagreement. Names are for interpretability, not output quality.
- **Preserved-dissent synthesis ≠ better outputs.** Dissent visibility is a UX product (reviewer can see who said what); it doesn't improve recall over consensus synthesis.
- **K+H+T is the best tested default, not a magic formula.** A follow-up triple search tested 10 of 20 possible 3-persona combinations and found no challenger with a better point estimate, but several challengers are statistical ties and the untested 10 remain open.

The repo includes the runnable harness so anyone can re-test these claims (or refute them) on `foundry-ai/swe-prbench` from inside Claude Code.

## Why Knuth + Hickey + Torvalds?

The default is **K+H+T Classic**: Knuth for rigor, Hickey for simplicity/data/time, and Torvalds for maintainer reality. The names are not magic. They are memorable review contracts for three complementary engineering lenses.

Synthetic roles may become useful specialized presets, but they need to beat this default in the harness before replacing it. For v0, K+H+T is the public default because it is the best-tested composition and the easiest version to explain.

It is especially useful when:

- you want a code review that surfaces what each tradition would actually say
- you are designing a system and want competing architectural lenses, not the consensus pattern
- you suspect your code has a problem but the team has talked themselves into liking it
- you are choosing between paradigms (OO vs. data-oriented, types vs. dynamism, TDD vs. design-first) and want each tradition's strongest case
- you want disagreement on purpose — engineers who would actually argue with each other

## What the crew is

Each persona is a **reasoning archetype** inspired by the public work, papers, code, talks, and operating style of a real software engineer or computer scientist. None of them claim to speak for the actual person, invent quotations from them, endorse anything in their name, or impersonate them. Several are still living and active; the system uses these archetypes as decision contracts, not identity simulations.

## Invocation model

Multi-lens runs are orchestrated by Foreman. Each selected lens is launched as its own subagent or independent execution context, preferably in parallel when the lenses do not depend on each other. The subagents return blind-pass reports; Foreman alone synthesizes the reports and speaks for the crew as a whole.

A single assistant response that roleplays several people in sequence is not a crew run. Single-lens advisory use is allowed, but it should be labeled as one lens rather than a multi-agent review.

## Roster

The crew is in [AGENTS.md](AGENTS.md). Specs are in `agents/` and `agents/council/`.

**Default crew of 3** (validated by the persona ablation; this is the recommended starting point):

- [Knuth](agents/knuth_agent.md) — algorithmic rigor, literate programming, "premature optimization is the root of all evil"
- [Hickey](agents/hickey_agent.md) — simple-not-easy, data-oriented, value-and-time reasoning
- [Torvalds](agents/torvalds_agent.md) — pragmatic systems engineering, brutal code review, ship working code

**Extended roster** (use for specific angles or one-at-a-time as single-lens calls; adding them to the default 3 measurably degrades synthesis quality):

- [Dijkstra](agents/dijkstra_agent.md) — formal correctness, structured programming, brutal critique of sloppy thinking
- [Liskov](agents/liskov_agent.md) — abstraction, substitution, type discipline, system architecture
- [Pike](agents/pike_agent.md) — Unix philosophy, "data structures, not classes," small composable tools

**Operations 7** (synthetic 2026 specialist roles for autonomous code work):

- [Foreman](agents/operations/foreman_agent.md) — code-review orchestrator; picks the lenses, runs blind passes, synthesizes, gates action
- [Surveyor](agents/operations/surveyor_agent.md) — codebase cartographer; git archaeology, blast-radius mapping, prior art
- [Forge](agents/operations/forge_agent.md) — AI coding-agent coordinator (Claude Code / Cursor / Aider / autonomous); the only ops role that writes code directly
- [Sentry](agents/operations/sentry_agent.md) — security, secrets, license, supply chain, AI provenance; gates external action
- [Telemeter](agents/operations/telemeter_agent.md) — observability, SLOs, error budgets; reads production back into review
- [Ledger](agents/operations/ledger_agent.md) — engineering economics, tech-debt accounting, cost-of-feature
- [Scribe](agents/operations/scribe_agent.md) — theory transmission, ADRs, onboarding memory; the operational arm of Naur

**Council 6** (extended specialist lenses):

- [Brooks](agents/council/brooks_agent.md) — software project management, conceptual integrity, "no silver bullet"
- [Lamport](agents/council/lamport_agent.md) — distributed systems, formal verification, TLA+
- [Hoare](agents/council/hoare_agent.md) — concurrent computing, the "billion-dollar mistake" (null), correctness contracts
- [Beck](agents/council/beck_agent.md) — TDD, XP, "make the change easy, then make the easy change"
- [Naur](agents/council/naur_agent.md) — programming as theory building, mental models over text
- [Armstrong](agents/council/armstrong_agent.md) — Erlang, "let it crash," fault tolerance

## How to use

Use Foreman as the dispatcher:

- "Foreman: dispatch Dijkstra as a single-lens subagent on this diff."
- "Foreman: dispatch Hickey as a single-lens subagent to find the simple version."
- "Foreman: dispatch Torvalds as a single-lens subagent to decide whether this patch is acceptable."
- "Foreman: dispatch Liskov as a single-lens subagent to audit the abstraction."
- "Foreman: dispatch Knuth and Torvalds as independent blind-pass subagents, then synthesize the disagreement."
- "Foreman: dispatch Beck and Hickey as independent blind-pass subagents; Beck covers the smallest test, Hickey checks whether the design should exist in that shape."

Useful pairings:

> **Knuth + Torvalds**: rigor vs. shipping. They will disagree by design.
>
> **Hickey + Beck**: data-first vs. test-first. Hickey explicitly criticized TDD; Beck invented it.
>
> **Liskov + Hickey**: abstraction/types vs. data-oriented composition.
>
> **Dijkstra + anyone-pragmatic**: he was famously dismissive of working systems; useful as the rigor floor that nothing reaches.
>
> **Pike + Kay/OOP-heavy thinkers** (Kay not in roster but represented through Liskov's abstraction lens): "data structures, not classes" against the OO mainstream.
>
> **Lamport + Torvalds**: prove correctness vs. test-and-ship.
>
> **Naur alone**: when the team has the code right but doesn't share the *theory* of why, Naur is the only voice that captures what's missing.

For a full code-review run, the operating rhythm is: Foreman dispatches each lens as an independent blind-pass subagent, candidates are merged, claims are checked, and the recommendation is recorded.

## Files

- [AGENTS.md](AGENTS.md) — crew manifest and roster
- [project_workflow.md](project_workflow.md) — autonomous code-improvement loop (how ops + archetypes interact on real work)
- [code_review_methods.md](code_review_methods.md) — concrete review and improvement methods the crew uses
- [crew_disagreements.md](crew_disagreements.md) — built-in disagreement map (the seams the system is designed around)
- [safety_floor.md](safety_floor.md) — autonomy boundaries, AI provenance, refusal rules (binding)
- [INSTALL.md](INSTALL.md) — install paths for Codex, Claude Code, Hermes, and AgentSkills-compatible agents
- [plugins/code-crew/](plugins/code-crew/) — distributable plugin/skill package
- `agents/` — core persona files (historical archetypes)
- `agents/operations/` — synthetic ops-agent files (Foreman, Surveyor, Forge, Sentry, Telemeter, Ledger, Scribe)
- `agents/council/` — extended council persona files
- `runs/` — local formal run history, ignored by default unless a run is intentionally published with `git add -f`
