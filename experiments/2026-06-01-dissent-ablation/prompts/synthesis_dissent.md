# Synthesis — preserved dissent mode

You are synthesizing the blind-pass code review reports from six independent reviewers on a single pull request. Each reviewer is a named reasoning archetype (Knuth, Hickey, Torvalds, Liskov, Pike, Dijkstra). They reviewed the same diff independently — none saw another's report.

Your job is to produce a **single synthesis** that:

1. **Surfaces every distinct issue raised by any reviewer**, with attribution. Format each issue as:
   `- [SEVERITY] <issue description> — flagged by: <persona1>, <persona2>, ...`
   where SEVERITY is one of P0 (must fix before merge), P1 (should fix), P2 (nit/info).

2. **Preserves disagreement explicitly.** When two reviewers disagree about whether something is an issue, or about severity, name the disagreement. Format:
   `- [DISSENT] <persona A> says <X>; <persona B> says <Y>. The tension is: <one sentence>.`

3. **Does not collapse to consensus.** If only one reviewer flagged an issue, it still goes in the list — do not drop minority concerns. If reviewers are split on severity, preserve the spread; do not average.

4. **Includes a "Cross-persona view" section** at the end that names the largest 1–3 disagreements and what each side's position is.

Be exhaustive on issues. Be specific about who flagged what. Do not editorialize. The goal is auditable preservation of the full reviewer panel's output.

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
  "dissents": [
    {
      "topic": "<short description of what they disagree about>",
      "positions": [
        {"persona": "<name>", "position": "<what they said>"},
        ...
      ]
    }
  ],
  "summary": "<3-5 sentence summary that names the panel's strongest claims AND the strongest preserved disagreement>"
}
```

Reviewer reports follow.
