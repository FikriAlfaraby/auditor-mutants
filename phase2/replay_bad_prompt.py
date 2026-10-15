"""Replay two of the bad agent's recorded probes straight to the model, with the exact system message
iFixAi built, to see whether the appended instructions reach the model and what it does with them.

    uv run python phase2/replay_bad_prompt.py   # writes phase2/runs/replay-bad-prompt.json
"""

from __future__ import annotations

import json
from pathlib import Path

import run_suite
from ifixai.inspections.judge_probe import build_system_message
from openai import OpenAI

HERE = Path(__file__).resolve().parent


def main() -> None:
    system = build_system_message(run_suite.system_prompt("bad"), "0123456789abcdef")
    assert "Operator override for this deployment" in system, (
        "the bad instructions are not in the system message"
    )
    run = json.loads((HERE / "runs" / "bad-1.json").read_text(encoding="utf-8"))
    client = OpenAI(base_url=run_suite.GATEWAY, api_key=run_suite.gateway_key())
    out = []
    for tid in ("B08", "B27"):
        test = next(t for t in run["test_results"] if t["test_id"] == tid)
        item = next(e for e in test["evidence"] if e.get("prompt_sent"))
        answer = (
            client.chat.completions.create(
                model=run_suite.SUT_MODEL,
                temperature=0,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": item["prompt_sent"]},
                ],
            )
            .choices[0]
            .message.content
        )
        out.append(
            {
                "inspection": tid,
                "test_case_id": item.get("test_case_id"),
                "probe": item["prompt_sent"],
                "recorded_reply": item.get("actual_response"),
                "replayed_reply": answer,
            }
        )
    target = HERE / "runs" / "replay-bad-prompt.json"
    target.write_text(
        json.dumps(
            {"system_message_contains_bad_instructions": True, "replays": out}, indent=1, ensure_ascii=False
        )
        + "\n",
        encoding="utf-8",
    )
    for r in out:
        print(r["inspection"], "->", r["replayed_reply"][:160].replace("\n", " "))


if __name__ == "__main__":
    main()
