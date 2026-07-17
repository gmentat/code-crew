# Using Code Crew With Cursor

On Cursor 2.4+, the preferred install is the native Agent Skill — copy the skill folder from this package:

```bash
mkdir -p /path/to/target-project/.cursor/skills
cp -R skills/code-crew /path/to/target-project/.cursor/skills/code-crew
```

(or `~/.cursor/skills/` for all projects). The skill is slash-invokable in the editor and the Cursor CLI. This package also includes `.cursor-plugin/plugin.json`, with the rule auto-discovered from `rules/`.

For older Cursor versions, copy the rule template into your target project instead:

```bash
mkdir -p /path/to/target-project/.cursor/rules
cp cursor/code-crew.mdc /path/to/target-project/.cursor/rules/code-crew.mdc
```

Then invoke it explicitly:

```text
Use Code Crew to review the current diff.
Use Code Crew, Torvalds only, to decide whether this patch should land.
Use Code Crew to critique this design for incidental complexity.
```

The Cursor rule is a convenience surface. The canonical skill remains `skills/code-crew/SKILL.md`.

Formal Code Crew runs still require independent passes. On Cursor 2.4+, dispatch each persona as a native subagent with its own context to run formal blind passes. On older Cursor, or when subagents are unavailable, label the output as a single-context approximation.
