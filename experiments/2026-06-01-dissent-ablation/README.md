# DA-PRB — Dissent Ablation on SWE-PRBench

Empirical test of the **code_crew pattern** against a single-agent baseline on real code review.

This directory contains a reproducible experiment that measures whether the crew's distinctive features — preserved dissent in synthesis, blind-pass independence, named reasoning archetypes — translate to measurable improvement in code review recall over a budget-matched single Claude agent.

## TL;DR — what we found

| Run | n | H1 (dissent > consensus) | H2 (crew > budget single) | H3 (personas diverge) | Sanity (crew > naive single) |
|---|---|---|---|---|---|
| **Pilot** | 3 | +0.200 (3-0) | +0.200 (3-0) | broken metric | +0.283 (3-0) |
| **Main (bias-mitigated)** | 50 | **+0.012, p=0.41 ❌** | **+0.025, p=0.15 ❌** | **0.565, PASS ✓** | **+0.074, p=0.0035 ✓** |

**Headline:** the pilot did not replicate. At n=50 with an anonymized + skeptic-framed judge:
- **Preserved-dissent synthesis is NOT the active ingredient** (consensus synthesis is statistically indistinguishable on recall).
- **Multi-perspective review DOES beat naive single-agent** (+7pp recall, paired p=0.004).
- The crew's value is in *process* (interpretable disagreement, persona-attributed dissent visible to reviewers) — **not in measurably better issue-list outputs** vs a comparably-budgeted single agent.

Full writeup: [`runs/main/SUMMARY.md`](runs/main/SUMMARY.md). Pilot for comparison: [`runs/pilot/SUMMARY.md`](runs/pilot/SUMMARY.md).

## What's being tested

Three pre-registered hypotheses, in [`PROTOCOL.md`](PROTOCOL.md):

- **H1 — preserved dissent matters.** Crew synthesis that preserves dissent beats crew synthesis that collapses to consensus on recall (paired sign test).
- **H2 — multi-pass beats single-pass at equal compute.** Crew beats a single Claude agent with the same realized token budget.
- **H3 — personas actually diverge** (manipulation check, gating). If H3 fails, H1/H2 conclusions are aborted.

