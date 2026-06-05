# Using Code Crew With Cursor

If you downloaded only the `plugins/code-crew/` package, copy the rule template into your target project:

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

Formal Code Crew runs still require independent passes. If the host cannot isolate persona contexts, label the output as a single-context approximation.
