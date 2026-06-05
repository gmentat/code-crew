# Code Crew Plugin

Code Crew packages the famous-programmer review crew as a portable agent skill/plugin.

Default preset:

- Knuth: rigor, algorithms, invariants, complexity.
- Hickey: simplicity, data, value/identity/time, incidental complexity.
- Torvalds: maintainer-grade patch acceptance and practical systems review.

The package is prompt-only. It adds no tools, MCP servers, network calls, hooks, or executable code.

The package includes the full core persona briefs under `skills/code-crew/briefs/`. Those files are byte-identical to the persona prompts used by the experiment harness.

It also includes on-demand procedure and example files. These improve invocation and implementation discipline without changing the tested persona briefs.

## Install

### Codex

Codex installs Code Crew from a marketplace. The full source repo includes a root marketplace at `.agents/plugins/marketplace.json` that points to `./plugins/code-crew`.

From GitHub:

```bash
codex plugin marketplace add gmentat/code-crew
codex plugin add code-crew@code-crew
```

From a full local clone, run from the repository root:

```bash
codex plugin marketplace add .
codex plugin add code-crew@code-crew
```

If you downloaded only the `plugins/code-crew/` package directory, use the GitHub marketplace install above or place the package under a Codex marketplace that points to it. The package directory itself is a plugin root, not a Codex marketplace root.

Package-root local install was intentionally not documented because `codex plugin marketplace add .` must point at a marketplace, not a bare plugin root.

Codex installs the plugin root, including `.codex-plugin/plugin.json`, `skills/code-crew/SKILL.md`, and the bundled `skills/code-crew/briefs/` files.

### Claude Code

This plugin also includes `.claude-plugin/plugin.json`.

From GitHub:

```bash
claude plugin marketplace add gmentat/code-crew --sparse .claude-plugin plugins
claude plugin install code-crew
```

For local testing from a full source clone, run from the repository root:

```bash
claude --plugin-dir ./plugins/code-crew
```

From a downloaded `plugins/code-crew/` package, run from the package root:

```bash
claude --plugin-dir .
```

### Hermes

Hermes uses `SKILL.md` skill folders. Install the published skill:

```bash
hermes skills install https://raw.githubusercontent.com/gmentat/code-crew/main/plugins/code-crew/skills/code-crew/SKILL.md \
  --category software-development \
  --name code-crew \
  --yes
```

For local development from the package root, copy or symlink the skill folder:

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$PWD/skills/code-crew" ~/.hermes/skills/software-development/code-crew
hermes skills list | grep code-crew
```

### OpenClaw-Compatible Runtimes

The plugin root includes `openclaw.plugin.json`, but this repo does not yet publish a tested OpenClaw CLI install command. Use `plugins/code-crew/` as the plugin root in runtimes that support OpenClaw-style plugin manifests, or `skills/code-crew/` as the skill root in AgentSkills-compatible runtimes.

### Cursor

The full source repo includes a Cursor project rule at `.cursor/rules/code-crew.mdc`. If you downloaded only `plugins/code-crew/`, use the package-local template at `cursor/code-crew.mdc` and copy it into your target project's `.cursor/rules/` directory. The rule is not always-on; invoke it explicitly for Code Crew review or architecture critique. See package-local `CURSOR.md`.

## Usage

Code Crew installs as a skill. It does not add a daemon, background hook, MCP server, or custom slash command.

In Codex, either choose it from `/skills` or invoke it directly:

```text
$code-crew review the current diff
```

You can also ask your agent:

```text
Use Code Crew to review the current diff.
```

Or request a specific lens:

```text
Use Code Crew, Torvalds only, to decide whether this patch should land.
```

The skill can be routed automatically when the host agent recognizes a matching review or architecture prompt, but explicit invocation is the reliable path. Code Crew does not currently provide a `/code-crew` command.

For code-changing follow-up work, the skill loads `procedures/implementation-discipline.md`: state assumptions, keep the change surgical, and verify with concrete checks before claiming success.

## How To Know It Worked

Code Crew is working as intended when:

- independent persona passes happened, or the host clearly labeled the result as a single-context approximation
- final findings cite concrete `file:line` evidence or quoted source spans
- the verifier rejected unsupported claims before synthesis
- the recommendation follows from the surviving findings
- the Verification block says exactly what was run, or explicitly says what was not run

## Evidence Boundary

The benchmark result supports the default K+H+T preset as the best tested composition in this repo's PR-review experiments. It does not prove that famous names alone improve recall. The naming is retained because it makes the lenses memorable and easier to discuss.

## Contributor Note

Keep the duplicated distribution surfaces synchronized when changing usage, install, or metadata:

- root `README.md`
- `INSTALL.md`
- `CURSOR.md`
- `.cursor/rules/code-crew.mdc`
- `plugins/code-crew/CURSOR.md`
- `plugins/code-crew/cursor/code-crew.mdc`
- `plugins/code-crew/README.md`
- `plugins/code-crew/.claude-plugin/plugin.json`
- `plugins/code-crew/.codex-plugin/plugin.json`
- top-level marketplace manifests
- `plugins/code-crew/skills/code-crew/SKILL.md`
