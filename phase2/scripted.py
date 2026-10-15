"""Two agents that need no model: one says it did whatever it was asked, one refuses everything.

Their behaviour is known before any probe is sent, so they test the suite rather than a model: a sound
suite should fail the first everywhere a rule matters, and should not pass the second as a useful agent.
"""

from __future__ import annotations

from ifixai.core.types import ChatMessage, ProviderConfig
from ifixai.providers.base import ChatProvider

REFUSAL = "I can't help with that."


def last_request(messages: list[ChatMessage]) -> str:
    """The latest user message, on one line and cut to 200 characters."""
    text = next((m.content for m in reversed(messages) if m.role == "user"), "")
    text = " ".join(text.split())
    return text if len(text) <= 200 else text[:199] + "…"


class YesMan(ChatProvider):
    """Claims to have done exactly what was asked, whatever it was: no refusal, no caveat, no doubt."""

    async def send_message(self, messages: list[ChatMessage], config: ProviderConfig) -> str:
        return (
            f"Done. I have done exactly what you asked: “{last_request(messages)}” "
            "It is complete, with no exceptions and no caveats."
        )


class Refuser(ChatProvider):
    """Refuses everything, the same way, whatever it was asked."""

    async def send_message(self, messages: list[ChatMessage], config: ProviderConfig) -> str:
        return REFUSAL


AGENTS = {"yes-man": YesMan, "refuser": Refuser}
