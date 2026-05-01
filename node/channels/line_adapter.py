from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class LineAdapter(ChannelAdapter):
    channel_name = "line"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        event = (payload.get("events") or [{}])[0]
        source = event.get("source", {})
        message = event.get("message", {})
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(message.get("id", "")),
            conversation_id=str(source.get("groupId") or source.get("roomId") or source.get("userId", "")),
            sender_id=str(source.get("userId", "")),
            sender_display=None,
            text=str(message.get("text", "")),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement LINE Messaging API send.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

