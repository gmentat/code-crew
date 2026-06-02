"""Generate a workflow script with all pilot data inlined.

Output: scripts/pilot_workflow.js — a self-contained Workflow script.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA, PERSONAS


def main() -> None:
    bundle = json.loads((DATA / "pilot_prompts.json").read_text())
    js_data = json.dumps(bundle).replace("</", "<\\/")
    out = Path(__file__).resolve().parent / "pilot_workflow.js"

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

    personas_list = json.dumps(PERSONAS)
    review_schema_js = json.dumps(review_schema)
    judge_schema_js = json.dumps(judge_schema)

    script = f"""
export const meta = {{
  name: 'da-prb-pilot',
  description: 'Dissent Ablation pilot — 3 PRs through 4 arms with judge scoring',
  phases: [
    {{ title: 'Crew passes' }},
    {{ title: 'Syntheses' }},
    {{ title: 'Single-agent baselines' }},
    {{ title: 'Scoring' }},
  ],
}}

const DATA = {js_data}
const PERSONAS = {personas_list}
const REVIEW_SCHEMA = {review_schema_js}
const JUDGE_SCHEMA = {judge_schema_js}

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

function judgePrompt(arm, pr, flaggedIssues) {{
  const indexed = flaggedIssues.map((iss, i) => ({{
    index: i,
    severity: iss.severity,
    description: iss.description,
    detail: (iss.detail || '').slice(0, 600),
    file: iss.file,
    lines: iss.lines,
  }}))
  return `You are scoring AI-generated code-review feedback against real human reviewer comments. Be strict but fair.

For each flagged issue, classify as:
- **CONFIRMED**: substantively matches at least one human reviewer comment (paraphrase OK, same concern).
- **PLAUSIBLE**: not in human comments, but a competent reviewer would consider it a real concern on inspection.
- **FABRICATED**: does not correspond to anything in the diff, misreads the code, or is a generic non-issue.

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

## AI-flagged issues to judge (arm=${{arm}})
\\`\\`\\`json
${{JSON.stringify(indexed, null, 2)}}
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

// Organize passes by pr.task_id → persona → result
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

// ============= PHASE 4: scoring =============
phase('Scoring')
const scoreTasks = []
for (const pr of DATA.prs) {{
  // Crew arms (dissent / consensus) — judge their synthesized issue lists
  for (const mode of ['dissent', 'consensus']) {{
    const issues = syntheses[pr.task_id][mode] ? syntheses[pr.task_id][mode].issues : []
    scoreTasks.push({{ pr, arm: mode, issues }})
  }}
  // Single-agent arms — judge their direct issue lists
  for (const variant of ['budget', 'naive']) {{
    const issues = singles[pr.task_id][variant] ? singles[pr.task_id][variant].issues : []
    scoreTasks.push({{ pr, arm: variant, issues }})
  }}
}}

const scoreResults = await parallel(scoreTasks.map(t => () =>
  agent(judgePrompt(t.arm, t.pr, t.issues || []), {{
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

return {{ passes, syntheses, singles, scores }}
"""
    out.write_text(script.strip() + "\n")
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
