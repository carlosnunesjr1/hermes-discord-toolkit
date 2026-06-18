# Gateway Integration Workaround — Discord Bot → Hermes Gateway

## Problem
The Discord Gateway Bot (`hermes-discord-bot`) forwards interactions to Hermes Gateway via `POST /v1/discord/interaction`, but **this endpoint does not exist** in Hermes Gateway — returns 404.

---

## Root Cause
Hermes Gateway's Discord platform adapter (`gateway/platforms/discord/adapter.py`) registers WebSocket gateway connection and slash commands, but does NOT expose an HTTP endpoint for the external Discord bot to forward interactions.

---

## Architecture (Broken Path)
```
Discord Bot (WS) ──forward_interaction()──► POST /v1/discord/interaction ──► 404 NOT FOUND
```

---

## Validated Workaround (Immediate)

### Bot Side: Use Existing Hermes Endpoints
In `gateway_client.py`:

```python
async def forward_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route Discord interaction to working Hermes Gateway endpoint."""
    # Extract message content
    content = payload.get("content", "")
    if not content:
        content = payload.get("message", "")
    
    # Use agent spawn endpoint (WORKS)
    return await self.spawn_agent(
        goal=content,
        context=f"Discord interaction from user {payload.get('user_id')} in channel {payload.get('channel_id')}",
        toolsets=[
            "terminal", "file", "web", "browser", "coding", 
            "skills", "cronjob", "memory", "delegation"
        ]
    )

# Alternative: Use agent chat if available
# return await self._request("POST", "/v1/agent/chat", json_data={...})
```

### Spawn Agent Implementation (already working)
```python
async def spawn_agent(
    self,
    goal: str,
    context: str = "",
    toolsets: Optional[List[str]] = None
) -> Dict[str, Any]:
    payload = {
        "goal": goal,
        "context": context,
        "toolsets": toolsets or ["terminal", "file", "web", "skills", "cronjob"]
    }
    return await self._request("POST", "/v1/agents/spawn", json=payload)
```

---

## Required Gateway Fix (Long-term)

### Add Missing Endpoint in Hermes Gateway
**Location**: `gateway/platforms/discord/adapter.py` or `hermes_cli/web_server.py`

```python
# In Discord adapter or API server
@router.post("/v1/discord/interaction")
async def handle_discord_interaction(request: Request):
    """Receive forwarded Discord interactions from Gateway Bot."""
    payload = await request.json()
    
    # Extract context
    user_id = payload.get("user_id")
    channel_id = payload.get("channel_id")
    thread_id = payload.get("thread_id")
    message = payload.get("content") or payload.get("message", "")
    
    # Determine Hermes session
    session_id = payload.get("session_id")
    if not session_id and thread_id:
        # Lookup session from thread mapping
        session_id = await get_session_for_thread(thread_id)
    
    # Build Hermes event
    event = MessageEvent(
        text=message,
        message_type=MessageType.TEXT,
        source=build_source(
            chat_id=f"discord:{channel_id}",
            chat_name=f"discord-thread-{thread_id}" if thread_id else f"discord-{channel_id}",
            chat_type="thread" if thread_id else "channel",
            user_id=str(user_id),
            user_name=payload.get("username", "Discord User"),
        ),
        raw_message=payload,
    )
    
    # Process through Hermes (async, non-blocking)
    task = asyncio.create_task(handle_message(event))
    
    return {
        "status": "accepted",
        "session_id": session_id,
        "thread_id": thread_id
    }
```

### Session Mapping Helper
```python
# In thread_manager or gateway registry
async def get_session_for_thread(thread_id: int) -> Optional[str]:
    """Map Discord thread_id to Hermes session_id."""
    session = thread_manager.get_session(thread_id)
    return session.hermes_session_id if session else None
```

---

## Current Working Flow (with Workaround)

```
┌─────────────────┐     WS/Gateway      ┌──────────────────────┐
│   Discord       │ ◄─────────────────► │ hermes-discord-bot   │
│   (Guild)       │   Events/Commands   │ (discord.py, systemd)│
└─────────────────┘                     └──────────┬───────────┘
                                                   │ HTTP localhost:8642
                                                   ▼                                    ┌──────────────────────┐
                                            ┌──────────────────┐ │ Hermes Gateway:8642  │
                                            │ POST /v1/agents/ │ │ (your control plane) │
                                            │     spawn        │ └──────────────────────┘
                                            └──────────────────┘
```

---

## Verification Checklist
- [ ] Gateway Bot process running: `systemctl status hermes-discord-bot`
- [ ] Discord slash commands synced to guild
- [ ] DM/mention handling works (logs show "DM from..." / "Mention from...")
- [ ] Gateway health: `curl -H "Authorization: Bearer $KEY" http://localhost:8642/v1/health`
- [ ] Agent spawn works: `curl -X POST http://localhost:8642/v1/agents/spawn -d '{"goal":"test"}'`
- [ ] **Current gap:** Bot logs show "Gateway error 404: 404: Not Found" on every interaction without workaround

---

## Files Modified for Workaround
| File | Change |
|------|--------|
| `/home/carlos/hermes-discord-bot/gateway_client.py` | `forward_interaction()` → calls `spawn_agent()` |
| `/home/carlos/hermes-discord-bot/bot.py` | `_handle_dm()`, `_handle_mention()`, `_handle_thread_message()` use `gateway.forward_interaction()` |

---

## Testing the Workaround
```bash
# Test agent spawn directly
curl -X POST http://localhost:8642/v1/agents/spawn \
  -H "Authorization: Bearer hermes-api-key-dev-2026" \
  -H "Content-Type: application/json" \
  -d '{"goal":"Say hello from Hermes", "toolsets":["terminal"]}'

# Test via bot (in Discord DM)
@Hermes diga olá

# Should work without 404 error
```

---

## Related Files
| File | Purpose |
|------|---------|
| `/home/carlos/hermes-discord-bot/gateway_client.py:185` | `forward_interaction()` workaround |
| `/home/carlos/hermes-discord-bot/gateway_client.py:65` | `spawn_agent()` implementation |
| `/usr/local/lib/hermes-agent/gateway/platforms/discord/adapter.py` | Missing endpoint location |
| `/usr/local/lib/hermes-agent/hermes_cli/web_server.py` | API server (add endpoint here) |

---

## Priority
**P1** - Add proper `/v1/discord/interaction` endpoint to Hermes Gateway for clean architecture.