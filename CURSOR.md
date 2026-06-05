# Using Code Crew With Cursor

This repository includes a Cursor project rule at `.cursor/rules/code-crew.mdc`.

If you downloaded only the plugin package, use the copyable template at `plugins/code-crew/cursor/code-crew.mdc`; package-local instructions are in `plugins/code-crew/CURSOR.md`.

The rule is **not always-on**. Invoke it when you want a Code Crew review or design critique:

```text
Use Code Crew to review the current diff.
Use Code Crew, Torvalds only, to decide whether this patch should land.
Use Code Crew to critique this design for incidental complexity.
```

Cursor rule support is a convenience surface, not a separate implementation. The canonical package remains `plugins/code-crew/`, and the canonical skill instructions remain `plugins/code-crew/skills/code-crew/SKILL.md`.

Formal Code Crew runs still require independent passes. If the host cannot isolate persona contexts, label the output as a single-context approximation and do not claim it as a formal crew run.
