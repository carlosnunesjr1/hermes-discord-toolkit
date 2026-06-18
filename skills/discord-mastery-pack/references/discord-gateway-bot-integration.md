# Discord Gateway Bot - Related Skill Reference

## Overview

This document bridges **discord-mastery-pack** (webhook-based Discord integration) with **discord-gateway-bot** (native WebSocket Gateway Bot).

## Architecture Comparison

| Aspect | discord-mastery-pack (Webhook) | discord-gateway-bot (Gateway Bot) |
|--------|--------------------------------|-----------------------------------|
| **Connection** | HTTP Webhook (Discord → Gateway) | WebSocket Gateway (Discord ↔ Bot) |
| **Auth** | Webhook URL + HMAC | Bot Token + Gateway Intents |
| **Commands** | Webhook routes only | Full Slash Commands (`/hermes ...`) |
| **Events** | Inbound webhook only | Real-time: mentions, threads, reactions |
| **Thread Mgmt** | Via webhook `channel_id` | Native Discord thread API |
| **Voice** | Not supported | `VoiceReceiver` in adapter |
| **Multi-user** | Single tenant (webhook) | Multi-user in same server |

## When to Use Each

| Use Case | Recommended Skill |
|----------|-------------------|
| **Simple notifications** (cron alerts, deploy status) | `discord-mastery-pack` webhook outbound |
| **Full interactive control plane** | `discord-gateway-bot` |
| **Slash commands** (`/hermes panel`) | `discord-gateway-bot` |
| **Auto-thread creation on mention** | `discord-gateway-bot` |
| **Voice channel integration** | `discord-gateway-bot` |
| **Multi-user collaboration** | `discord-gateway-bot` |
| **Cron job delivery to Discord** | Both (webhook outbound in Gateway) |

## Hybrid Architecture (Current Production)

Both skills active simultaneously:

```
┌─────────────┐     HTTPS/Webhook      ┌──────────────┐
│   Discord   │ ─────────────────────► │   Caddy      │ ──► webhook:8644
│  (Webhook)  │   webhook.menusummo    │  (SSL/Proxy) │
└─────────────┘                         └──────────────┘
                                               │
                    ┌────────────────────────┘
                    ▼
         ┌──────────────────┐     HTTP :8642      ┌─────────────────┐
         │ hermes-discord-  │ ─────────────────► │ Hermes Gateway  │
         │ bot (WS)         │                    │ :8642           │
         │ systemd service  │                    │ (control plane) │
         └──────────────────┘                    └─────────────────┘
```

**Paths:**
1. **Webhook Path** → Hermes Gateway → Webhook Adapter → Discord Channel Webhook URL (outbound)
2. **Gateway Bot Path** → Discord WS → Bot → HTTP :8642 → Hermes Gateway → Agent → Discord WS response

## Integration Points

### 1. Webhook Outbound → Discord (Implemented in Gateway)
Both skills use the same webhook outbound method:
- Gateway `webhook` adapter has `_deliver_discord_webhook()`
- Uses `deliver: "discord"` + `deliver_extra.webhook_url`
- Thread support via `thread_id` / `message_thread_id`

### 2. Thread Session Compatibility
- `discord-gateway-bot` uses `~/.hermes/discord_threads.json`
- `discord-mastery-pack` webhook can target same threads via `thread_id`
- Both preserve `hermes_session_id` for context continuity

### 3. Shared Configuration
| Config | discord-mastery-pack | discord-gateway-bot |
|--------|---------------------|---------------------|
| Discord Bot Token | ❌ (Webhook only) | ✅ Required |
| Discord App ID | ❌ | ✅ Required |
| Discord Guild ID | ❌ | ✅ Required |
| Hermes Gateway URL | ✅ (API) | ✅ (Bot client) |
| Webhook URL | ✅ (outbound) | ✅ (outbound via Gateway) |

## Deployment Recommendations

### For Full Discord Control Plane (Option B)
```bash
# 1. Install discord-mastery-pack base (webhook + cron + MCP)
hermes skill install discord-mastery-pack
# ... configure webhook, cron, MCP ...

# 2. Deploy Gateway Bot for full features
cd /home/carlos/hermes-discord-bot
./deploy.sh install
./deploy.sh start
```

### For Minimal Setup (Webhook Only)
```bash
# Only discord-mastery-pack
hermes skill install discord-mastery-pack
# Configure webhook outbound for cron/alerts
# No Gateway Bot needed
```

## Migration Path

| From | To | Steps |
|------|-----|-------|
| Webhook only | Full Gateway Bot | 1. Create Discord Application/Bot\n2. Add Bot Token/App ID/Guild ID to `.env`\n3. Run `./deploy.sh install && ./deploy.sh start`\n4. Slash commands auto-sync to guild |
| Gateway Bot | Webhook only | 1. Stop `hermes-discord-bot` service\n2. Configure webhook outbound in Gateway\n3. Keep CRM webhook for alerts |

## Feature Parity Matrix

| Feature | discord-mastery-pack | discord-gateway-bot | Notes |
|---------|---------------------|---------------------|-------|
| **Slash Commands** | ❌ | ✅ `/hermes panel`, `/hermes deploy`, etc. | Gateway Bot only |
| **Thread Auto-Provisioning** | ❌ | ✅ 6 categories × 4 channels | Gateway Bot only |
| **Background Automation** | Cron only | ✅ 3 tasks (monitor, cleanup, sync) | Gateway Bot only |
| **Thread Persistence** | ❌ | ✅ JSON + session preservation | Gateway Bot only |
| **Rich UI (Selects/Modals)** | ❌ | ✅ Views, Modals, Buttons | Gateway Bot only |
| **Reaction Controls** | ❌ | ✅ ✅❌🔄📋🧵🤖 | Gateway Bot only |
| **Cron Delivery to Discord** | ✅ Webhook | ✅ Webhook (via Gateway) | Both |
| **Webhook Inbound** | ✅ | ❌ (uses WS instead) | Different paradigms |
| **MCP Integration** | ✅ | Via Gateway | Both |
| **Voice Channel** | ❌ | ✅ `VoiceReceiver` in adapter | Gateway Bot only |
| **Multi-user** | ❌ | ✅ Per-thread sessions | Gateway Bot only |

## References

- **discord-gateway-bot**: `~/.hermes/skills/devops/discord-gateway-bot/`
  - `references/architecture.md` — Full architecture
  - `references/slash-commands.md` — All 20+ commands
  - `references/thread-management.md` — Session mapping
  - `references/auto-provisioning.md` — Structure creation
  - `references/ui-components.md` — Views, Modals, Selects
  - `references/background-tasks.md` — Automation
  - `references/webhook-outbound.md` — Gateway → Discord delivery
  - `references/troubleshooting.md` — Common issues

- **discord-mastery-pack**: `~/.hermes/skills/devops/discord-mastery-pack/`
  - `references/COURSE.md` — Complete course
  - `references/ARCHITECTURE.md` — Webhook architecture
  - `references/DAILY_WORKFLOW.md` — Daily usage
  - `references/option-b-implementation.md` — Gateway Bot implementation
  - `references/auto-provisioning-ui.md` — Auto-provisioning + UI
  - `references/webhook-config-details.md` — Webhook setup