from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class WhatsAppAdapter(ChannelAdapter):
    channel_name = "whatsapp"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        entry = (payload.get("entry") or [{}])[0]
        change = (entry.get("changes") or [{}])[0]
        value = change.get("value", {})
        message = (value.get("messages") or [{}])[0]
        contact = (value.get("contacts") or [{}])[0]
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(message.get("id", "")),
            conversation_id=str(value.get("metadata", {}).get("phone_number_id", "")),
            sender_id=str(message.get("from", "")),
            sender_display=contact.get("profile", {}).get("name"),
            text=str(message.get("text", {}).get("body", "")),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement WhatsApp Business API send.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

