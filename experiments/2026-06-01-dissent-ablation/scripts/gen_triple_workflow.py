"""Generate sharded workflow scripts that test 8 new triples against the persona-run baseline.

Per PR per triple: 1 synthesis (using inlined existing passes) + 1 judge = 2 agents.
8 triples × 50 PRs × 2 agents = 800 agents. Sharded 5 ways (~10 PRs each).

Output: scripts/triple_workflow_{1..5}.js
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA

# 8 new triples to test. K+H+T and D+L+P scores are reused from the persona run.
# Triples are chosen to test the "span 3 axes" hypothesis: rigor + architectural + pragmatic.
# Knuth/Dijkstra = rigor axis. Hickey/Liskov/Pike = architectural axis. Torvalds = pragmatic axis.
TRIPLES = [
    ["knuth", "liskov", "torvalds"],  # K+L+T  rigor + abstract + pragmatic
    ["knuth", "pike", "torvalds"],  # K+P+T  rigor + composition + pragmatic
    ["dijkstra", "hickey", "torvalds"],  # D+H+T  formal + simple + pragmatic
    ["dijkstra", "liskov", "torvalds"],  # D+L+T  formal + abstract + pragmatic
    ["dijkstra", "pike", "torvalds"],  # D+P+T  formal + composition + pragmatic
    ["knuth", "hickey", "dijkstra"],  # K+H+D  no pragmatic (control)
    ["hickey", "liskov", "pike"],  # H+L+P  no rigor, no pragmatic (control)
    ["liskov", "pike", "torvalds"],  # L+P+T  no rigor (control)
]


def make_script(
    shard_id, n_prs, js_data, triples_js, review_schema_js, judge_schema_js
):
    return f"""
export const meta = {{
  name: 'da-prb-triples-{shard_id}',
  description: 'Triple composition search shard {shard_id} — {n_prs} PRs × 8 triples (existing passes reused)',
  phases: [
    {{ title: 'Syntheses' }},
    {{ title: 'Scoring' }},
  ],
}}

const DATA = {js_data}
const TRIPLES = {triples_js}
const REVIEW_SCHEMA = {review_schema_js}
const JUDGE_SCHEMA  = {judge_schema_js}

const TERSE_RULES = `\\n\\nCRITICAL OUTPUT RULES:
- Maximum 6 issues. Pick the most important; do not pad.
- Each "detail" field: at most 60 words. Plain prose. No multi-paragraph essays.
- Each "description": one sentence.
- Call the StructuredOutput tool with your final JSON. Do NOT emit JSON as prose.`

function tripleKey(t) {{ return t.join('+') }}

function synthesisPrompt(pr, triple) {{
  const sections = triple.map(p => {{
    const review = pr.passes[p]
    return `### Reviewer: ${{p[0].toUpperCase() + p.slice(1)}}\\n\\`\\`\\`json\\n${{JSON.stringify(review, null, 2)}}\\n\\`\\`\\``
  }}).join('\\n\\n')
  return `${{DATA.synthesis_template}}

${{TERSE_RULES}}

---

PR under review: ${{pr.task_id}} — synthesizing triple ${{tripleKey(triple)}}

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

// ============= PHASE 1: syntheses (one per PR per triple) =============
phase('Syntheses')
const synthTasks = []
for (const pr of DATA.prs) {{
  for (const triple of TRIPLES) {{
    synthTasks.push({{ pr, triple }})
  }}
}}
const synthResults = await parallel(synthTasks.map(t => () =>
  agent(synthesisPrompt(t.pr, t.triple), {{
    schema: REVIEW_SCHEMA,
    label: `synth:${{t.pr.task_id}}:${{tripleKey(t.triple)}}`,
    phase: 'Syntheses',
  }})
))
const syntheses = {{}}
for (let i = 0; i < synthTasks.length; i++) {{
  const t = synthTasks[i]
  const k = tripleKey(t.triple)
  syntheses[t.pr.task_id] = syntheses[t.pr.task_id] || {{}}
  syntheses[t.pr.task_id][k] = synthResults[i]
}}

// ============= PHASE 2: scoring =============
phase('Scoring')
const scoreTasks = []
for (const pr of DATA.prs) {{
  for (const triple of TRIPLES) {{
    const k = tripleKey(triple)
    const issues = (syntheses[pr.task_id][k] || {{}}).issues || []
    scoreTasks.push({{ pr, key: k, issues }})
  }}
}}
const scoreResults = await parallel(scoreTasks.map(t => () =>
  agent(judgePrompt(t.pr, t.issues || []), {{
    schema: JUDGE_SCHEMA,
    label: `score:${{t.pr.task_id}}:${{t.key}}`,
    phase: 'Scoring',
  }})
))
const scores = {{}}
for (let i = 0; i < scoreTasks.length; i++) {{
  const t = scoreTasks[i]
  scores[t.pr.task_id] = scores[t.pr.task_id] || {{}}
  scores[t.pr.task_id][t.key] = scoreResults[i]
}}

return {{ syntheses, scores }}
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


def main() -> None:
    bundle = json.loads((DATA / "triple_prompts.json").read_text())
    all_prs = bundle["prs"]
    n = len(all_prs)
    cuts = [int(n * i / 5) for i in range(6)]
    triples_js = json.dumps(TRIPLES)
    review_schema_js = json.dumps(REVIEW_SCHEMA)
    judge_schema_js = json.dumps(JUDGE_SCHEMA)
    for i in range(5):
        shard_prs = all_prs[cuts[i] : cuts[i + 1]]
        if not shard_prs:
            continue
        shard_bundle = {**bundle, "prs": shard_prs}
        js_data = json.dumps(shard_bundle).replace("</", "<\\/")
        out = Path(__file__).resolve().parent / f"triple_workflow_{i + 1}.js"
        out.write_text(
            make_script(
                i + 1,
                len(shard_prs),
                js_data,
                triples_js,
                review_schema_js,
                judge_schema_js,
            ).strip()
            + "\n"
        )
        print(f"wrote {out} ({out.stat().st_size:,} bytes, {len(shard_prs)} PRs)")


if __name__ == "__main__":
    main()
