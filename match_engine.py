# Match engine using Honcho local memory
# Profiles stored as Honcho memory entries
# Matching: interest overlap (Jaccard similarity) + age range compatibility
# Returns top N matches sorted by compatibility score

import json, math, sys
sys.path.insert(0, "/home/wuyanbingep/.hermes")
from honcho_memory import HonchoMemory

class MatchEngine:
    def __init__(self):
        self.db = HonchoMemory(peer_id="datingbot", session_id="matchmaking")
    
    def store_profile(self, node_id: str, profile: dict):
        self.db.save_message(peer_id=node_id, content=json.dumps(profile), role="user", metadata={"type": "profile"})
    
    def get_profile(self, node_id: str) -> dict | None:
        entries = self.db.get_session_messages(limit=100)
        for e in entries:
            if e.get("peer_id") == node_id:
                try: return json.loads(e["content"])
                except: pass
        return None
    
    def compute_compatibility(self, p1: dict, p2: dict) -> float:
        interests1 = set(i.lower().strip() for i in p1.get("interests", []))
        interests2 = set(i.lower().strip() for i in p2.get("interests", []))
        if not interests1 or not interests2:
            return 0.0
        overlap = len(interests1 & interests2)
        union = len(interests1 | interests2)
        return overlap / union if union > 0 else 0.0
    
    def find_matches(self, node_id: str, top_n: int = 5) -> list:
        profile = self.get_profile(node_id)
        if not profile:
            return []
        entries = self.db.get_session_messages(limit=500)
        candidates = {}
        for e in entries:
            nid = e.get("peer_id")
            if nid == node_id:
                continue
            try:
                p = json.loads(e["content"])
                score = self.compute_compatibility(profile, p)
                candidates[nid] = {"profile": p, "score": round(score, 3)}
            except:
                pass
        sorted_matches = sorted(candidates.items(), key=lambda x: x[1]["score"], reverse=True)
        return [{"node_id": nid, **data} for nid, data in sorted_matches[:top_n] if data["score"] > 0]
