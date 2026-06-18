# Webhook Configuration Details (Session 2026-06-16)

## Config Structure (config.yaml)

```yaml
platforms:
  webhook:
    enabled: true
    port: 8644
    secret: "webhook-secret-2026"  # Global fallback secret
    extra:
      routes:
        discord:
          secret: "discord-webhook-secret-2026"  # Per-route secret (REQUIRED)
          prompt: |
            Mensagem recebida do Discord:
            Usuário: {{author.username}} ({{author.id}})
            Canal: {{channel_id}}
            Conteúdo: {{content}}
            
            Responda naturalmente como Hermes. Se for comando técnico, execute.
          skills: []
          deliver: "discord"  # or "webhook" with Discord Webhook URL
          deliver_extra:
            channel_id: "1516397585701666962"
```

## Key Points

1. **Routes live under `extra.routes`** — NOT at top-level `webhook.routes`
2. **Each route REQUIRES a `secret`** — either per-route or global fallback
3. **Discord webhook signature**: Uses `X-Webhook-Signature` header with HMAC-SHA256 hex digest
4. **Test signature**:
   ```python
   import hmac, hashlib
   secret = "discord-webhook-secret-2026"
   body = b'{"content":"test"}'
   sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
   # Header: X-Webhook-Signature: <sig>
   ```

## Current Route Test (Working)

```bash
curl -s http://localhost:8644/webhooks/discord \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: 9b23dff99a8fb4eb3a50719ba591a93bfb14b139dde31733d6afad355e9375eb" \
  -d '{"content":"test"}'
# Returns: {"status":"accepted","route":"discord","event":"unknown","delivery_id":"..."}
```

## Outbound to Discord (Without Gateway Bot)

Since we don't have the Discord Gateway Bot (Option B) running yet, outbound requires:

1. **Create Discord Channel Webhook**:
   - Server Settings → Integrations → Webhooks → New Webhook
   - Select target channel (e.g., #geral)
   - Copy Webhook URL: `https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN`

2. **Update route to use webhook delivery**:
   ```yaml
   deliver: "webhook"
   deliver_extra:
     url: "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN"
     # Optional: username, avatar_url, etc.
   ```

## Discord Developer Portal - Option B Checklist

### Application Setup
- [ ] Create Application: https://discord.com/developers/applications
- [ ] Name: "Hermes Agent" (or preferred)

### Bot Configuration
- [ ] Bot tab → **Reset Token** → Save as `DISCORD_BOT_TOKEN`
- [ ] **Privileged Gateway Intents** → Enable ALL:
  - [ ] Message Content Intent
  - [ ] Server Messages Intent
  - [ ] Guild Members Intent (optional but recommended)
- [ ] Save Changes

### OAuth2 Scopes & Permissions
- [ ] OAuth2 → URL Generator → Scopes: `bot` + `applications.commands`
- [ ] Bot Permissions (calculated integer or checkbox):
  - [ ] Manage Channels (0x10)
  - [ ] Manage Threads (0x80000000000)
  - [ ] Send Messages (0x800)
  - [ ] Send Messages in Threads (0x800000000000)
  - [ ] Embed Links (0x4000)
  - [ ] Read Message History (0x10000)
  - [ ] Use Slash Commands (0x2000000000)
  - [ ] Add Reactions (0x40)
  - [ ] Manage Messages (0x2000) — optional

### IDs to Collect
| ID | Location |
|----|----------|
| `DISCORD_APP_ID` | General Information → Application ID |
| `DISCORD_GUILD_ID` | Discord (Dev Mode ON) → Right-click server → Copy ID |

### Install Bot to Server
- [ ] Use OAuth2 URL with scopes above → Authorize in target server
- [ ] Verify bot appears in server member list

## Integration Architecture (Option B)

```
┌─────────────┐     WebSocket/Gateway      ┌──────────────────────┐
│   Discord   │ ◄─────────────────────────► │ hermes-discord-bot   │
│   (Guild)   │   Events + Slash Commands   │ (discord.py, systemd)│
└─────────────┘                             └──────────┬───────────┘
                                                       │ HTTP localhost:8642
                                                       ▼
                                            ┌──────────────────────┐
                                            │ Hermes Gateway:8642  │
                                            │ (control plane)      │
                                            └──────────────────────┘
```

## Slash Commands to Implement (Option B)

| Command | Description |
|---------|-------------|
| `/hermes status` | Gateway health, connected platforms |
| `/hermes agent spawn` | Spawn sub-agent (coder/architect/critic) |
| `/hermes cron list` | List active cron jobs |
| `/hermes cron run <name>` | Trigger cron job manually |
| `/hermes deploy` | Deploy/update services |
| `/hermes thread create` | Create thread for task |
| `/hermes thread archive` | Archive current thread |
| `/hermes channel create` | Create dedicated channel |
| `/hermes session new` | New Hermes session in thread |
| `/hermes memory save` | Save context to memory |