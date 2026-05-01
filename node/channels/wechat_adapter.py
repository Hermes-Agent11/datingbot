from __future__ import annotations

from typing import Any

from channel_adapter import ChannelAdapter, NormalizedMessage, OutboundMessage


class WeChatAdapter(ChannelAdapter):
    channel_name = "wechat"

    def normalize_inbound(self, payload: dict[str, Any]) -> NormalizedMessage:
        return NormalizedMessage(
            channel=self.channel_name,
            message_id=str(payload.get("MsgId", "")),
            conversation_id=str(payload.get("FromUserName", "")),
            sender_id=str(payload.get("FromUserName", "")),
            sender_display=None,
            text=str(payload.get("Content", "")),
            raw=payload,
        )

    def send_outbound(self, message: OutboundMessage) -> dict[str, Any]:
        # TODO: implement WeChat bot bridge send.
        return {
            "status": "todo",
            "channel": self.channel_name,
            "conversation_id": message.conversation_id,
            "text_preview": message.text[:80],
        }

