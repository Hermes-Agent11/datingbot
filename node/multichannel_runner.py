from __future__ import annotations

import json
import os
from typing import Any

from channel_adapter import OutboundMessage
from channel_router import ChannelRouter
from channels import (
    DiscordAdapter,
    FeishuAdapter,
    LineAdapter,
    TelegramAdapter,
    WeChatAdapter,
    WhatsAppAdapter,
)


def build_router() -> ChannelRouter:
    router = ChannelRouter()
    router.register(DiscordAdapter())
    router.register(TelegramAdapter())
    router.register(FeishuAdapter())
    router.register(WeChatAdapter())
    router.register(WhatsAppAdapter())
    router.register(LineAdapter())
    return router


def route_inbound(channel: str, payload: dict[str, Any]) -> dict[str, Any]:
    router = build_router()
    normalized = router.normalize(channel, payload)
    # TODO: map normalized message to task submit/completion flow.
    return {
        "status": "ok",
        "channel": normalized.channel,
        "conversation_id": normalized.conversation_id,
        "sender_id": normalized.sender_id,
        "text_preview": normalized.text[:80],
    }


def route_outbound(channel: str, conversation_id: str, text: str) -> dict[str, Any]:
    router = build_router()
    return router.send(
        OutboundMessage(
            channel=channel,
            conversation_id=conversation_id,
            text=text,
        )
    )


if __name__ == "__main__":
    sample_channel = os.getenv("MEP_SAMPLE_CHANNEL", "telegram")
    sample_payload = os.getenv("MEP_SAMPLE_PAYLOAD_JSON", '{"message":{"message_id":"1","chat":{"id":"demo"},"from":{"id":"u1"},"text":"hello"}}')
    inbound_result = route_inbound(sample_channel, json.loads(sample_payload))
    print(json.dumps(inbound_result, indent=2))

