"""Run a single persona's blind pass on a PR."""

from __future__ import annotations

import click

from lib import (
    RUNS,
    build_persona_pass_prompt,
    call_anthropic,
    extract_json,
    load_pr_by_task_id,
    write_json,
)


@click.command()
@click.option("--task-id", required=True)
@click.option("--persona", required=True)
@click.option("--run-dir", default="runs/pilot")
@click.option("--model", default="claude-sonnet-4-5")
@click.option("--max-tokens", default=4096, type=int)
def main(task_id: str, persona: str, run_dir: str, model: str, max_tokens: int) -> None:
    pr = load_pr_by_task_id(task_id)
    system, user = build_persona_pass_prompt(persona, pr)
    resp = call_anthropic(system, user, model=model, max_tokens=max_tokens)
    parsed = extract_json(resp["text"])
    out = {
        "persona": persona,
        "task_id": task_id,
        "model": resp["model"],
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
        "review": parsed,
        "raw": resp["text"],
    }
    out_path = (
        RUNS / run_dir.split("runs/")[-1] / task_id / "passes" / f"{persona}.json"
    )
    write_json(out_path, out)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
