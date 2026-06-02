# Code Crew — project conventions for Claude Code

This repo is a code-review crew + the empirically tested plugin that packages it. Claude Code working in this repo should read this file and follow the conventions below. The same rules in fuller form live in [`AGENTS.md`](AGENTS.md) (for Codex); load that file when you need the full Foreman protocol.

## What this repo is

- **`plugins/code-crew/`** — the distributable plugin (Claude Code, Codex, Hermes, OpenClaw-compatible). The canonical install target. Validates with `claude plugin validate --strict ./plugins/code-crew`.
- **`agents/`** — the source persona briefs and ops-agent definitions. The plugin's `briefs/` directory is byte-identical to the 6 core persona files here.
- **`experiments/`** — DA-PRB and persona/triple ablations on `foundry-ai/swe-prbench`. Each run has a `SUMMARY.md` and an `ANALYSIS.json`. Raw per-PR outputs are committed for auditability but are large.
- **`runs/`** — local formal run history. **Gitignored.** Only commit a specific run with `git add -f` after explicit user approval.

## Default crew

When asked for "a review", use **Knuth + Hickey + Torvalds**. This is the empirically best-tested 3-persona crew in our SWE-PRBench experiments: n=50, +6.4pp recall over the full 6-sextet (p=0.047), and the highest recall *and* precision of the 10 triples that were tested. Fabrication rate is second-lowest at 0.645 (L+P+T edges it at 0.640, a 0.005 gap on n≈41). Do **not** auto-escalate to the full 6-crew "to be thorough" — adding personas to K+H+T measurably degrades the synthesis. See `experiments/2026-06-01-dissent-ablation/runs/personas/SUMMARY.md` and `experiments/2026-06-01-dissent-ablation/runs/triples/SUMMARY.md`.

For single-lens shortcuts and the full triage logic, load `plugins/code-crew/skills/code-crew/procedures/triage.md`.

## Crew dispatch rules

1. **Independent blind passes.** Each persona runs in its own subagent context. One agent writing "Knuth says... Hickey says..." in a single transcript is consensus-by-author, not a crew run.
2. **Highest reasoning budget available.** For every dispatched persona, verifier, or ops role: use the maximum the host exposes. In Claude Code via the Agent tool, that means asking for `model: opus` or the highest-tier model the workspace allows. In Codex, pass `reasoning_effort: xhigh` on every `spawn_agent` call. If you cannot raise the budget, label the output "ran at host-default budget" — do not pretend it's a formal crew run.
3. **Mandatory verifier between passes and synthesis.** The verifier (`plugins/code-crew/skills/code-crew/procedures/verify.md`) drops candidate findings that aren't anchored to a specific diff line or quoted span. Our experiments measured ~64% of K+H+T synthesis findings as FABRICATED by the judge without it.
4. **Synthesis is consensus-by-default.** Preserve dissent only when lenses disagree on the *decision* (land vs block), not on severity-by-one-step. Preserved-dissent synthesis was tested and did not improve recall (Δ=+0.012, p=0.41) while increasing fabrication (0.74 vs 0.63).

## Plugin-quality rules

When editing the plugin (`plugins/code-crew/`):

- Run `claude plugin validate --strict ./plugins/code-crew` and `claude plugin validate --strict .` before committing.
- Run the Codex validator too: `uvx --with pyyaml python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py ./plugins/code-crew`.
- End-to-end install/uninstall the plugin (`claude plugin marketplace add ./ --scope project` → `install` → `details` → `uninstall` → `marketplace remove`) before claiming the plugin works.
- For changes to procedure files or hard gates, smoke-test the actual skill invocation: `claude --plugin-dir ./plugins/code-crew -p "Use code-crew to review the following diff..."` with a known-buggy diff.

## Experiments rules

- Each run has a frozen `PROTOCOL*.md` pre-registration. Any deviation is recorded in `DEVIATIONS.md` with a date.
- Empirical claims must cite the specific run (`runs/main/`, `runs/personas/`, `runs/triples/`). Soften language to "best tested default" rather than "empirical optimum" until exhaustive coverage exists.
- `data/*_prompts.json` is regenerable from `scripts/prepare_*_prompts.py` and is gitignored.

## What not to do

- Do not reference private internal projects, sibling repositories, or unpublished context. This is a public-facing codebase.
- Do not commit experimental run outputs to `runs/` at the repo root — that directory is gitignored and is for local history.
- Do not pad reviews with low-severity nits. Move them to a Notes block per `procedures/synthesis.md`.
- Do not claim verification (tests, types, builds) you did not run. The Verification block must say "Not run" with a reason when nothing was executed.

## When in doubt

Load `AGENTS.md` for the full protocol. The plugin's `SKILL.md` and `procedures/*.md` are the canonical operational rules for an actual review — they're shorter than `AGENTS.md` and explicitly designed for an LLM mid-task.
