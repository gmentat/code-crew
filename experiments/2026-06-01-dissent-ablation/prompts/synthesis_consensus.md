# Synthesis — consensus mode

You are synthesizing the blind-pass code review reports from six independent reviewers on a single pull request. Each reviewer is a named reasoning archetype (Knuth, Hickey, Torvalds, Liskov, Pike, Dijkstra). They reviewed the same diff independently — none saw another's report.

Your job is to produce a **single synthesis** that:

1. **Resolves the panel to a single consensus list of issues.** For each issue, decide the severity the panel agrees on (P0 / P1 / P2). When reviewers disagree about severity, pick the severity supported by the most reviewers (ties broken by the higher severity).

2. **Drops minority-only concerns.** If only one reviewer flagged something, omit it unless the issue is clearly substantive enough to survive panel scrutiny.

3. **Resolves disagreements to a single position.** When reviewers contradict each other, pick the position supported by the majority. Do not preserve a "dissent" section.

4. **Produces a clean prioritized list** that a developer could action without seeing the underlying reviews.

Be decisive. Aim for a high-confidence consensus output. Do not editorialize. The goal is one clean actionable list.

---

**Format your output as JSON exactly matching this schema:**

```json
{
  "issues": [
    {
      "severity": "P0" | "P1" | "P2",
      "description": "<one-line summary of the issue>",
      "detail": "<2-4 sentence explanation>",
      "file": "<path or null>",
      "lines": "<line range or null>",
      "flagged_by": ["<persona>", ...]
    }
  ],
  "dissents": [],
  "summary": "<3-5 sentence consensus summary of the panel's main verdict>"
}
```

Reviewer reports follow.
