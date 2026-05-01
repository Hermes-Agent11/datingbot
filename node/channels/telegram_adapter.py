from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class TelegramAdapter(ChannelAdapter):
    channel_name = "telegram"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        msg = payload.get("message", payload)
        chat = msg.get("chat", {})
        sender = msg.get("from", {})
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(msg.get("message_id", "")),
            conversation_id=str(chat.get("id", "")),
            sender_id=str(sender.get("id", "")),
            sender_display=sender.get("username") or sender.get("first_name"),
            text=str(msg.get("text", "")),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement Telegram Bot API call.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

