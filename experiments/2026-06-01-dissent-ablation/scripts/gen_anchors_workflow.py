"""Emit 2 sharded framing-ablation workflow scripts.

Per PR per shard: 3 direct-K/H/T passes + 1 consensus synthesis + 1 judge = 5 agents.
25 PRs/shard × 5 = 125 agents/shard. 50 PRs total → 2 shards.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA

TRIPLE = ["knuth", "hickey", "torvalds"]


def make_script(shard_id, n_prs, js_data, triple_js, review_schema_js, judge_schema_js):
    return f"""
export const meta = {{
  name: 'anchors-ablation-{shard_id}',
  description: 'Persona framing ablation shard {shard_id} — K+H+T direct-named briefs on {n_prs} PRs',
  phases: [
    {{ title: 'Passes (direct-named)' }},
    {{ title: 'Syntheses' }},
    {{ title: 'Scoring' }},
  ],
}}

const DATA = {js_data}
const TRIPLE = {triple_js}
const REVIEW_SCHEMA = {review_schema_js}
const JUDGE_SCHEMA  = {judge_schema_js}

const TERSE_RULES = `\\n\\nCRITICAL OUTPUT RULES:
- Maximum 6 issues. Pick the most important; do not pad.
- Each "detail" field: at most 60 words. Plain prose. No multi-paragraph essays.
- Each "description": one sentence.
- Call the StructuredOutput tool with your final JSON. Do NOT emit JSON as prose.`

function personaPassPrompt(personaName, pr) {{
  const brief = DATA.personas_anchored[personaName]
  return `You are the **${{personaName[0].toUpperCase() + personaName.slice(1)}}** code-review archetype. Adopt the operating principles, process, tone, and decision labels from the brief. Review the pull request below as that lens.

---

${{brief}}

---

${{DATA.review_output_instruction}}

${{TERSE_RULES}}

---

${{pr.formatted_for_review}}

Output ONLY the JSON object via StructuredOutput. Use your persona name (${{personaName}}) in flagged_by.`
}}

function synthesisPrompt(pr, passesByName) {{
  const sections = TRIPLE.map(p => {{
    const obj = JSON.stringify(passesByName[p], null, 2)
    const title = p[0].toUpperCase() + p.slice(1)
    return `### Reviewer: ${{title}}\\n\\`\\`\\`json\\n${{obj}}\\n\\`\\`\\``
  }}).join('\\n\\n')
  return `${{DATA.synthesis_template}}

${{TERSE_RULES}}

---

PR under review: ${{pr.task_id}} (${{pr.repo}}) — synthesizing anchored K+H+T

${{sections}}

Output ONLY the JSON object via StructuredOutput.`
}}

function judgePrompt(pr, flaggedIssues) {{
  const indexed = flaggedIssues.map((iss, i) => ({{
    index: i,
    severity: iss.severity,
    description: iss.description,
    detail: (iss.detail || '').slice(0, 600),
    file: iss.file,
    lines: iss.lines,
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

Call StructuredOutput. Each reason: one short sentence. Default to FABRICATED when uncertain.`
}}

// ============= PHASE 1: passes =============
phase('Passes (direct-named)')
const passTasks = []
for (const pr of DATA.prs) {{
  for (const p of TRIPLE) {{
    passTasks.push({{ pr, persona: p }})
  }}
}}
const passResults = await parallel(passTasks.map(t => () =>
  agent(personaPassPrompt(t.persona, t.pr), {{
    schema: REVIEW_SCHEMA,
    label: `pass:${{t.pr.task_id}}:${{t.persona}}-anchored`,
    phase: 'Passes (direct-named)',
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
const synthTasks = DATA.prs.map(pr => ({{
  pr,
  passesByName: Object.fromEntries(TRIPLE.map(p => [p, passes[pr.task_id][p]])),
}}))
const synthResults = await parallel(synthTasks.map(t => () =>
  agent(synthesisPrompt(t.pr, t.passesByName), {{
    schema: REVIEW_SCHEMA,
    label: `synth:${{t.pr.task_id}}:anchored`,
    phase: 'Syntheses',
  }})
))
const syntheses = {{}}
for (let i = 0; i < synthTasks.length; i++) {{
  syntheses[synthTasks[i].pr.task_id] = synthResults[i]
}}

// ============= PHASE 3: scoring =============
phase('Scoring')
const scoreTasks = DATA.prs.map(pr => ({{
  pr,
  issues: (syntheses[pr.task_id] || {{}}).issues || [],
}}))
const scoreResults = await parallel(scoreTasks.map(t => () =>
  agent(judgePrompt(t.pr, t.issues), {{
    schema: JUDGE_SCHEMA,
    label: `score:${{t.pr.task_id}}:anchored`,
    phase: 'Scoring',
  }})
))
const scores = {{}}
for (let i = 0; i < scoreTasks.length; i++) {{
  scores[scoreTasks[i].pr.task_id] = scoreResults[i]
}}

return {{ passes, syntheses, scores }}
"""


REVIEW_SCHEMA = {
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
        "dissents": {"type": "array"},
        "summary": {"type": "string"},
    },
    "required": ["issues", "summary"],
}
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "label": {"type": "string", "enum": ["CONFIRMED", "PLAUSIBLE", "FABRICATED"]},
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
            "required": ["total_human_comments", "comments_matched_by_ai", "comments_missed"],
        },
    },
    "required": ["verdicts", "ground_truth_recall"],
}


def main() -> None:
    bundle = json.loads((DATA / "anchors_prompts.json").read_text())
    all_prs = bundle["prs"]
    n = len(all_prs)
    half = n // 2
    shards = [
        (1, all_prs[:half]),
        (2, all_prs[half:]),
    ]
    triple_js = json.dumps(TRIPLE)
    review_schema_js = json.dumps(REVIEW_SCHEMA)
    judge_schema_js = json.dumps(JUDGE_SCHEMA)
    for shard_id, shard_prs in shards:
        shard_bundle = {**bundle, "prs": shard_prs}
        js_data = json.dumps(shard_bundle).replace("</", "<\\/")
        out = Path(__file__).resolve().parent / f"anchors_workflow_{shard_id}.js"
        out.write_text(make_script(shard_id, len(shard_prs), js_data, triple_js,
                                   review_schema_js, judge_schema_js).strip() + "\n")
        print(f"wrote {out} ({out.stat().st_size:,} bytes, {len(shard_prs)} PRs)")


if __name__ == "__main__":
    main()
