"""Generate the main-run workflow script with all data inlined.

Improvements over pilot_workflow.js:
  1. Anonymized judge prompt — no `arm=...` label leak; judge sees only "issues to judge".
  2. Skeptic framing — judge instructed to default to FABRICATED on doubt, breaking
     Claude's mild self-preference.
  3. LLM-based H3 manipulation check — one classifier per PR computes a 6x6 pairwise
     persona-issue-similarity matrix from semantic matching (replacing the broken
     exact-fingerprint Jaccard the pilot used).

Sharded into two scripts (a/b) because the Workflow tool caps inline scripts at 524KB.
The shards are independent runs; their outputs are merged at materialization time.

Output: scripts/main_workflow_a.js, scripts/main_workflow_b.js
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA, PERSONAS


def main() -> None:
    bundle = json.loads((DATA / "main_prompts.json").read_text())
    all_prs = bundle["prs"]
    half = len(all_prs) // 2
    shards = {
        "a": {**bundle, "prs": all_prs[:half]},
        "b": {**bundle, "prs": all_prs[half:]},
    }

    review_schema = {
        "type": "object",
        "properties": {
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["P0", "P1", "P2"]},
                        "description": {"type": "string"},
                        "detail": {"type": "string"},
                        "file": {"type": ["string", "null"]},
                        "lines": {"type": ["string", "null"]},
                        "flagged_by": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["severity", "description", "flagged_by"],
                },
            },
            "dissents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "positions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "persona": {"type": "string"},
                                    "position": {"type": "string"},
                                },
                                "required": ["persona", "position"],
                            },
                        },
                    },
                    "required": ["topic", "positions"],
                },
            },
            "summary": {"type": "string"},
        },
        "required": ["issues", "dissents", "summary"],
    }

    judge_schema = {
        "type": "object",
        "properties": {
            "verdicts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "label": {
                            "type": "string",
                            "enum": ["CONFIRMED", "PLAUSIBLE", "FABRICATED"],
                        },
                        "reason": {"type": "string"},
                    },
                    "required": ["index", "label", "reason"],
                },
            },
            "ground_truth_recall": {
                "type": "object",
                "properties": {
                    "total_human_comments": {"type": "integer"},
                    "comments_matched_by_ai": {"type": "integer"},
                    "comments_missed": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "total_human_comments",
                    "comments_matched_by_ai",
                    "comments_missed",
                ],
            },
        },
        "required": ["verdicts", "ground_truth_recall"],
    }

    h3_schema = {
        "type": "object",
        "properties": {
            "personas": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 6,
                "maxItems": 6,
            },
            "matrix": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 6,
                    "maxItems": 6,
                },
                "minItems": 6,
                "maxItems": 6,
            },
            "notes": {"type": "string"},
        },
        "required": ["personas", "matrix"],
    }

    personas_list = json.dumps(PERSONAS)
    review_schema_js = json.dumps(review_schema)
    judge_schema_js = json.dumps(judge_schema)
    h3_schema_js = json.dumps(h3_schema)

    for shard_id, shard_bundle in shards.items():
        js_data = json.dumps(shard_bundle).replace("</", "<\\/")
        out = Path(__file__).resolve().parent / f"main_workflow_{shard_id}.js"
        script = make_script(
            shard_id,
            len(shard_bundle["prs"]),
            js_data,
            personas_list,
            review_schema_js,
            judge_schema_js,
            h3_schema_js,
        )
        out.write_text(script.strip() + "\n")
        print(
            f"wrote {out} ({out.stat().st_size:,} bytes, {len(shard_bundle['prs'])} PRs)"
        )


def make_script(
    shard_id: str,
    n_prs: int,
    js_data: str,
    personas_list: str,
    review_schema_js: str,
    judge_schema_js: str,
    h3_schema_js: str,
) -> str:
    return f"""
export const meta = {{
  name: 'da-prb-main-{shard_id}',
  description: 'Dissent Ablation main run shard {shard_id} — {n_prs} PRs through 4 arms with bias-mitigated judge + LLM H3 check',
  phases: [
    {{ title: 'Crew passes' }},
    {{ title: 'Syntheses' }},
    {{ title: 'Single-agent baselines' }},
    {{ title: 'Scoring' }},
    {{ title: 'H3 manipulation check' }},
  ],
}}

const DATA = {js_data}
const PERSONAS = {personas_list}
const REVIEW_SCHEMA = {review_schema_js}
const JUDGE_SCHEMA = {judge_schema_js}
const H3_SCHEMA = {h3_schema_js}

function reviewOutputInstruction() {{
  return DATA.review_output_instruction
}}