Substrate: [`foundry-ai/swe-prbench`](https://huggingface.co/datasets/foundry-ai/swe-prbench) — 350 real PRs, human-annotated review comments as ground truth.

## Data and attribution

All scored content under `runs/*/<task_id>/` is derived from the public [`foundry-ai/swe-prbench`](https://huggingface.co/datasets/foundry-ai/swe-prbench) dataset (CC BY 4.0). The `human_review_comments` ground truth and embedded PR content include real-author attribution from the upstream dataset; we redistribute that derived content under the dataset's existing terms and do not add new PII.

## How to run (the way we ran it)

The crew is designed to be invoked from inside Claude Code / Codex as subagents — not driven from a Python API loop. The runnable harness here dispatches everything through the Workflow tool, using your Claude Code subscription credentials. **No API keys required.**

```bash
# Install Python deps (used only for sampling / preprocessing / analysis)
uv sync

# Sample PRs (deterministic; seed=42)
uv run python scripts/select_prs.py --pilot   # 3 PRs, harness validation
uv run python scripts/select_prs.py --main    # 50 PRs, the main run

# Build the prompt bundle and generate the workflow script
uv run python scripts/prepare_main_prompts.py
uv run python scripts/gen_main_workflow.py     # emits two sharded workflow scripts

# Inside Claude Code, dispatch the workflow:
#   /workflow scripts/main_workflow_a.js
#   /workflow scripts/main_workflow_b.js
# (the shards exist because Workflow caps inline scripts at 524KB)

# Materialize results, analyze
uv run python scripts/materialize_main.py <transcript-path-a>
uv run python scripts/materialize_main.py <transcript-path-b>
uv run python scripts/analyze.py --run main
```

The full main run (n=50, ~750 subagents) cost ~24M tokens and ~80 min wall-clock (two shards in parallel).

### Optional: direct API path

If you want to run this with raw API access (e.g. for a non-Claude judge to remove the Claude-judging-Claude caveat), `scripts/orchestrate.py` + `scripts/crew_pass.py` + `scripts/score.py` provide a parallel SDK-driven path. That path requires `ANTHROPIC_API_KEY` (crew passes) and `OPENAI_API_KEY` (GPT-5.1 judge per `PROTOCOL.md`). It was not used for the main run reported here.

## Status

- ✅ Substrate verified (`foundry-ai/swe-prbench` on HuggingFace)
- ✅ Protocol pre-registered ([`PROTOCOL.md`](PROTOCOL.md), frozen 2026-06-01)
- ✅ Harness scripts built (Workflow-driven + optional SDK-driven)
- ✅ Pilot completed (3 PRs × 4 arms) — [`runs/pilot/SUMMARY.md`](runs/pilot/SUMMARY.md)
- ✅ **Main run completed (50 PRs × 4 arms + H3 check) — [`runs/main/SUMMARY.md`](runs/main/SUMMARY.md)**
- ⏳ Optional follow-up: full n=80 with non-Claude judge (GPT-5.1) — requires API keys per PROTOCOL.md

## Decision rules (from PROTOCOL.md) — outcome

| Outcome | What gets published | **Triggered?** |
|---|---|---|
| H1 confirmed + H3 passes | *"Preserved dissent improves PR review recall by Xpp over consensus synthesis at equal compute."* | ❌ |
| H1 null, H2 confirmed | *"Multi-pass review beats single-pass at equal compute, but dissent isn't the active ingredient."* | ◐ (H2 direction right, n.s.) |
| **Both null** | ***"Multi-persona review does not outperform single-agent extended-thinking on PR recall at equal budget. OSS pivots to process/audit claim."*** | **✅** |
| H3 fails | Methodology note only. Ship v2 with stronger persona enforcement and retest. | n/a (H3 passed) |

OSS framing therefore shifts from "preserved dissent improves recall" → **"the crew's product is auditable disagreement, not better issue lists."**

## Directory layout

```
2026-06-01-dissent-ablation/
├── PROTOCOL.md              # frozen pre-registration
├── README.md                # this file
├── DEVIATIONS.md            # departures from PROTOCOL.md, dated
├── pyproject.toml           # uv project
├── prompts/                 # frozen prompts (personas, synthesis, single-agent)
├── scripts/
│   ├── select_prs.py        # deterministic sample (--pilot / --main / default=full 80)
│   ├── prepare_main_prompts.py    # builds data/main_prompts.json
│   ├── gen_main_workflow.py # generates Workflow scripts (2 shards)
│   ├── main_workflow_a.js   # generated, runnable via Workflow tool
│   ├── main_workflow_b.js   # generated, runnable via Workflow tool
│   ├── materialize_main.py  # extracts Workflow result into runs/main/
│   ├── analyze.py           # paired sign tests, H3, ANALYSIS.json
│   ├── crew_pass.py         # SDK-driven persona pass (optional API path)
│   ├── synthesize.py        # SDK-driven synthesis (optional API path)
│   ├── single_agent.py      # SDK-driven baseline (optional API path)
│   ├── score.py             # SDK-driven judge (optional API path; GPT-5.1)
│   └── orchestrate.py       # SDK-driven full pipeline (optional API path)
├── data/
│   ├── prs_pilot.json       # 3 PRs
│   └── prs_main.json        # 50 PRs (the main run)
└── runs/
    ├── pilot/               # n=3 results
    │   ├── SUMMARY.md
    │   ├── ANALYSIS.json
    │   └── <task_id>/       # per-PR raw outputs
    └── main/                # n=50 results
        ├── SUMMARY.md
        ├── ANALYSIS.json
        └── <task_id>/       # per-PR raw outputs (incl. h3_similarity.json)
```

## Why this is in the repo

The code_crew pattern makes empirical claims. Most multi-agent frameworks ship claims without measurement. This directory exists so anyone can re-run the experiment, verify the numbers, and challenge the methodology — including the methodology that *contradicted* the project's original hypothesis.

When code_crew is released open-source, this experiment ships with it as a **proof-of-claim test**, including the null result.

## License

The repository's own code, prompts, plugin files, and analysis scripts are MIT licensed. SWE-PRBench-derived scored content remains under the upstream dataset's CC BY 4.0 terms; see "Data and attribution" above.
