# Multi-Channel Adapter Skeleton (DatingBot)

This PR adds the first adapter skeleton for IM plugin direction:
- Discord
- Telegram
- Feishu
- WeChat
- WhatsApp
- LINE

## What Is Included
- Shared channel message contracts in `node/channel_adapter.py`
- Adapter router/registry in `node/channel_router.py`
- Per-channel adapter skeletons in `node/channels/`
- Example runner in `node/multichannel_runner.py`

## What Is Not Included Yet
- Real API credentials and webhook verification
- Outbound API calls for each platform
- Mapping to MEP task submit/complete contract
- Channel-specific retry/rate-limit/replay protection

## Next PR Suggestions
1. Implement Telegram and Discord first (best docs and easiest bootstrap)
2. Add unified webhook validation middleware
3. Add message idempotency store (prevent duplicate delivery)
4. Add end-to-end tests for `receive -> normalize -> route -> reply`
5. Add channel-level observability fields (`channel`, `conversation_id`, `message_id`)

