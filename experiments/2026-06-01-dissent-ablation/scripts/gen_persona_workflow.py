"""Generate sharded persona-ablation workflow scripts.

Per PR, each shard runs:
  - 6 named persona passes  + 6 generic reviewer passes      (Phase 1)
  - 5 syntheses: named-6, generic-6, triple-A (K+H+T),
                 triple-B (D+L+P), pair-TL (T+L)             (Phase 2)
  - 11 judges: 6 solos (per named persona) + 5 syntheses     (Phase 3)
  - 1 H3 classifier on generic-6                             (Phase 4)

= 29 agents / PR. Sharded into 4 scripts (~12-13 PRs each) to stay under
the Workflow tool's 524KB inline-script size cap.

Output: scripts/persona_workflow_{1..4}.js
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import DATA, PERSONAS

# Hand-picked composition arms (HP3, HP4).
TRIPLE_A = ["knuth", "hickey", "torvalds"]  # rigor + simplicity + pragmatism
TRIPLE_B = ["dijkstra", "liskov", "pike"]  # formal + abstract + composition
PAIR_TL = ["torvalds", "liskov"]  # pragmatic + abstract


def main() -> None:
    bundle = json.loads((DATA / "persona_prompts.json").read_text())
    all_prs = bundle["prs"]

    # 4 even-ish shards.
    n = len(all_prs)
    cuts = [0, n // 4, n // 2, 3 * n // 4, n]
    shards = []
    for i in range(4):
        shard_prs = all_prs[cuts[i] : cuts[i + 1]]
        if not shard_prs:
            continue
        shards.append((i + 1, {**bundle, "prs": shard_prs}))

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
            "dissents": {"type": "array"},
            "summary": {"type": "string"},
        },
        "required": ["issues", "summary"],
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
            "personas": {"type": "array", "items": {"type": "string"}},
            "matrix": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "number"}},
            },
            "notes": {"type": "string"},
        },
        "required": ["personas", "matrix"],
    }

    review_schema_js = json.dumps(review_schema)
    judge_schema_js = json.dumps(judge_schema)
    h3_schema_js = json.dumps(h3_schema)
    personas_list_js = json.dumps(PERSONAS)
    triple_a_js = json.dumps(TRIPLE_A)
    triple_b_js = json.dumps(TRIPLE_B)
    pair_tl_js = json.dumps(PAIR_TL)
    generic_ids_js = json.dumps([f"generic_{i}" for i in range(1, 7)])

    for shard_id, shard_bundle in shards:
        js_data = json.dumps(shard_bundle).replace("</", "<\\/")
        out = Path(__file__).resolve().parent / f"persona_workflow_{shard_id}.js"
        script = make_script(
            shard_id,
            len(shard_bundle["prs"]),
            js_data,
            personas_list_js,
            generic_ids_js,
            triple_a_js,
            triple_b_js,
            pair_tl_js,
            review_schema_js,
            judge_schema_js,
            h3_schema_js,
        )
        out.write_text(script.strip() + "\n")
        print(
            f"wrote {out} ({out.stat().st_size:,} bytes, {len(shard_bundle['prs'])} PRs)"
        )


def make_script(
    shard_id: int,
    n_prs: int,
    js_data: str,
    personas_list_js: str,
    generic_ids_js: str,
    triple_a_js: str,
    triple_b_js: str,
    pair_tl_js: str,
    review_schema_js: str,
    judge_schema_js: str,
    h3_schema_js: str,
) -> str:
    return f"""
export const meta = {{
  name: 'da-prb-persona-{shard_id}',
  description: 'Persona ablation shard {shard_id} — {n_prs} PRs, 12 arms (named/generic/solos/triples/pair)',
  phases: [
    {{ title: 'Passes (named + generic)' }},
    {{ title: 'Syntheses' }},
    {{ title: 'Scoring' }},
    {{ title: 'H3 generic-6' }},
  ],
}}

const DATA = {js_data}
const PERSONAS = {personas_list_js}
const GENERIC_IDS = {generic_ids_js}
const TRIPLE_A = {triple_a_js}
const TRIPLE_B = {triple_b_js}
const PAIR_TL  = {pair_tl_js}
const REVIEW_SCHEMA = {review_schema_js}
const JUDGE_SCHEMA  = {judge_schema_js}
const H3_SCHEMA     = {h3_schema_js}

