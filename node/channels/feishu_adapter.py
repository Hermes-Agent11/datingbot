from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class FeishuAdapter(ChannelAdapter):
    channel_name = "feishu"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        event = payload.get("event", payload)
        sender = event.get("sender", {})
        message = event.get("message", {})
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(message.get("message_id", "")),
            conversation_id=str(message.get("chat_id", "")),
            sender_id=str(sender.get("sender_id", {}).get("open_id", "")),
            sender_display=sender.get("sender_type"),
            text=str(event.get("text", message.get("content", ""))),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement Feishu send API call.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