function personaPassPrompt(personaName, pr) {{
  const brief = DATA.personas[personaName]
  return `You are the **${{personaName[0].toUpperCase() + personaName.slice(1)}}** code-review archetype. Adopt the operating principles, process, tone, and decision labels from the brief. Review the pull request below as that lens.

---

${{brief}}

---

${{reviewOutputInstruction()}}

---

${{pr.formatted_for_review}}

Output ONLY the JSON object. Use your persona name (${{personaName}}) in flagged_by.`
}}

function synthesisPrompt(mode, pr, passes) {{
  const template = DATA.templates[`synthesis_${{mode}}`]
  const sections = PERSONAS.map(p => {{
    const obj = JSON.stringify(passes[p], null, 2)
    return `### Reviewer: ${{p[0].toUpperCase() + p.slice(1)}}\\n\\`\\`\\`json\\n${{obj}}\\n\\`\\`\\``
  }}).join('\\n\\n')
  return `${{template}}

---

PR under review: ${{pr.task_id}} (${{pr.repo}})

${{sections}}

Output ONLY the JSON object.`
}}

function singleAgentPrompt(variant, pr) {{
  const template = DATA.templates.single_agent
  const hint = variant === 'budget'
    ? '\\n\\nTake extra care: produce a thorough review with multiple perspectives.'
    : ''
  return `${{template}}${{hint}}

---

${{pr.formatted_for_review}}

Output ONLY the JSON object.`
}}

// Anonymized + skeptic-framed judge prompt.
// - No arm label.
// - Issues from the AI are stripped of \`flagged_by\` before being shown to the judge,
//   so the judge cannot tell which arm produced which issue.
// - Skeptic framing: default to FABRICATED unless evidence is strong.
function judgePrompt(pr, flaggedIssues) {{
  const indexed = flaggedIssues.map((iss, i) => ({{
    index: i,
    severity: iss.severity,
    description: iss.description,
    detail: (iss.detail || '').slice(0, 600),
    file: iss.file,
    lines: iss.lines,
    // flagged_by intentionally omitted to prevent arm leakage
  }}))
  return `You are scoring AI-generated code-review feedback against real human reviewer comments. You are a strict skeptic: when in doubt, mark FABRICATED, not PLAUSIBLE. Generic concerns ("consider adding tests" with no specific gap), vague style notes, or misreadings of the diff are FABRICATED. A finding is only CONFIRMED if it substantively matches a real human reviewer concern (paraphrase OK). A finding is only PLAUSIBLE if a competent reviewer would clearly raise it on inspection of THIS diff — not in general.

Output JSON exactly matching:
\\`\\`\\`json
{{
  "verdicts": [{{"index": <int>, "label": "CONFIRMED" | "PLAUSIBLE" | "FABRICATED", "reason": "<one sentence>"}}],
  "ground_truth_recall": {{
    "total_human_comments": <int>,
    "comments_matched_by_ai": <int>,
    "comments_missed": ["<short description of each missed concern>"]
  }}
}}
\\`\\`\\`

## PR: ${{pr.repo}} — ${{pr.title}}

## Human review comments (ground truth)
\\`\\`\\`json
${{JSON.stringify(pr.human_review_comments, null, 2)}}
\\`\\`\\`

## AI-flagged issues to judge
\\`\\`\\`json
${{JSON.stringify(indexed, null, 2)}}
\\`\\`\\`

Output ONLY the JSON. Default to FABRICATED when uncertain.`
}}

// LLM-based H3 manipulation check: given the 6 persona reviews, compute a pairwise
// "fraction of concerns shared" matrix using semantic matching (not exact strings).
function h3Prompt(pr, passes) {{
  const reviewBlocks = PERSONAS.map(p => {{
    const issues = (passes[p] && passes[p].issues) || []
    const brief = issues.map((iss, i) => `  ${{i + 1}}. [${{iss.severity}}] ${{iss.description}}${{iss.detail ? ' — ' + (iss.detail || '').slice(0, 200) : ''}}`).join('\\n')
    return `### ${{p[0].toUpperCase() + p.slice(1)}} flagged ${{issues.length}} issue(s)\\n${{brief || '  (no issues flagged)'}}`
  }}).join('\\n\\n')
  return `Six reviewers each independently reviewed the same pull request. For each PAIR of reviewers, compute the **Jaccard similarity** of their flagged concerns: |intersection| / |union|, where two issues count as the same concern if they identify the SAME underlying problem (paraphrase OK; different file/line OK if it's the same underlying defect). Differently-described variants of the same root cause = same concern. Cosmetic vs semantic concerns = different.

A reviewer with zero flagged issues contributes |intersection|=0 with everyone; Jaccard with another empty reviewer is 1.0; Jaccard with a non-empty reviewer is 0.0.

Output a 6x6 matrix in the persona order: ["knuth", "hickey", "torvalds", "liskov", "pike", "dijkstra"]. Diagonal = 1.0. Symmetric matrix.

PR: ${{pr.repo}} — ${{pr.title}}

${{reviewBlocks}}

Output JSON exactly matching:
\\`\\`\\`json
{{
  "personas": ["knuth", "hickey", "torvalds", "liskov", "pike", "dijkstra"],
  "matrix": [[1.0, ...], [...], [...], [...], [...], [..., 1.0]],
  "notes": "<one sentence on how much overlap you saw>"
}}
\\`\\`\\`

Output ONLY the JSON.`
}}

