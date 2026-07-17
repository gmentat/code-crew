# Code Crew Plugin

Code Crew packages the famous-programmer review crew as a portable agent skill/plugin.

Default preset:

- Knuth: rigor, algorithms, invariants, complexity.
- Hickey: simplicity, data, value/identity/time, incidental complexity.
- Torvalds: maintainer-grade patch acceptance and practical systems review.

The package is prompt-only. It adds reusable skill instructions and persona references, not running software.

The package includes the full core persona lenses under `skills/code-crew/references/`. Those files are byte-identical to the persona prompts used by the experiment harness.

It also includes on-demand workflow and example files. These improve invocation and implementation discipline without changing the tested persona content.

## Install

### Codex

Codex installs Code Crew from a marketplace. The full source repo includes a root marketplace at `.agents/plugins/marketplace.json` that points to `./plugins/code-crew`.

From GitHub:

```bash
codex plugin marketplace add gmentat/code-crew
codex plugin add code-crew@code-crew
```

The first command tells Codex where this repo's plugin marketplace lives. Most users run it once per Codex profile or machine; after that, the second command installs `code-crew` from that marketplace.

Update an existing GitHub installation with:

```bash
codex plugin marketplace upgrade code-crew
codex plugin add code-crew@code-crew
```

From a full local clone, run from the repository root:

```bash
codex plugin marketplace add .
codex plugin add code-crew@code-crew
```

If you downloaded only the `plugins/code-crew/` package directory, use the GitHub marketplace install above or place the package under a Codex marketplace that points to it. The package directory itself is a plugin root, not a Codex marketplace root.

Package-root local install was intentionally not documented because `codex plugin marketplace add .` must point at a marketplace, not a bare plugin root.

Codex installs the plugin root, including `.codex-plugin/plugin.json`, `skills/code-crew/SKILL.md`, and the bundled persona and workflow files under `skills/code-crew/references/`.

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

Hermes uses `SKILL.md` skill folders. Install the published skill by its GitHub repo-path identifier:

```bash
hermes skills install gmentat/code-crew/plugins/code-crew/skills/code-crew \
  --category software-development \
  --yes
```

The GitHub identifier lets Hermes track the source for later updates. Current Hermes releases install `SKILL.md` plus its explicitly linked files under `references/` and `examples/`.

For local development from the package root, copy or symlink the skill folder:

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$PWD/skills/code-crew" ~/.hermes/skills/software-development/code-crew
hermes skills list | grep code-crew
```

### OpenClaw-Compatible Runtimes

The plugin root includes `openclaw.plugin.json`. OpenClaw documents local-path installs — `openclaw plugins install <path-to-this-package>` or `openclaw skills install <path>/skills/code-crew` — but this repo has not yet verified them against a live OpenClaw binary. Prefer a clone/download + local-path install over the `git:` source form (git skill installs expect `SKILL.md` at the source root, and subdirectory git installs are not documented; in the full source repo this package is nested under `plugins/code-crew/`). Use the package directory as the plugin root, or `skills/code-crew/` as the skill root in AgentSkills-compatible runtimes.

### Cursor

On Cursor 2.4+, install the skill folder directly — Cursor reads the same AgentSkills `SKILL.md` format:

```bash
mkdir -p /path/to/target-project/.cursor/skills
cp -R skills/code-crew /path/to/target-project/.cursor/skills/code-crew
```

(or `~/.cursor/skills/` for all projects). The skill is slash-invokable in the editor and CLI, and Cursor's native subagents can run the personas as independent blind passes. The package also includes `.cursor-plugin/plugin.json`, with the rule auto-discovered from `rules/`.

For older Cursor, copy the package-local rule template `cursor/code-crew.mdc` into your target project's `.cursor/rules/` directory. Neither surface is always-on; invoke Code Crew explicitly. See package-local `CURSOR.md`.

## Usage

Code Crew installs as a skill. It does not run in the background or review every change automatically; ask for it when you want the crew.

In Codex, either choose it from `/skills` or invoke it directly:

```text
$code-crew review the current diff
```

In fresh Codex sessions the installed skill may appear as `code-crew:code-crew`. That is expected. Code Crew is not exposed as a callable review tool; it is a skill the host agent loads when selected or invoked. If an agent tries to search for a separate Code Crew tool, it is using the wrong mental model; selecting `$code-crew` is already the invocation.

You can also ask your agent:

```text
Use Code Crew to review the current diff.
```

Or request a specific lens:

```text
Use Code Crew, Torvalds only, to decide whether this patch should land.
```

The skill may be routed automatically when a request names Code Crew, K+H+T, famous-programmer lenses, or an independent multi-lens review, but explicit invocation is the reliable path. Code Crew does not currently provide a `/code-crew` command.

For code-changing follow-up work, the skill loads `references/implementation-discipline.md`: state assumptions, keep the change surgical, and verify with concrete checks before claiming success.

## How To Know It Worked

Code Crew is working as intended when:

- independent persona passes happened, or the host clearly labeled the result as a single-context approximation
- final findings cite concrete `file:line` evidence or quoted source spans
- the verifier rejected unsupported claims before synthesis
- the recommendation follows from the surviving findings
- the Verification block says exactly what was run, or explicitly says what was not run

## Evidence Boundary

The benchmark result supports the default K+H+T preset as the best tested composition in this repo's PR-review experiments. The reported recall numbers are raw recall because the original fixed-precision metric was not computable under the skeptic judge. The result does not prove that famous names alone improve recall. The naming is retained because it makes the lenses memorable and easier to discuss.

## License

The plugin package is MIT licensed; see `LICENSE`. If you are using the full repository, also read the root `NOTICE` for the license boundary around SWE-PRBench-derived experiment data.

## Contributor Note

Keep the duplicated distribution surfaces synchronized when changing usage, install, or metadata:

- root `README.md`
- `INSTALL.md`
- `CURSOR.md`
- `.cursor/rules/code-crew.mdc`
- `plugins/code-crew/CURSOR.md`
- `plugins/code-crew/cursor/code-crew.mdc`
- `plugins/code-crew/rules/code-crew.mdc`
- `plugins/code-crew/README.md`
- `plugins/code-crew/.claude-plugin/plugin.json`
- `plugins/code-crew/.codex-plugin/plugin.json`
- `plugins/code-crew/.cursor-plugin/plugin.json`
- `plugins/code-crew/openclaw.plugin.json`
- top-level marketplace manifests
- `plugins/code-crew/skills/code-crew/SKILL.md`