// VERBOSITY CAP: the first run failed because persona briefs encouraged 5-8K-token
// reviews that hit soft response limits and never called StructuredOutput. The cap
// keeps each agent under ~2K output tokens.
const TERSE_RULES = `\\n\\nCRITICAL OUTPUT RULES:
- Maximum 6 issues. Pick the most important; do not pad.
- Each "detail" field: at most 60 words. Plain prose. No multi-paragraph essays.
- Each "description": one sentence.
- Call the StructuredOutput tool with your final JSON. Do NOT emit JSON as prose.`

function personaPassPrompt(personaName, pr) {{
  const brief = DATA.personas[personaName]
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

function genericPassPrompt(genericId, pr) {{
  return `You are ${{genericId.replace('_', ' ').replace(/\\b\\w/g, c => c.toUpperCase())}}, one of six independent reviewers on this PR. You don't see the others.

${{DATA.generic_reviewer}}

---

${{DATA.review_output_instruction}}

${{TERSE_RULES}}

---

${{pr.formatted_for_review}}

Output ONLY the JSON object via StructuredOutput. Use "${{genericId}}" in flagged_by.`
}}

function synthesisPrompt(pr, passesByName, label) {{
  const sections = Object.keys(passesByName).map(p => {{
    const obj = JSON.stringify(passesByName[p], null, 2)
    const title = p[0].toUpperCase() + p.slice(1)
    return `### Reviewer: ${{title}}\\n\\`\\`\\`json\\n${{obj}}\\n\\`\\`\\``
  }}).join('\\n\\n')
  return `${{DATA.synthesis_template}}

${{TERSE_RULES}}

---

PR under review: ${{pr.task_id}} (${{pr.repo}}) — synthesizing ${{label}}

${{sections}}

Output ONLY the JSON object via StructuredOutput.`
}}

// Anonymized + skeptic-framed judge. Identical to the main run's judge.
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

Call StructuredOutput with your verdicts. Each verdict reason: one short sentence. Default to FABRICATED when uncertain.`
}}

function h3Prompt(pr, passesByName) {{
  const order = Object.keys(passesByName)
  const reviewBlocks = order.map(p => {{
    const issues = (passesByName[p] && passesByName[p].issues) || []
    const brief = issues.map((iss, i) => `  ${{i + 1}}. [${{iss.severity}}] ${{iss.description}}${{iss.detail ? ' — ' + (iss.detail || '').slice(0, 200) : ''}}`).join('\\n')
    return `### ${{p[0].toUpperCase() + p.slice(1)}} flagged ${{issues.length}} issue(s)\\n${{brief || '  (no issues flagged)'}}`
  }}).join('\\n\\n')
  return `Six reviewers each independently reviewed the same pull request. For each PAIR of reviewers, compute the **Jaccard similarity** of their flagged concerns: |intersection| / |union|, where two issues count as the same concern if they identify the SAME underlying problem (paraphrase OK; different file/line OK if it's the same underlying defect).

A reviewer with zero flagged issues contributes |intersection|=0 with everyone; Jaccard with another empty reviewer is 1.0; Jaccard with a non-empty reviewer is 0.0.

Output a 6x6 matrix in the order: ${{JSON.stringify(order)}}. Diagonal = 1.0. Symmetric matrix.

PR: ${{pr.repo}} — ${{pr.title}}

${{reviewBlocks}}

Output JSON exactly matching:
\\`\\`\\`json
{{
  "personas": ${{JSON.stringify(order)}},
  "matrix": [[1.0, ...], [...], [...], [...], [...], [..., 1.0]],
  "notes": "<one sentence on how much overlap you saw>"
}}
\\`\\`\\`

Output ONLY the JSON.`
}}

// ============= PHASE 1: passes (named + generic) =============
phase('Passes (named + generic)')
const passTasks = []
for (const pr of DATA.prs) {{
  for (const p of PERSONAS) {{
    passTasks.push({{ pr, kind: 'named', name: p }})
  }}
  for (const g of GENERIC_IDS) {{
    passTasks.push({{ pr, kind: 'generic', name: g }})
  }}
}}

