# Using Code Crew With Cursor

On Cursor 2.4+, the preferred install is the native Agent Skill — Cursor reads the same `SKILL.md` folder this repo ships:

```bash
mkdir -p /path/to/target-project/.cursor/skills
cp -R plugins/code-crew/skills/code-crew /path/to/target-project/.cursor/skills/code-crew
```

(or `~/.cursor/skills/` for all projects). The skill is slash-invokable in the editor and the Cursor CLI. The package also ships a Cursor plugin manifest at `plugins/code-crew/.cursor-plugin/plugin.json`, with the rule auto-discovered from `plugins/code-crew/rules/`.

For older Cursor versions, this repository includes a project rule at `.cursor/rules/code-crew.mdc`. If you downloaded only the plugin package, use the copyable template at `plugins/code-crew/cursor/code-crew.mdc`; package-local instructions are in `plugins/code-crew/CURSOR.md`.

Neither surface is **always-on**. Invoke Code Crew when you want a review or design critique:

```text
Use Code Crew to review the current diff.
Use Code Crew, Torvalds only, to decide whether this patch should land.
Use Code Crew to critique this design for incidental complexity.
```

Cursor rule support is a convenience surface, not a separate implementation. The canonical package remains `plugins/code-crew/`, and the canonical skill instructions remain `plugins/code-crew/skills/code-crew/SKILL.md`.

Formal Code Crew runs still require independent passes. On Cursor 2.4+, dispatch each persona as a native subagent with its own context to run formal blind passes. On older Cursor, or when subagents are unavailable, label the output as a single-context approximation and do not claim it as a formal crew run.
