from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizedMessage:
    channel: str
    message_id: str
    conversation_id: str
    sender_id: str
    sender_display: str | None
    text: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OutboundMessage:
    channel: str
    conversation_id: str
    text: str
    reply_to_message_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ChannelAdapter:
    """Base interface for all IM channel connectors."""

    channel_name: str = "unknown"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        raise NotImplementedError

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        raise NotImplementedError

