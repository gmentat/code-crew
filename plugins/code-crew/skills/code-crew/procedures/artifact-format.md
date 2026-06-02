# Artifact format — persistent review records

Loaded when the user wants a Code Crew review persisted to disk (not just printed). Defines the on-disk layout so reviews are auditable and comparable across runs.

## When to write artifacts

Write **only** when one of these is true:

- The user explicitly asks ("save this review", "write it to disk", "put this under runs/").
- The host is configured for CI / artifact mode (an environment variable, host flag, or hook that signals this run's output is consumed by another process, not just shown in chat).

Do **not** write artifacts on your own initiative — not for "substantive findings", not for "this seems important", not for "the user might want this later". Chat output is the default; disk output is opt-in. Unexpected `runs/` writes are intrusive and the user should never have to clean them up.

## Directory layout

One folder per formal run:

```
runs/YYYY-MM-DD-<topic>_<host>/
├── 01_knuth.md           # blind pass, full markdown
├── 02_hickey.md
├── 03_torvalds.md
├── 04_verifier.md        # verifier's per-finding verdicts
├── 99_synthesis.md       # final review (what the user sees)
└── meta.json             # crew, briefs loaded, host, model, commit SHA
```

- `YYYY-MM-DD` is the run date.
- `<topic>` is a kebab-case slug derived from the PR title, file under review, or user query.
- `<host>` suffix is one of `_claude`, `_codex`, `_hermes`, or another agent runner name. **Always include it.** Different hosts produce slightly different outputs and the suffix lets future readers tell them apart at a glance.

Numbered prefixes (`01_`, `02_`, `99_`) keep the directory sortable in the order the review was produced. Reserve `99_` for the synthesis so it's always the last file.

## Single-lens shortcuts

When the user invoked a solo lens (e.g. "Torvalds-only review"), still write the folder:

```
runs/YYYY-MM-DD-<topic>_<host>/
├── 01_torvalds.md
├── 02_verifier.md
└── 99_synthesis.md
```

Number the verifier `02_` since there's only one persona pass. Synthesis stays `99_`.

## meta.json schema

```json
{
  "date": "YYYY-MM-DD",
  "host": "claude | codex | hermes | <other>",
  "model": "<model-id reported by the host>",
  "crew": ["knuth", "hickey", "torvalds"],
  "briefs_loaded": ["briefs/knuth_agent.md", "briefs/hickey_agent.md", "briefs/torvalds_agent.md"],
  "verifier_used": true,
  "scope": {
    "type": "diff | file | pr | design",
    "target": "<path or PR URL>",
    "commit_sha": "<git SHA at review time, if applicable>"
  },
  "recommendation": "LAND | LAND WITH FIXES | REQUEST CHANGES | REDESIGN | NEEDS MORE EVIDENCE",
  "finding_counts": { "critical": 0, "high": 0, "medium": 0, "low": 0 }
}
```

## Hard rules

- **Do not overwrite an existing `runs/<date-topic-host>/`.** If the slug collides, append `_2`, `_3`, etc. Past reviews are evidence; preserve them.
- **Do not commit `runs/` to git automatically.** The user decides what's worth versioning. The repo-level `.gitignore` may already exclude it; do not work around that.
- **Do not write artifacts the user didn't ask for.** "I saved your review to runs/..." is annoying if they expected a chat reply.
- **Always end with the synthesis output in chat**, even when writing artifacts. The disk copy is for auditability; the chat copy is what the user reads now.
