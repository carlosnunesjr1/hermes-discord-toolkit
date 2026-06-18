# Option B Gateway Integration Gap — 2026-06-16

## Critical Finding: Missing `/v1/discord/interaction` Endpoint

### Problem
The Discord Gateway Bot (`hermes-discord-bot`, systemd service) uses `gateway_client.py` to forward Discord interactions to Hermes Gateway via `POST /v1/discord/interaction`. **This endpoint returns 404 NOT FOUND.**

### Evidence
```bash
# Bot logs show repeated 404 errors:
2026-06-16 23:18:54,915 [ERROR] gateway_client: Gateway error 404: 404: Not Found
2026-06-16 23:21:17,957 [ERROR] gateway_client: Gateway error 404: 404: Not Found
2026-06-16 23:23:51,564 [ERROR] gateway_client: Gateway error 404: 404: Not Found
```

### Root Cause
Hermes Gateway's Discord platform adapter (`gateway/platforms/discord/adapter.py`) registers:
- WebSocket gateway connection for real-time events
- Slash command registration via Discord HTTP API

But does **NOT** expose an HTTP endpoint for external Discord bots to forward interactions.

### Current Architecture (Broken Path)
```text
Discord Bot (WS) ──forward_interaction()──► POST /v1/discord/interaction ──► 404 NOT FOUND
```

### Validated Workaround (Immediate)
The Discord bot's `gateway_client.py` should call existing Hermes Gateway endpoints:

```python
# In gateway_client.py - replace forward_interaction():
async def forward_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Forward Discord interaction to Hermes Gateway via existing endpoints."""
    # Option A: Spawn agent directly (works now)
    return await self.spawn_agent(
        goal=payload.get("message", ""),
        context=f"Discord interaction from user {payload.get('user_id')} in channel {payload.get('channel_id')}",
        toolsets=["terminal", "file", "web", "browser", "coding"]
    )
    
    # Option B: Use /v1/agent/chat if implemented
    # return await self._request("POST", "/v1/agent/chat", json_data={
    #     "session_id": payload.get("thread_id"),
    #     "message": payload.get("message"),
    #     "metadata": {"platform": "discord", "user_id": payload.get("user_id")}
    # })
```

### Required Gateway Fix (Long-term)
Add endpoint in Hermes Gateway Discord adapter or API server:

```python
# In gateway/platforms/discord/adapter.py or gateway/platforms/api_server.py
@router.post("/v1/discord/interaction")
async def handle_discord_interaction(request: Request):
    """Receive forwarded Discord interactions from Gateway Bot."""
    payload = await request.json()
    # Extract: user_id, channel_id, thread_id, message, guild_id, interaction_type
    # Route to appropriate Hermes session based on thread_id / channel_id
    # Return response formatted for Discord bot to send back via WS
    
    # Expected response format:
    # {
    #     "type": "response",
    #     "content": "Agent response text",
    #     "thread_id": "...",
    #     "session_id": "..."
    # }
```

### Verification Checklist
- [ ] Gateway Bot process running: `systemctl status hermes-discord-bot`
- [ ] Discord slash commands synced to guild (13 commands visible in Discord)
- [ ] DM/mention handling works (bot logs show "DM from..." / "Mention from...")
- [ ] Gateway health: `curl -H "Authorization: Bearer *** https://api.menusummo.com.br/v1/health`
- [ ] **Current gap:** Bot logs show "Gateway error 404: 404: Not Found" on every interaction

### Architecture Decision
Both paths now active in production:
- **Inbound Webhook** → Hermes Gateway (8644) → Agent → Discord Channel Webhook URL (outbound) — **WORKING**
- **Gateway Bot (WS)** → Real-time events/slash commands → Hermes Gateway (8642) — **BROKEN: 404 on /v1/discord/interaction**

### Systemd Service Conflict (Also Found This Session)
Two `hermes-gateway` services on same port 8642:
- `hermes-gateway.service` (system, `/etc/systemd/system/`) — **CONFLICTING, DISABLE**
- `hermes-gateway.service` (user, `~/.config/systemd/user/`) — **CORRECT, ACTIVE**

```bash
# Fix applied:
sudo systemctl disable --now hermes-gateway
sudo systemctl daemon-reload
systemctl --user daemon-reload
```

### Related References
- `references/option-b-implementation.md` — Complete Option B deployment
- `references/ARCHITECTURE.md` — Architecture decisions
- `cn-tech-ecosystem-ops/references/2026-06-16-operational-state-audit.md` — Full operational state