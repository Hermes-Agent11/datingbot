"""
honcho_memory.py — Honcho Local Memory integration for MEP listeners.

Provides session-aware memory for MEP DM conversations.
Each agent stores/retrieves messages via Honcho, forming
a persistent context across DM exchanges.

Usage:
    from honcho_memory import HonchoMemory
    
    mem = HonchoMemory(peer_id="hermes", session_id="mep_dm_chat")
    mem.save_message(peer_id="moltbot", content="Hello!", role="user")
    ctx = mem.get_context()  # Returns last N messages as context string
"""

import requests
import json
import os
from typing import Optional

HONCHO_BASE = "http://127.0.0.1:8000/v3"
WORKSPACE = "default"
DEFAULT_MAX_CONTEXT = 10  # Max messages to include in context


class HonchoMemory:
    """Persistent session memory for MEP DM conversations via Honcho."""

    def __init__(
        self,
        peer_id: str = "hermes",
        session_id: str = "mep_dm_chat",
        max_context: int = DEFAULT_MAX_CONTEXT,
    ):
        self.peer_id = peer_id
        self.session_id = session_id
        self.max_context = max_context
        self._session_ok = True

    def _ensure_session(self) -> bool:
        """Ensure the session exists on Honcho."""
        try:
            r = requests.post(
                f"{HONCHO_BASE}/workspaces/{WORKSPACE}/sessions",
                json={"id": self.session_id},
                timeout=5,
            )
            if r.status_code == 200:
                return True
            return False
        except Exception as e:
            print(f"[Honcho] ensure_session error: {e}", flush=True)
            return False

    def save_message(
        self,
        peer_id: str,
        content: str,
        role: str = "assistant",
        metadata: Optional[dict] = None,
    ) -> dict | None:
        """Store a message in the current session."""
        self._ensure_session()
        payload = {
            "peer_id": peer_id,
            "content": content,
            "role": role,
        }
        if metadata:
            payload["metadata"] = metadata
        try:
            r = requests.post(
                f"{HONCHO_BASE}/workspaces/{WORKSPACE}/sessions/{self.session_id}/messages",
                json=payload,
                timeout=5,
            )
            if r.status_code == 200:
                return r.json()
            print(f"[Honcho] save_message error: {r.status_code} {r.text[:200]}", flush=True)
            return None
        except Exception as e:
            print(f"[Honcho] save_message exception: {e}", flush=True)
            return None

    def get_messages(self, limit: Optional[int] = None) -> list[dict]:
        """Retrieve recent messages from the session, newest first."""
        limit = limit or self.max_context
        try:
            r = requests.post(
                f"{HONCHO_BASE}/workspaces/{WORKSPACE}/sessions/{self.session_id}/messages/list",
                json={},
                timeout=5,
            )
            if r.status_code == 200:
                data = r.json()
                items = data.get("items", [])
                # Return newest N first
                return items[:limit]
            print(f"[Honcho] get_messages error: {r.status_code}", flush=True)
            return []
        except Exception as e:
            print(f"[Honcho] get_messages exception: {e}", flush=True)
            return []

    def get_context(self, limit: Optional[int] = None) -> str:
        """
        Build a context string from recent conversation history.
        Returns messages oldest-first, formatted for injection into an AI prompt.
        """
        limit = limit or self.max_context
        messages = self.get_messages(limit=limit * 2)  # Get more to reverse

        if not messages:
            return ""

        # Reverse so oldest is first (chronological order for context)
        messages.reverse()

        # Take only the most recent N
        recent = messages[-limit:]

        parts = ["# Previous conversation context (via Honcho):\n"]
        for m in recent:
            peer = m.get("peer_id", "unknown")
            content = m.get("content", "")
            timestamp = m.get("created_at", "")[:19].replace("T", " ")
            parts.append(f"[{timestamp}] {peer}: {content}")

        return "\n".join(parts)

    def search(self, query: str) -> str:
        """Search memory for relevant context by keyword."""
        messages = self.get_messages(limit=100)
        relevant = [m for m in messages if query.lower() in m.get("content", "").lower()]
        if not relevant:
            return ""

        relevant.reverse()
        parts = ["# Relevant memory:\n"]
        for m in relevant:
            peer = m.get("peer_id", "unknown")
            content = m.get("content", "")
            parts.append(f"[{peer}]: {content}")

        return "\n".join(parts) + "\n"
