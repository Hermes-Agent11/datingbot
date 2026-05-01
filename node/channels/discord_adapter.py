from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class DiscordAdapter(ChannelAdapter):
    channel_name = "discord"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        data = payload.get("data", payload)
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(data.get("id", "")),
            conversation_id=str(data.get("channel_id", "")),
            sender_id=str(data.get("author_id", "")),
            sender_display=data.get("author_name"),
            text=str(data.get("content", "")),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement Discord send API/webhook call.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

