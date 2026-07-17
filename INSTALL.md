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

To update an existing GitHub installation:

```bash
codex plugin marketplace upgrade code-crew
codex plugin add code-crew@code-crew
```

Install from a local clone:

```bash
codex plugin marketplace add .
codex plugin add code-crew@code-crew
```

If you downloaded only the `plugins/code-crew/` package directory, install from the GitHub marketplace source above or place that package under your own Codex marketplace. A bare plugin directory is not itself a Codex marketplace root.

Do not run `codex plugin marketplace add .` from inside `plugins/code-crew/`; that directory is a plugin root, not a supported Codex marketplace shape.

This installs `plugins/code-crew/`, including the full persona and workflow files in `plugins/code-crew/skills/code-crew/references/`.

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

Install the published skill by its GitHub repo-path identifier:

```bash
hermes skills install gmentat/code-crew/plugins/code-crew/skills/code-crew \
  --category software-development \
  --yes
```

The GitHub identifier lets Hermes track the source for later updates. Current Hermes releases install `SKILL.md` plus the explicitly linked files under standard support directories; Code Crew keeps all required persona and workflow material under `references/` and its optional calibration material under `examples/`.

Local development symlink:

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$PWD/plugins/code-crew/skills/code-crew" ~/.hermes/skills/software-development/code-crew
hermes skills list | grep code-crew
```

## OpenClaw-Compatible Runtimes

The plugin root includes `openclaw.plugin.json`, which points at the same `SKILL.md` folder. OpenClaw documents local-path installs:

```bash
openclaw plugins install ./plugins/code-crew
# or install just the skill folder:
openclaw skills install ./plugins/code-crew/skills/code-crew
```

A local OpenClaw binary was not available during validation, so these commands are OpenClaw-documented but not yet verified by this repo. Prefer clone-then-local-path over the `git:` source form: OpenClaw's docs state git and local *skill* installs expect `SKILL.md` at the source root, subdirectory installs from a git source are not documented for plugins, and this repo nests the package under `plugins/code-crew/`.

Use `plugins/code-crew/` as the plugin root in runtimes that support OpenClaw-style plugin manifests. OpenClaw also runs AgentSkills-style `SKILL.md` folders natively.

## Cursor

On Cursor 2.4+, install Code Crew as a native Agent Skill — Cursor reads the same `SKILL.md` folder format:

```bash
# project-scoped
mkdir -p /path/to/target-project/.cursor/skills
cp -R plugins/code-crew/skills/code-crew /path/to/target-project/.cursor/skills/code-crew

# or global
mkdir -p ~/.cursor/skills
cp -R plugins/code-crew/skills/code-crew ~/.cursor/skills/code-crew
```

The skill becomes slash-invokable in the editor and the Cursor CLI, and Cursor's native subagents (2.4+) can run the personas as independent blind passes. The package also includes a Cursor plugin manifest at `plugins/code-crew/.cursor-plugin/plugin.json`, with the rule auto-discovered from `plugins/code-crew/rules/`; the plugin has not yet been submitted to the Cursor marketplace.

For older Cursor versions, the explicit-invocation project rule still works:

```bash
mkdir -p /path/to/target-project/.cursor/rules
cp .cursor/rules/code-crew.mdc /path/to/target-project/.cursor/rules/code-crew.mdc
```

If you downloaded only the plugin package, copy `plugins/code-crew/cursor/code-crew.mdc` instead.

Both surfaces are opt-in. Neither runs as an always-on reviewer; ask Cursor to use Code Crew when you want the review.

## Other AgentSkills-Compatible Hosts

`plugins/code-crew/skills/code-crew/` follows the open Agent Skills format ([agentskills.io](https://agentskills.io)). The generic install is copying the folder into a host's documented skills directory.

Gemini CLI and other hosts adopting the vendor-neutral convention read `.agents/skills/` (project) and `~/.agents/skills/` (global):

```bash
mkdir -p ~/.agents/skills
cp -R plugins/code-crew/skills/code-crew ~/.agents/skills/code-crew
```

GitHub Copilot reads `.github/skills/` (project) and `~/.copilot/skills/` (user), per GitHub's docs.

These copy destinations follow the Gemini CLI and GitHub Copilot documentation but have not been smoke-tested by this repo. GitHub CLI also provides `gh skill` commands in public preview; this project is not yet published through that channel.

## What It Installs

The skill adds the famous-programmer review crew:

- Knuth for rigor, algorithms, invariants, complexity, and literate clarity.
- Hickey for simplicity, data, value/identity/time, and incidental complexity.
- Torvalds for practical maintainer review, patch scope, and working systems.

It only installs skill instructions and persona references. Nothing runs in the background.

## Invocation Model

Code Crew is a prompt skill. The host agent loads it when selected explicitly or when a request names Code Crew, K+H+T, famous-programmer lenses, or an independent multi-lens review. It is not a resident process and does not run on every file edit or commit.

In Codex, the installed skill may appear as `code-crew:code-crew`. That is expected. It is not a callable tool exposed in the tool list.

If an agent says it cannot find a Code Crew callable tool after you selected `$code-crew`, that is a routing mistake. The skill is already loaded; it should use the host's generic subagent mechanism when available, or label the run as a single-context approximation when not.

If a runtime supports custom commands, any command should call the same `code-crew` skill instructions rather than maintaining a separate prompt.
