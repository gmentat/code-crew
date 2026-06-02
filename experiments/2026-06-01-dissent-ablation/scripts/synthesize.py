"""Run synthesis on a PR's persona passes. --mode {dissent,consensus}."""

from __future__ import annotations


import click

from lib import (
    PERSONAS,
    RUNS,
    ReviewOutput,
    build_synthesis_prompt,
    call_anthropic,
    extract_json,
    read_json,
    write_json,
)


@click.command()
@click.option("--task-id", required=True)
@click.option("--mode", type=click.Choice(["dissent", "consensus"]), required=True)
@click.option("--run-dir", default="runs/pilot")
@click.option("--model", default="claude-sonnet-4-5")
@click.option("--max-tokens", default=6000, type=int)
def main(task_id: str, mode: str, run_dir: str, model: str, max_tokens: int) -> None:
    base = RUNS / run_dir.split("runs/")[-1] / task_id
    passes = {}
    for p in PERSONAS:
        rec = read_json(base / "passes" / f"{p}.json")
        passes[p] = ReviewOutput.from_json(rec["review"])
    system, user = build_synthesis_prompt(mode, passes)
    resp = call_anthropic(system, user, model=model, max_tokens=max_tokens)
    parsed = extract_json(resp["text"])
    out = {
        "task_id": task_id,
        "mode": mode,
        "model": resp["model"],
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
        "synthesis": parsed,
        "raw": resp["text"],
    }
    out_path = base / "syntheses" / f"{mode}.json"
    write_json(out_path, out)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
