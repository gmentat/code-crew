# Install Code Crew

Code Crew is distributed as a prompt-only plugin/skill pack. The canonical package lives at `plugins/code-crew/`.

Repository:

```bash
git clone https://github.com/gmentat/code-crew.git code_crew
cd code_crew
```

## Codex

Codex plugins use `.codex-plugin/plugin.json` plus `skills/<name>/SKILL.md`. This repo includes both and a local marketplace file.

Install from GitHub:

```bash
codex plugin marketplace add gmentat/code-crew
codex plugin add code-crew@code-crew
```

The marketplace command tells Codex where this repo's plugin source lives. Most users run it once per Codex profile or machine; after that, the second command installs `code-crew` from that source.

Install from a local clone:

```bash
codex plugin marketplace add .
codex plugin add code-crew@code-crew
```

If you downloaded only the `plugins/code-crew/` package directory, install from the GitHub marketplace source above or place that package under your own Codex marketplace. A bare plugin directory is not itself a Codex marketplace root.

Do not run `codex plugin marketplace add .` from inside `plugins/code-crew/`; that directory is a plugin root, not a supported Codex marketplace shape.

This installs `plugins/code-crew/`, including the full core persona briefs in `plugins/code-crew/skills/code-crew/briefs/`.

After installation, Code Crew is available as a skill. In an interactive Codex session, either select it with `/skills` or invoke it directly:

```text
$code-crew review the current diff
```

You can also ask in natural language:

```text
Use Code Crew to review this PR with the default Knuth + Hickey + Torvalds crew.
```

The plugin does not add a `/code-crew` slash command, background hook, or automatic always-on reviewer.

## Claude Code

Claude Code plugins use `.claude-plugin/plugin.json` plus plugin-root components such as `skills/`.

Install from GitHub:

```bash
claude plugin marketplace add gmentat/code-crew --sparse .claude-plugin plugins
claude plugin install code-crew
```

Install from a local clone:

```bash
claude plugin marketplace add ./ --scope project
claude plugin install code-crew
```

For one-session local testing:

```bash
claude --plugin-dir ./plugins/code-crew
```

## Hermes

Hermes uses local skill folders with `SKILL.md`.

Install the published skill directly:

```bash
hermes skills install https://raw.githubusercontent.com/gmentat/code-crew/main/plugins/code-crew/skills/code-crew/SKILL.md \
  --category software-development \
  --name code-crew \
  --yes
```

Local development symlink:

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$PWD/plugins/code-crew/skills/code-crew" ~/.hermes/skills/software-development/code-crew
hermes skills list | grep code-crew
```

## OpenClaw-Compatible Runtimes

The plugin root includes `openclaw.plugin.json`, which points at the same `SKILL.md` folder. A local OpenClaw binary was not available during validation, so this repo does not publish a tested OpenClaw CLI command yet.

Use `plugins/code-crew/` as the plugin root in runtimes that support OpenClaw-style plugin manifests. Use `plugins/code-crew/skills/code-crew/` as the skill root in runtimes that support AgentSkills-compatible `SKILL.md` folders.

## Cursor

From a full source clone, Cursor can use the project rule already committed at `.cursor/rules/code-crew.mdc`.

To install the rule into another project:

```bash
mkdir -p /path/to/target-project/.cursor/rules
cp .cursor/rules/code-crew.mdc /path/to/target-project/.cursor/rules/code-crew.mdc
```

If you downloaded only the plugin package, copy `plugins/code-crew/cursor/code-crew.mdc` into the target project's `.cursor/rules/` directory instead.

The Cursor rule is opt-in. It does not run as an always-on reviewer; ask Cursor to use Code Crew when you want the review.

## What It Installs

The skill adds the famous-programmer review crew:

- Knuth for rigor, algorithms, invariants, complexity, and literate clarity.
- Hickey for simplicity, data, value/identity/time, and incidental complexity.
- Torvalds for practical maintainer review, patch scope, and working systems.

It only installs skill files and persona briefs. Nothing runs in the background.

## Invocation Model

Code Crew is a prompt skill. The host agent loads the skill when selected explicitly, invoked by name, or routed from a matching review/design request. It is not a resident process and does not run on every file edit or commit.

In Codex, the installed skill may appear as `code-crew:code-crew`. That is expected. It is not a callable tool exposed in the tool list.

If an agent says it cannot find a Code Crew callable tool after you selected `$code-crew`, that is a routing mistake. The skill is already loaded; it should use the host's generic subagent mechanism when available, or label the run as a single-context approximation when not.

If a runtime supports custom commands, any command should call the same `code-crew` skill instructions rather than maintaining a separate prompt.
