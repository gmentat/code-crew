"""Single-agent baseline. --variant {budget,naive}; --budget overrides max_tokens for the budget variant."""

from __future__ import annotations

import click

from lib import (
    RUNS,
    build_single_agent_prompt,
    call_anthropic,
    extract_json,
    load_pr_by_task_id,
    write_json,
)


@click.command()
@click.option("--task-id", required=True)
@click.option("--variant", type=click.Choice(["budget", "naive"]), required=True)
@click.option("--run-dir", default="runs/pilot")
@click.option("--model", default="claude-sonnet-4-5")
@click.option(
    "--budget", default=8000, type=int, help="Max tokens for --variant budget."
)
def main(task_id: str, variant: str, run_dir: str, model: str, budget: int) -> None:
    pr = load_pr_by_task_id(task_id)
    system, user = build_single_agent_prompt(pr)
    if variant == "budget":
        # Budget-matched: extended thinking with a cap derived from the realized crew median
        resp = call_anthropic(
            system,
            user,
            model=model,
            max_tokens=budget,
            thinking_budget=max(1024, budget // 2),
        )
    else:
        # Naive: no extended thinking, smaller token budget, floor sanity check
        resp = call_anthropic(system, user, model=model, max_tokens=2048)
    parsed = extract_json(resp["text"])
    out = {
        "task_id": task_id,
        "variant": variant,
        "model": resp["model"],
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
        "review": parsed,
        "raw": resp["text"],
    }
    out_path = RUNS / run_dir.split("runs/")[-1] / task_id / f"single_{variant}.json"
    write_json(out_path, out)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
