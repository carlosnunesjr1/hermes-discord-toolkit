# Webhook Outbound Discord Delivery — Implementation Reference

## Overview
Complete implementation of Discord message delivery from Hermes Gateway webhook adapter to Discord channels via Discord Channel Webhook URLs.

---

## File Location
`/usr/local/lib/hermes-agent/gateway/platforms/webhook.py` — method `_deliver_discord_webhook()` (line 894)

---

## Method Signature
```python
async def _deliver_discord_webhook(self, content: str, delivery: dict) -> SendResult
```

---

## Delivery Configuration (config.yaml)
```yaml
webhook:
  extra:
    routes:
      my-route:
        secret: "hmac-secret"
        prompt: "Template..."
        skills: []
        deliver: "discord"                    # REQUIRED: triggers _deliver_discord_webhook
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"  # DIRECT (highest priority)
          # OR use channel_id mapping via env:
          channel_id: "1516397585701666962"   # → reads DISCORD_WEBHOOK_1516397585701666962
          thread_id: 123456789012345678       # optional: post in thread
          message_thread_id: 123456789012345678  # alias for thread_id
```

---

## Environment Variable Mapping
```bash
# Channel-specific (highest priority after direct webhook_url)
DISCORD_WEBHOOK_1516397585701666962=https://discord.com/api/webhooks/ID/TOKEN

# Default fallback (used if channel_id not mapped)
DISCORD_DEFAULT_WEBHOOK_URL=https://discord.com/api/webhooks/ID/TOKEN
```

---

## Resolution Priority
```
1. deliver_extra.webhook_url (explicit in route config)
2. DISCORD_WEBHOOK_{channel_id} (env var mapping)
3. DISCORD_DEFAULT_WEBHOOK_URL (global fallback)
4. ❌ Error: "Missing webhook_url"
```

---

## Discord Payload Format
```python
payload = {
    "content": content[:2000],  # Discord 2000 char limit
    "username": "Hermes",
    "avatar_url": "https://cdn.discordapp.com/avatars/1516328637526179870/avatar.png"
}

# Thread support
if thread_id:
    payload["thread_id"] = thread_id
```

---

## HTTP Request
```python
async with aiohttp.ClientSession() as session:
    async with session.post(
        webhook_url,
        json=payload,
        timeout=10
    ) as resp:
        if resp.status in (200, 204):
            return SendResult(success=True)
        else:
            return SendResult(success=False, error=f"HTTP {resp.status}: {await resp.text()}")
```

---

## Error Handling
| Scenario | Return |
|----------|--------|
| Missing webhook_url | `SendResult(success=False, error="Missing webhook_url...")` |
| Connection error | `SendResult(success=False, error="Connection error: {e}")` |
| HTTP 4xx/5xx | `SendResult(success=False, error=f"HTTP {status}: {text}")` |
| Success (200/204) | `SendResult(success=True)` |

---

## Usage Examples

### 1. Cron Job → Discord Channel
```yaml
# ~/.hermes/cron/jobs/deploy-monitor.yaml
schedule: "*/5 * * * *"
prompt: "Check deploy status"
skills: ["cn-tech-ecosystem-ops"]
deliver: "discord"
deliver_extra:
  channel_id: "1516397585701666962"  # #deploy channel
```

### 2. Webhook Subscribe with Discord Outbound
```bash
hermes webhook subscribe github-deploy \
  --prompt "GitHub deploy event: {{payload}}" \
  --events "push" \
  --deliver "discord" \
  --deliver_extra '{"channel_id": "1516397585701666962"}'
```

### 3. Direct Delivery (deliver_only)
```yaml
# Config - skip agent, deliver payload directly
webhook:
  extra:
    routes:
      alert:
        secret: "alert-secret"
        deliver_only: true
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"
```

---

## Creating Discord Channel Webhooks
1. Discord → Channel Settings (⚙️) → Integrations → Webhooks
2. **New Webhook** → Name: "Hermes Outbound"
3. **Copy Webhook URL** → `https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN`
4. Add to `.env`: `DISCORD_WEBHOOK_1516397585701666962=<copied_url>`

---

## Testing
```bash
# Test webhook directly
curl -X POST "https://discord.com/api/webhooks/WEBHOOK_ID/WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test from Hermes", "username": "Hermes"}'

# Test via Hermes webhook route
curl -X POST http://localhost:8644/webhooks/test-route \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $(echo -n '{\"content\":\"test\"}' | openssl dgst -sha256 -hmac 'secret' | cut -d' ' -f2)" \
  -d '{"content":"test"}'
```

---

## Related Files
| File | Purpose |
|------|---------|
| `gateway/platforms/webhook.py:894` | `_deliver_discord_webhook()` implementation |
| `gateway/platforms/webhook.py:247` | Route handler calls delivery method |
| `bot.py:gateway_client.py` | Bot uses webhook for outbound via `forward_interaction()` |
| `.env.discord_webhook` | Template for Discord webhook URLs |

---

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| "Missing webhook_url" | No webhook_url in deliver_extra or env | Add `DISCORD_WEBHOOK_{channel_id}` to .env |
| "HTTP 404" | Invalid webhook URL | Recreate webhook in Discord channel settings |
| "HTTP 403" | Webhook token expired | Regenerate webhook in Discord |
| Message not in thread | Missing thread_id | Add `thread_id` to `deliver_extra` |
| Content truncated | >2000 chars | Content auto-truncated to 2000 chars |