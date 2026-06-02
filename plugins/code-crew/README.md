# Code Crew Plugin

Code Crew packages the famous-programmer review crew as a portable agent skill/plugin.

Default preset:

- Knuth: rigor, algorithms, invariants, complexity.
- Hickey: simplicity, data, value/identity/time, incidental complexity.
- Torvalds: maintainer-grade patch acceptance and practical systems review.

The package is prompt-only. It adds no tools, MCP servers, network calls, hooks, or executable code.

The package includes the full core persona briefs under `skills/code-crew/briefs/`. Those files are byte-identical to the persona prompts used by the experiment harness.

## Install

### Codex

This repo includes a Codex marketplace at `.agents/plugins/marketplace.json` that points to `./plugins/code-crew`.

From GitHub:

```bash
codex plugin marketplace add gmentat/code-crew
codex plugin add code-crew@code-crew
```

From a local clone:

```bash
codex plugin marketplace add .
codex plugin add code-crew@code-crew
```

Codex installs the plugin root, including `.codex-plugin/plugin.json`, `skills/code-crew/SKILL.md`, and the bundled `skills/code-crew/briefs/` files.

### Claude Code

This plugin also includes `.claude-plugin/plugin.json`.

From GitHub:

```bash
claude plugin marketplace add gmentat/code-crew --sparse .claude-plugin plugins
claude plugin install code-crew
```

For local testing from a clone:

```bash
claude --plugin-dir ./plugins/code-crew
```

### Hermes

Hermes uses `SKILL.md` skill folders. Install the published skill:

```bash
hermes skills install https://raw.githubusercontent.com/gmentat/code-crew/main/plugins/code-crew/skills/code-crew/SKILL.md \
  --category software-development \
  --name code-crew \
  --yes
```

For local development, copy or symlink the skill folder:

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$PWD/plugins/code-crew/skills/code-crew" ~/.hermes/skills/software-development/code-crew
hermes skills list | grep code-crew
```

### OpenClaw-Compatible Runtimes

The plugin root includes `openclaw.plugin.json`, but this repo does not yet publish a tested OpenClaw CLI install command. Use `plugins/code-crew/` as the plugin root in runtimes that support OpenClaw-style plugin manifests, or `skills/code-crew/` as the skill root in AgentSkills-compatible runtimes.

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

## Evidence Boundary

The benchmark result supports the default K+H+T preset as the best tested composition in this repo's PR-review experiments. It does not prove that famous names alone improve recall. The naming is retained because it makes the lenses memorable and easier to discuss.
