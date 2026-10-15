"""Phase 2: iFixAi's default suite on a customer-support agent that follows its rules, and on the
same agent told to break them.

    uv run python phase2/run_suite.py good 1          # one run of the good agent
    uv run python phase2/run_suite.py bad 1 --only B06  # one inspection, for a smoke test

Both agents are GPT-6 Luna through a local OpenAI-compatible gateway, grounded in iFixAi's built-in
customer_support fixture the way `ifixai run --grounding fixture` does it. The judge is Gemini 3.8 Flash,
one judge from another vendor, as iFixAi's single mode asks. The probe samplers are pinned, so both agents
and every run see the same probes. Telemetry is off: nothing leaves this machine but the model calls.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import time
from pathlib import Path

from ifixai.api import run_selected
from ifixai.core.fixture_loader import load_fixture
from ifixai.core.grounding import GroundingMode, compose_system_prompt
from ifixai.core.types import EvaluationMode, EvaluationPipelineConfig
from ifixai.harness.suites import essential_ids
from ifixai.judge.config import JudgeConfig
from scripted import AGENTS

HERE = Path(__file__).resolve().parent
GATEWAY = "http://127.0.0.1:20128/v1"
SUT_MODEL = "cx/gpt-6-luna"
JUDGE_MODEL = "ag/gemini-3.8-flash"
FIXTURE = "customer_support"
SEEDS = {
    "b12_seed": 1201,
    "b14_seed": 1401,
    "b28_seed": 2801,
    "b29_seed": 2901,
    "b30_seed": 3001,
    "b32_seed": 3201,
}
JUDGE_BUDGET = 1000  # above the dry run's estimate of 100 judge calls, so no item is skipped for budget
# Appended after the fixture's own policy prompt. Each line targets what one of the default inspections
# says it measures, so a sound suite should score this agent far below the good one.
BAD = (HERE / "bad-instructions.txt").read_text(encoding="utf-8").strip()


def gateway_key() -> str:
    """Read at run time from the local gateway's config; never printed or written."""
    text = (Path.home() / ".omp" / "agent" / "models.yml").read_text(encoding="utf-8")
    match = re.search(r"9router:\s*\n\s*baseUrl:.*\n\s*api:.*\n\s*apiKey:\s*(\S+)", text)
    if not match:
        raise SystemExit("no 9router key in ~/.omp/agent/models.yml")
    return match.group(1).strip("'\"")


def system_prompt(agent: str) -> str:
    fixture = load_fixture(FIXTURE)
    return compose_system_prompt(GroundingMode.FIXTURE, fixture, BAD if agent == "bad" else None)


async def run(agent: str, number: int, only: list[str] | None) -> Path:
    key = gateway_key()
    tests = set(only) if only else set(essential_ids())
    pipeline = EvaluationPipelineConfig(
        mode=EvaluationMode.SINGLE,
        judge_max_calls=JUDGE_BUDGET,
        **SEEDS,
        **{f"{name}_pinned": True for name in SEEDS},
    )
    judge = JudgeConfig(
        provider="openai",
        model=JUDGE_MODEL,
        endpoint=GATEWAY,
        api_key=key,
        temperature=0.0,
        max_calls_per_run=JUDGE_BUDGET,
        timeout=120,
    )
    started = time.time()
    if agent in AGENTS:  # a scripted agent: no model and no key; it ignores the grounding it is sent
        sut = {"provider": AGENTS[agent](), "system_name": agent}
    else:
        sut = {
            "provider": "openai",
            "api_key": key,
            "endpoint": GATEWAY,
            "model": SUT_MODEL,
            "system_name": f"luna-{agent}",
        }
    result = await run_selected(
        tests,
        fixture=FIXTURE,
        system_prompt=system_prompt(agent),
        system_version=str(number),
        timeout=120,
        pipeline_config=pipeline,
        judge_config=judge,
        sut_temperature=0.0,
        **sut,
    )
    out = HERE / "runs" / f"{agent}-{number}{'-' + '-'.join(sorted(only)) if only else ''}.json"
    out.parent.mkdir(exist_ok=True)
    text = result.model_dump_json(indent=1)
    if key in text:
        raise SystemExit("the gateway key appears in the result; not writing it")
    out.write_text(text + "\n", encoding="utf-8")
    print(
        f"{out.relative_to(HERE.parent)}: overall {result.overall_score}, grade {result.grade}, "
        f"{time.time() - started:.0f}s"
    )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("agent", choices=["good", "bad", *AGENTS])
    parser.add_argument("number", type=int)
    parser.add_argument("--only", action="append", help="run these inspection IDs only")
    args = parser.parse_args()
    # iFixAi's telemetry reads these when it would send; its CLI sends, this API path does not. Off anyway.
    os.environ.update({"DO_NOT_TRACK": "1", "IFIXAI_TELEMETRY": "0", "IFIXAI_NO_PROMO": "1"})
    asyncio.run(run(args.agent, args.number, args.only))


if __name__ == "__main__":
    main()
