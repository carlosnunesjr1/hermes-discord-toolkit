# Webhook Outbound: Hermes Gateway → Discord

## Overview

Hermes Gateway's webhook adapter (`gateway/platforms/webhook.py`) can deliver agent responses directly to Discord channels via **Discord Webhook URLs**. This enables cron jobs, alerts, and cross-platform messages to appear in Discord without the Gateway WS bot.

## Configuration

### Route Definition (config.yaml)

```yaml
webhook:
  enabled: true
  port: 8644
  secret: "webhook-secret-2026"
  extra:
    routes:
      # Existing Discord inbound route
      discord:
        secret: "discord-webhook-secret-2026"
        deliver: "discord"
        deliver_extra:
          channel_id: "1516397585701666962"
      
      # Outbound routes for specific channels
      deploy-status:
        secret: "deploy-webhook-secret"
        prompt: "Deploy status: {{payload}}"
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/DEPLOY_ID/DEPLOY_TOKEN"
          # OR use channel_id + env var
      
      infra-alerts:
        secret: "infra-webhook-secret"
        prompt: "ALERTA INFRA: {{payload}}"
        deliver: "discord"
        deliver_extra:
          channel_id: "1516397585701666962"
      
      bug-reports:
        secret: "bug-webhook-secret"
        prompt: "Novo bug: {{payload}}"
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/BUG_ID/BUG_TOKEN"
```

## Delivery Method: `_deliver_discord_webhook()`

```python
async def _deliver_discord_webhook(self, content: str, delivery: dict) -> SendResult:
    extra = delivery.get("deliver_extra", {})
    webhook_url = extra.get("webhook_url", "")
    
    # Fallback: channel_id → env var mapping
    if not webhook_url:
        channel_id = extra.get("channel_id", "")
        if channel_id:
            env_key = f"DISCORD_WEBHOOK_{channel_id}"
            webhook_url = os.getenv(env_key, "")
        if not webhook_url:
            webhook_url = os.getenv("DISCORD_DEFAULT_WEBHOOK_URL", "")
    
    if not webhook_url:
        return SendResult(success=False, error="Missing webhook_url")
    
    payload = {
        "content": content[:2000],  # Discord limit
        "username": "Hermes",
        "avatar_url": "https://cdn.discordapp.com/avatars/{APP_ID}/avatar.png"
    }
    
    # Thread support
    thread_id = extra.get("thread_id") or extra.get("message_thread_id")
    if thread_id:
        payload["thread_id"] = thread_id
    
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload, timeout=10) as resp:
            if resp.status in (200, 204):
                return SendResult(success=True)
            else:
                text = await resp.text()
                return SendResult(success=False, error=f"HTTP {resp.status}: {text}")
```

## Webhook URL Resolution Priority

1. **Route `deliver_extra.webhook_url`** — explicit per-route (highest priority)
2. **Route `deliver_extra.channel_id`** → env var `DISCORD_WEBHOOK_{channel_id}`
3. **Global env var** `DISCORD_DEFAULT_WEBHOOK_URL`

## Setting Up Discord Webhooks

### Per Channel (Manual, One-time)
1. Discord → Channel Settings → Integrations → Webhooks → New Webhook
2. Name: "Hermes Deploy" / "Hermes Alerts" / etc.
3. Channel: Target channel
4. Copy Webhook URL
4. Add to config.yaml route `deliver_extra.webhook_url`

### Via Environment Variables
```bash
# In /home/carlos/.hermes/.env (loaded by hermes-gateway systemd)
DISCORD_WEBHOOK_1516397585701666962=https://discord.com/api/webhooks/ID/TOKEN
DISCORD_DEFAULT_WEBHOOK_URL=https://discord.com/api/webhooks/DEFAULT_ID/DEFAULT_TOKEN
```

## Cron Job Integration

### Deliver Cron Output to Discord Channel

```yaml
# ~/.hermes/cron/jobs/deploy-monitor.yaml
schedule: "*/5 * * * *"
prompt: "Check recent deploy status and report failures"
skills: ["cn-tech-ecosystem-ops"]
deliver: "webhook:deploy-status"  # References route above
```

### Deliver to Thread (Preserves Context)

```yaml
deliver_extra:
  webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"
  thread_id: 1516641040352673924  # Target thread ID
```

## Payload Templating

The `prompt` field in route config is a Jinja2 template with webhook payload:

```yaml
prompt: |
  {{#if event}}
  Event: {{event}}
  {{/if}}
  {{#if content}}
  Message: {{content}}
  {{/if}}
  Timestamp: {{timestamp}}
```

Available variables: all fields from incoming webhook JSON payload.

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing webhook_url | Log error, return `SendResult(success=False, error=...)` |
| HTTP 404 | Webhook deleted → log, return error |
| HTTP 403 | Invalid token → log, return error |
| HTTP 429 | Rate limited → retry with backoff (configurable) |
| Timeout (10s) | Return connection error |
| Content > 2000 chars | Truncated to 2000 |

## Testing

```bash
# Test webhook route directly
curl -X POST http://localhost:8644/webhooks/deploy-status \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $(echo -n '{\"test\":\"deploy\"}' | openssl dgst -sha256 -hmac 'deploy-webhook-secret' | cut -d' ' -f2)" \
  -d '{"test":"deploy"}'

# Expected: {"status":"accepted","route":"deploy-status","delivery_id":"..."}
```

## Security

- HMAC secret required per route (validated at startup)
- `INSECURE_NO_AUTH` only allowed on loopback host
- Webhook URLs stored in config/env (not code)
- Rate limiting: 30 req/min per route (configurable)

## Integration with Auto-Provisioning

Bot's auto-provisioning can create webhooks automatically:

```python
# In _auto_provision_structure()
for channel_name, webhook_name in WEBHOOK_CHANNELS.items():
    channel = get_channel_by_name(guild, channel_name)
    webhook = await channel.create_webhook(name=webhook_name)
    # Store webhook.url in config/env for route
```

## Examples

### Deploy Notifications
```yaml
# Route
deploy-notify:
  secret: "deploy-secret"
  deliver: "discord"
  deliver_extra:
    webhook_url: "https://discord.com/api/webhooks/DEPLOY/TOKEN"

# Cron job
schedule: "@hourly"
prompt: "Deploy status: {{status}} | Version: {{version}} | Logs: {{logs_url}}"
deliver: "webhook:deploy-notify"
```

### Infra Alerts (VPS Health)
```yaml
# Route
infra-alerts:
  secret: "infra-secret"
  deliver: "discord"
  deliver_extra:
    channel_id: "1516397585701666962"

# Background task (_monitor_system_events)
# Detects ERROR in gateway logs → posts to #incidents via webhook
```

### Bug Tracker Integration
```yaml
# Route
bug-tracker:
  secret: "bug-secret"
  deliver: "discord"
  deliver_extra:
    webhook_url: "https://discord.com/api/webhooks/BUG/TOKEN"
    thread_id: 1516641014754967582  # #bugs thread
```

## Limitations

- **One-way**: Gateway → Discord only (no interaction responses)
- **No threading auto-create**: Must specify `thread_id` or post in channel
- **Rate limits**: Discord webhook limits apply (30/sec per webhook)
- **No rich embeds from template**: Only `content` field (embeds need JSON payload)