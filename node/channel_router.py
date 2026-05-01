from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class ChannelRouter:
    """Routes inbound/outbound messages through registered channel adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, ChannelAdapter] = {}

    def register(self, adapter: ChannelAdapter) -> None:
        self._adapters[adapter.channel_name] = adapter

    def registered_channels(self) -> list[str]:
        return sorted(self._adapters.keys())

    def normalize(self, channel: str, payload: dict[str, Any]) -> NormalizedMessage:
        adapter = self._adapters.get(channel)
        if adapter is None:
            raise KeyError(f"No adapter registered for channel '{channel}'")
        return adapter.normalize_inbound(payload)

    def send(self, message: OutboundMessage) -> dict[str, Any]:
        adapter = self._adapters.get(message.channel)
        if adapter is None:
            raise KeyError(f"No adapter registered for channel '{message.channel}'")
        return adapter.send_outbound(message)

