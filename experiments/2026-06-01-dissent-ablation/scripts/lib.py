"""Shared utilities: data loading, prompt assembly, model calls."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
DATA = ROOT / "data"
RUNS = ROOT / "runs"

PERSONAS = ["knuth", "hickey", "torvalds", "liskov", "pike", "dijkstra"]
SWE_PRBENCH_DATASET = "foundry-ai/swe-prbench"
SWE_PRBENCH_CONFIG = "eval_split"
SWE_PRBENCH_REVISION = "b87f5797aef3ed2c3153bb1304ea4d801d36ba6e"  # pragma: allowlist secret


@dataclass
class Issue:
    severity: str  # "P0" | "P1" | "P2"
    description: str
    detail: str = ""
    file: str | None = None
    lines: str | None = None
    flagged_by: list[str] = field(default_factory=list)


@dataclass
class Dissent:
    topic: str
    positions: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ReviewOutput:
    issues: list[Issue]
    dissents: list[Dissent]
    summary: str

    def to_json(self) -> dict[str, Any]:
        return {
            "issues": [asdict(i) for i in self.issues],
            "dissents": [asdict(d) for d in self.dissents],
            "summary": self.summary,
        }

    @classmethod
    def from_json(cls, obj: dict[str, Any]) -> "ReviewOutput":
        return cls(
            issues=[Issue(**i) for i in obj.get("issues", [])],
            dissents=[Dissent(**d) for d in obj.get("dissents", [])],
            summary=obj.get("summary", ""),
        )


# ---------- Dataset loading ----------


def load_pr_by_task_id(task_id: str) -> dict[str, Any]:
    """Load a single PR row from swe-prbench by task_id."""
    from datasets import load_dataset

    ds = load_dataset(
        SWE_PRBENCH_DATASET,
        SWE_PRBENCH_CONFIG,
        revision=SWE_PRBENCH_REVISION,
    )["train"]
    for row in ds:
        if row["task_id"] == task_id:
            return dict(row)
    raise KeyError(task_id)


def format_pr_for_review(pr: dict[str, Any], diff_max_chars: int = 40_000) -> str:
    """Render PR into reviewer-facing context. Truncate giant diffs for cost control."""
    diff = pr.get("diff_patch") or ""
    if len(diff) > diff_max_chars:
        diff = (
            diff[:diff_max_chars] + f"\n\n[...diff truncated at {diff_max_chars} chars]"
        )
    return (
        f"# Pull Request {pr['task_id']}\n"
        f"**Repo:** {pr['repo']}\n"
        f"**Title:** {pr['title']}\n"
        f"**Type:** {pr.get('pr_type', 'unknown')} | "
        f"**Language:** {pr.get('language', 'unknown')} | "
        f"**Difficulty:** {pr.get('difficulty', 'unknown')}\n\n"
        f"## Description\n{pr.get('description', '(no description)')}\n\n"
        f"## Diff\n```diff\n{diff}\n```\n"
    )


def load_persona_brief(persona: str) -> str:
    p = PROMPTS / f"{persona}_agent.md"
    return p.read_text()


# ---------- Prompt assembly ----------

REVIEW_OUTPUT_INSTRUCTION = """
You must output JSON exactly matching this schema (no prose outside the JSON):

```json
{
  "issues": [
    {
      "severity": "P0" | "P1" | "P2",
      "description": "<one-line summary>",
      "detail": "<2-4 sentence explanation>",
      "file": "<path or null>",
      "lines": "<line range or null>",
      "flagged_by": ["<persona-name>"]
    }
  ],
  "dissents": [],
  "summary": "<3-5 sentence summary>"
}
```

P0 = must fix before merge. P1 = should fix. P2 = nit/info.
Use `flagged_by` to record your own persona name only.
""".strip()


def build_persona_pass_prompt(persona: str, pr: dict[str, Any]) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for one persona's blind pass."""
    brief = load_persona_brief(persona)
    system = (
        f"You are the **{persona.title()}** reviewing archetype defined below. "
        f"Read the role brief carefully and adopt that role, including the operating principles, "
        f"process, tone, and decision labels. You are reviewing a real pull request as "
        f"the {persona.title()} lens.\n\n"
        f"---\n\n{brief}\n\n---\n\n"
        f"{REVIEW_OUTPUT_INSTRUCTION}"
    )
    user = (
        f"Review the following pull request as {persona.title()}. "
        f"Output only the JSON object.\n\n{format_pr_for_review(pr)}"
    )
    return system, user


def build_synthesis_prompt(
    mode: str, passes: dict[str, ReviewOutput]
) -> tuple[str, str]:
    """mode ∈ {dissent, consensus}. passes maps persona -> ReviewOutput."""
    template = (PROMPTS / f"synthesis_{mode}.md").read_text()
    reviewer_section = "\n\n".join(
        f"### Reviewer: {p.title()}\n```json\n{json.dumps(rep.to_json(), indent=2)}\n```"
        for p, rep in passes.items()
    )
    system = (
        "You are the synthesis layer for a code-review crew. "
        "Follow the synthesis instructions below precisely. Output only the JSON object."
    )
    user = f"{template}\n\n{reviewer_section}"
    return system, user


def build_single_agent_prompt(pr: dict[str, Any]) -> tuple[str, str]:
    template = (PROMPTS / "single_agent.md").read_text()
    system = template
    user = (
        f"Review the following pull request. Output only the JSON object.\n\n"
        f"{format_pr_for_review(pr)}"
    )
    return system, user


# ---------- Model calls ----------


def call_anthropic(
    system: str,
    user: str,
    *,
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 4096,
    thinking_budget: int | None = None,
) -> dict[str, Any]:
    """Call the Anthropic API. Returns dict with `text`, `input_tokens`, `output_tokens`."""
    from anthropic import Anthropic

    client = Anthropic()
    kwargs: dict[str, Any] = dict(
        model=model,
        system=system,
        messages=[{"role": "user", "content": user}],
        max_tokens=max_tokens,
    )
    if thinking_budget is not None:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return {
        "text": text,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "model": resp.model,
    }


def call_openai(
    system: str,
    user: str,
    *,
    model: str = "gpt-5.1",
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Call OpenAI for judging. Returns text + token counts."""
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_completion_tokens=max_tokens,
    )
    return {
        "text": resp.choices[0].message.content or "",
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "model": model,
    }


# ---------- JSON extraction ----------

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json(text: str) -> dict[str, Any]:
    """Pull the first JSON object out of model output. Tolerates fenced blocks + leading prose."""
    text = text.strip()
    # Try fenced block first
    m = JSON_BLOCK_RE.search(text)
    if m:
        return json.loads(m.group(1))
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Find first { ... balanced } in the text
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object found in output")
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("unbalanced JSON braces in output")


# ---------- I/O helpers ----------


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def iter_selected_prs(
    pilot: bool = False, run: str | None = None
) -> Iterable[dict[str, Any]]:
    """Iterate the PR records for the given run.

    Pass `run="pilot" | "main" | "full"` (preferred); the legacy `pilot=True`
    arg is kept for backward compatibility with the pilot orchestrator.
    """
    if run is None:
        run = "pilot" if pilot else "full"
    name = {
        "pilot": "prs_pilot.json",
        "main": "prs_main.json",
        "full": "prs.json",
    }.get(run)
    if name is None:
        raise ValueError(f"unknown run: {run!r}")
    p = DATA / name
    return iter(read_json(p))
