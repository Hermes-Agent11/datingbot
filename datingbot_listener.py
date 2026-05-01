#!/usr/bin/env python3
"""DatingBot MEP Listener — handles dating profiles, matching, and conversations."""
import asyncio, json, requests, sys, os, urllib.parse, websockets, time, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "node"))
from node.identity import MEPIdentity
from match_engine import MatchEngine
from profile_schema import validate_profile

HUB_HTTP = "https://mep-hub.silentcopilot.ai"
HUB_WS = "wss://mep-hub.silentcopilot.ai"
KEY_PATH = os.path.expanduser("~/.hermes/datingbot_mep_node.pem")
LOG_FILE = "/tmp/datingbot.log"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def auth_headers(payload: str) -> dict:
    return {"Content-Type": "application/json", **identity.get_auth_headers(payload)}

match_engine = MatchEngine()

async def handle_task(data: dict):
    task_id = data.get("id")
    payload = data.get("payload", "")
    sender = data.get("consumer_id", "unknown")
    log(f"📩 Task {task_id} from {sender}: {payload[:200]}")
    
    try:
        req = json.loads(payload)
    except:
        req = {"type": "unknown", "data": payload}
    
    task_type = req.get("type", req.get("task_type", "chat"))
    result = {"status": "error", "message": "Unknown task type"}
    
    if task_type == "register_profile":
        profile = req.get("profile", {})
        valid, msg = validate_profile(profile)
        if valid:
            profile["mep_node_id"] = sender
            match_engine.store_profile(sender, profile)
            result = {"status": "ok", "message": f"Profile registered for {profile.get('name')}"}
        else:
            result = {"status": "error", "message": msg}
    
    elif task_type == "find_match":
        profile = match_engine.get_profile(sender)
        if not profile:
            result = {"status": "error", "message": "Register a profile first via register_profile"}
        else:
            top_n = req.get("top_n", 5)
            matches = match_engine.find_matches(sender, top_n)
            result = {"status": "ok", "matches": matches}
    
    elif task_type == "send_message":
        target = req.get("target_node")
        message = req.get("message", "")
        if target and message:
            forward = json.dumps({"consumer_id": identity.node_id, "payload": json.dumps({"type": "chat", "from": sender, "message": message}), "bounty": 0.0, "target_node": target})
            headers = auth_headers(forward)
            headers["Content-Type"] = "application/json"
            r = requests.post(f"{HUB_HTTP}/tasks/submit", params={"provider_id": target}, data=forward, headers=headers, timeout=10)
            result = {"status": "ok" if r.status_code == 200 else "error", "message": f"Message sent: HTTP {r.status_code}"}
        else:
            result = {"status": "error", "message": "Need target_node and message"}
    
    elif task_type == "get_profile":
        target = req.get("target_node", sender)
        profile = match_engine.get_profile(target)
        result = {"status": "ok", "profile": profile} if profile else {"status": "error", "message": "Profile not found"}
    
    else:
        # chat/default fallback — always completes
        result = {"status": "ok", "reply": "❤️ DatingBot received your message. Use task_type: register_profile to set up your profile, or find_match to find matches."}
    
    # ALL task types reach this completion call
    try:
        cp = json.dumps({"task_id": task_id, "provider_id": identity.node_id, "result_payload": json.dumps(result)})
        r = requests.post(f"{HUB_HTTP}/tasks/complete", headers=auth_headers(cp), data=cp, timeout=10)
        log(f"✅ Completed {task_id[:8]}: HTTP {r.status_code}")
    except Exception as e:
        log(f"❌ Complete failed: {e}")

async def listen():
    retry_delay = 1
    max_delay = 60
    while True:
        try:
            ts = str(int(time.time()))
            sig = identity.sign(identity.node_id, ts)
            uri = f"{HUB_WS}/ws/{identity.node_id}?timestamp={ts}&signature={urllib.parse.quote(sig)}"
            log(f"Connecting (retry_delay={retry_delay}s)...")
            async with websockets.connect(uri, ping_interval=20) as ws:
                log(f"✅ Connected as {identity.node_id}")
                retry_delay = 1  # Reset on successful connect
                async def hb():
                    while True:
                        await asyncio.sleep(30)
                        try:
                            body = json.dumps({"availability": "online"})
                            requests.post(f"{HUB_HTTP}/registry/heartbeat", headers=auth_headers(body), data=body, timeout=5)
                        except:
                            pass
                asyncio.create_task(hb())
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    event = data.get("event", "")
                    edata = data.get("data", {})
                    if event == "new_task":
                        asyncio.create_task(handle_task(edata))
        except websockets.exceptions.ConnectionClosed as e:
            log(f"⚠️ ConnectionClosed: {e}")
        except asyncio.TimeoutError as e:
            log(f"⚠️ Timeout: {e}")
        except Exception as e:
            log(f"⚠️ Reconnect: {type(e).__name__}: {e}")
        # Exponential backoff with jitter, capped at max_delay
        await asyncio.sleep(retry_delay + random.uniform(0, 1))
        retry_delay = min(retry_delay * 2, max_delay)

if __name__ == "__main__":
    if not os.path.exists(KEY_PATH):
        log("Key not found. Create one via: python3 -c \"from node.identity import MEPIdentity; MEPIdentity(key_path='{KEY_PATH}')\"")
        sys.exit(1)
    identity = MEPIdentity(key_path=KEY_PATH)
    log(f"DatingBot starting as {identity.node_id}")
    try:
        r = requests.post(f"{HUB_HTTP}/register", json={"pubkey": identity.pub_pem}, timeout=10)
        reg = r.json()
        log(f"Registered: {reg}")
        body = json.dumps({"alias": "DatingBot", "availability": "online"})
        requests.post(f"{HUB_HTTP}/registry/update", data=body, headers=auth_headers(body), timeout=10)
    except Exception as e:
        log(f"Register: {e}")
    asyncio.run(listen())