// ============= PHASE 1: crew passes =============
phase('Crew passes')
const passTasks = []
for (const pr of DATA.prs) {{
  for (const p of PERSONAS) {{
    passTasks.push({{ pr, persona: p }})
  }}
}}

const passResults = await parallel(passTasks.map(t => () =>
  agent(personaPassPrompt(t.persona, t.pr), {{
    schema: REVIEW_SCHEMA,
    label: `pass:${{t.pr.task_id}}:${{t.persona}}`,
    phase: 'Crew passes',
  }})
))

const passes = {{}}
for (let i = 0; i < passTasks.length; i++) {{
  const t = passTasks[i]
  passes[t.pr.task_id] = passes[t.pr.task_id] || {{}}
  passes[t.pr.task_id][t.persona] = passResults[i]
}}

// ============= PHASE 2: syntheses =============
phase('Syntheses')
const synthTasks = []
for (const pr of DATA.prs) {{
  for (const mode of ['dissent', 'consensus']) {{
    synthTasks.push({{ pr, mode }})
  }}
}}

const synthResults = await parallel(synthTasks.map(t => () =>
  agent(synthesisPrompt(t.mode, t.pr, passes[t.pr.task_id]), {{
    schema: REVIEW_SCHEMA,
    label: `synth:${{t.pr.task_id}}:${{t.mode}}`,
    phase: 'Syntheses',
  }})
))

const syntheses = {{}}
for (let i = 0; i < synthTasks.length; i++) {{
  const t = synthTasks[i]
  syntheses[t.pr.task_id] = syntheses[t.pr.task_id] || {{}}
  syntheses[t.pr.task_id][t.mode] = synthResults[i]
}}

// ============= PHASE 3: single-agent baselines =============
phase('Single-agent baselines')
const singleTasks = []
for (const pr of DATA.prs) {{
  for (const variant of ['budget', 'naive']) {{
    singleTasks.push({{ pr, variant }})
  }}
}}

const singleResults = await parallel(singleTasks.map(t => () =>
  agent(singleAgentPrompt(t.variant, t.pr), {{
    schema: REVIEW_SCHEMA,
    label: `single:${{t.pr.task_id}}:${{t.variant}}`,
    phase: 'Single-agent baselines',
  }})
))

const singles = {{}}
for (let i = 0; i < singleTasks.length; i++) {{
  const t = singleTasks[i]
  singles[t.pr.task_id] = singles[t.pr.task_id] || {{}}
  singles[t.pr.task_id][t.variant] = singleResults[i]
}}

// ============= PHASE 4: scoring (anonymized + skeptic) =============
phase('Scoring')
const scoreTasks = []
for (const pr of DATA.prs) {{
  for (const mode of ['dissent', 'consensus']) {{
    const issues = syntheses[pr.task_id][mode] ? syntheses[pr.task_id][mode].issues : []
    scoreTasks.push({{ pr, arm: mode, issues }})
  }}
  for (const variant of ['budget', 'naive']) {{
    const issues = singles[pr.task_id][variant] ? singles[pr.task_id][variant].issues : []
    scoreTasks.push({{ pr, arm: variant, issues }})
  }}
}}

const scoreResults = await parallel(scoreTasks.map(t => () =>
  agent(judgePrompt(t.pr, t.issues || []), {{
    schema: JUDGE_SCHEMA,
    label: `score:${{t.pr.task_id}}:${{t.arm}}`,
    phase: 'Scoring',
  }})
))

const scores = {{}}
for (let i = 0; i < scoreTasks.length; i++) {{
  const t = scoreTasks[i]
  scores[t.pr.task_id] = scores[t.pr.task_id] || {{}}
  scores[t.pr.task_id][t.arm] = scoreResults[i]
}}

// ============= PHASE 5: H3 manipulation check =============
phase('H3 manipulation check')
const h3Tasks = DATA.prs.map(pr => ({{ pr }}))
const h3Results = await parallel(h3Tasks.map(t => () =>
  agent(h3Prompt(t.pr, passes[t.pr.task_id]), {{
    schema: H3_SCHEMA,
    label: `h3:${{t.pr.task_id}}`,
    phase: 'H3 manipulation check',
  }})
))
const h3 = {{}}
for (let i = 0; i < h3Tasks.length; i++) {{
  h3[h3Tasks[i].pr.task_id] = h3Results[i]
}}

return {{ passes, syntheses, singles, scores, h3 }}
"""


if __name__ == "__main__":
    main()