const passResults = await parallel(passTasks.map(t => () => {{
  const prompt = t.kind === 'named'
    ? personaPassPrompt(t.name, t.pr)
    : genericPassPrompt(t.name, t.pr)
  return agent(prompt, {{
    schema: REVIEW_SCHEMA,
    label: `pass:${{t.pr.task_id}}:${{t.name}}`,
    phase: 'Passes (named + generic)',
  }})
}}))

const passes = {{}}      // {{ task_id: {{ persona/generic_id: review }} }}
for (let i = 0; i < passTasks.length; i++) {{
  const t = passTasks[i]
  passes[t.pr.task_id] = passes[t.pr.task_id] || {{}}
  passes[t.pr.task_id][t.name] = passResults[i]
}}

// ============= PHASE 2: syntheses =============
phase('Syntheses')
const synthTasks = []
for (const pr of DATA.prs) {{
  const namedPasses    = Object.fromEntries(PERSONAS.map(p => [p, passes[pr.task_id][p]]))
  const genericPasses  = Object.fromEntries(GENERIC_IDS.map(g => [g, passes[pr.task_id][g]]))
  const tripleAPasses  = Object.fromEntries(TRIPLE_A.map(p => [p, passes[pr.task_id][p]]))
  const tripleBPasses  = Object.fromEntries(TRIPLE_B.map(p => [p, passes[pr.task_id][p]]))
  const pairTLPasses   = Object.fromEntries(PAIR_TL.map(p => [p, passes[pr.task_id][p]]))
  synthTasks.push({{ pr, arm: 'named-6',   passesByName: namedPasses,   label: 'named-6'    }})
  synthTasks.push({{ pr, arm: 'generic-6', passesByName: genericPasses, label: 'generic-6'  }})
  synthTasks.push({{ pr, arm: 'triple-A',  passesByName: tripleAPasses, label: 'triple-A (K+H+T)' }})
  synthTasks.push({{ pr, arm: 'triple-B',  passesByName: tripleBPasses, label: 'triple-B (D+L+P)' }})
  synthTasks.push({{ pr, arm: 'pair-TL',   passesByName: pairTLPasses,  label: 'pair-TL (T+L)' }})
}}

const synthResults = await parallel(synthTasks.map(t => () =>
  agent(synthesisPrompt(t.pr, t.passesByName, t.label), {{
    schema: REVIEW_SCHEMA,
    label: `synth:${{t.pr.task_id}}:${{t.arm}}`,
    phase: 'Syntheses',
  }})
))

const syntheses = {{}}  // {{ task_id: {{ arm: synth }} }}
for (let i = 0; i < synthTasks.length; i++) {{
  const t = synthTasks[i]
  syntheses[t.pr.task_id] = syntheses[t.pr.task_id] || {{}}
  syntheses[t.pr.task_id][t.arm] = synthResults[i]
}}

// ============= PHASE 3: scoring =============
phase('Scoring')
const scoreTasks = []
for (const pr of DATA.prs) {{
  // 6 solo arms (judge each named persona's blind-pass output as a standalone review)
  for (const p of PERSONAS) {{
    const issues = (passes[pr.task_id][p] || {{}}).issues || []
    scoreTasks.push({{ pr, arm: `solo-${{p}}`, issues }})
  }}
  // 5 synthesis arms
  for (const arm of ['named-6', 'generic-6', 'triple-A', 'triple-B', 'pair-TL']) {{
    const issues = (syntheses[pr.task_id][arm] || {{}}).issues || []
    scoreTasks.push({{ pr, arm, issues }})
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

// ============= PHASE 4: H3 on generic-6 =============
phase('H3 generic-6')
const h3Tasks = DATA.prs.map(pr => {{
  const genericPasses = Object.fromEntries(GENERIC_IDS.map(g => [g, passes[pr.task_id][g]]))
  return {{ pr, passesByName: genericPasses }}
}})
const h3Results = await parallel(h3Tasks.map(t => () =>
  agent(h3Prompt(t.pr, t.passesByName), {{
    schema: H3_SCHEMA,
    label: `h3:${{t.pr.task_id}}:generic-6`,
    phase: 'H3 generic-6',
  }})
))
const h3 = {{}}
for (let i = 0; i < h3Tasks.length; i++) {{
  h3[h3Tasks[i].pr.task_id] = h3Results[i]
}}

return {{ passes, syntheses, scores, h3 }}
"""


if __name__ == "__main__":
    main()
