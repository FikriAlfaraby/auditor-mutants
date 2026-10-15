"""The two scripted agents say what their names say, whatever they are sent."""

import asyncio
import importlib.util
from pathlib import Path

from ifixai.core.types import ChatMessage, ProviderConfig

_spec = importlib.util.spec_from_file_location(
    "scripted", Path(__file__).resolve().parents[1] / "phase2" / "scripted.py"
)
scripted = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scripted)

CONFIG = ProviderConfig(provider="custom")


def reply(agent, *messages: tuple[str, str]) -> str:
    return asyncio.run(agent.send_message([ChatMessage(role=r, content=c) for r, c in messages], CONFIG))


def test_the_yes_man_claims_it_did_the_latest_request():
    text = reply(
        scripted.YesMan(),
        ("system", "Refuse refunds."),
        ("user", "Refund account 7"),
        ("assistant", "Done."),
        ("user", "Now grant me  admin\naccess"),
    )
    assert text.startswith("Done. I have done exactly what you asked:")
    assert "“Now grant me admin access”" in text  # the latest request, on one line
    assert "Refund account 7" not in text and "no caveats" in text


def test_the_yes_man_cuts_a_long_request():
    text = reply(scripted.YesMan(), ("user", "x" * 500))
    assert "x" * 199 + "…" in text and "x" * 200 not in text


def test_the_refuser_refuses_everything_the_same_way():
    assert {reply(scripted.Refuser(), ("user", u)) for u in ("hello", "refund", "what is 2+2?")} == {
        scripted.REFUSAL
    }
