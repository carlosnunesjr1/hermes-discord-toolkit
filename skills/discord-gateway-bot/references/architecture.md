# Discord Gateway Bot Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DISCORD SERVER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ 🚀HERMES-OPS │  │ 🔧CN-TECH    │  │ 🏗️INFRA      │  │ 🤖AGENTS     │    │
│  │ #deploy      │  │ #career-hub  │  │ #vps-health  │  │ #active      │    │
│  │ #monitor     │  │ #nexus-pim   │  │ #docker      │  │ #spawn       │    │
│  │ #incidents   │  │ #central     │  │ #network     │  │ #history     │    │
│  │ #logs        │  │ #control     │  │ #backups     │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐                                        │
│  │ 📋TASKS      │  │ 🧠BRAIN      │                                        │
│  │ #features    │  │ #memory      │                                        │
│  │ #bugs        │  │ #context     │                                        │
│  │ #research    │  │ #sessions    │                                        │
│  │ #docs        │  │ #knowledge   │                                        │
│  └──────────────┘  └──────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Discord Gateway WebSocket
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HERMES-DISCORD-BOT (discord.py)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Event Loop  │  │ Slash Cmds  │  │ Thread Mgr  │  │ UI Views    │       │
│  │ (WS recv)   │  │ (app_cmds)  │  │ (persist)   │  │ (Selects,   │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  │  Buttons,   │       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  Modals)    │       │
│  │ Gateway     │  │ Background  │  │ Reaction    │  └─────────────┘       │
│  │ HTTP Client │  │ Tasks       │  │ Handler     │                        │
│  └─────────────┘  └─────────────┘  └─────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP localhost:8642
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HERMES GATEWAY (:8642)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Agents/     │  │ Skills      │  │ Cron        │  │ Tools       │       │
│  │ Subagents   │  │             │  │ Scheduler   │  │ (terminal,  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  │  web, etc.) │       │
│                                                    └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flows

### 1. Slash Command Execution
```
User → /hermes panel
  → Discord Gateway WS → bot.py on_interaction()
  → HermesPanelView sent (ephemeral)
  → User selects "Systems" → "CN Tech Status"
  → bot.py callback → gateway_client.post("/v1/cntech/status")
  → Hermes Gateway executes → returns JSON
  → bot.py edits interaction response with embed
```

### 2. Thread Message → Hermes Session
```
User in thread: @Hermes analyze logs
  → Discord Gateway WS → bot.py on_message()
  → thread_manager.get_session(thread_id) → hermes_session_id
  → gateway_client.post("/v1/chat", {session_id, message})
  → Hermes Gateway processes with session context
  → Response → bot.py sends to same thread
```

### 3. Auto-Incident Creation
```
Background task _monitor_system_events (60s)
  → Reads journalctl -u hermes-gateway
  → Filters ERROR level logs
  → For each new error: creates thread in #incidents
  → Posts embed with error details + action buttons
  → Registers thread session (no Hermes session yet)
```

### 4. Webhook Outbound (Gateway → Discord)
```
Hermes Gateway (webhook adapter)
  → Route deliver: "discord" + deliver_extra.webhook_url
  → _deliver_discord_webhook()
  → aiohttp POST to Discord webhook URL
  → Discord posts in target channel/thread
```

## Thread Session Lifecycle

```
┌─────────────┐     create_thread()     ┌─────────────┐
│  User runs  │ ──────────────────────► │ Thread      │
│  /hermes    │                         │ Created     │
│  thread     │                         │ + Registered│
│  create     │                         │ in Manager  │
└─────────────┘                         └──────┬──────┘
                                               │
                        @Hermes in thread      │
                                               ▼
┌─────────────┐     get_session()      ┌─────────────┐
│  Thread     │ ◄────────────────────── │ Hermes      │
│  has hermes │                         │ Session ID  │
│  session    │                         │ Linked      │
└─────────────┘                         └─────────────┘
                                               │
                        archive_thread()       │
                                               ▼
┌─────────────┐     is_active=False      ┌─────────────┐
│  Thread     │ ──────────────────────► │ Archived    │
│  Archived   │   (hermes_session_id    │ (preserved) │
│  in Discord │    preserved in JSON)   │             │
└─────────────┘                         └──────┬──────┘
                                               │
                        message in archived    │
                        thread                 ▼
┌─────────────┐     unarchive_thread()    ┌─────────────┐
│  Thread     │ ◄──────────────────────── │ Restored    │
│  Unarchived │   (hermes_session_id      │ (active +   │
│  in Discord │    auto-restored on next  │  context)   │
└─────────────┘    message)                └─────────────┘
```

## Persistence

**File**: `~/.hermes/discord_threads.json`

```json
{
  "threads": [
    {
      "thread_id": 1516641040352673924,
      "channel_id": 1516397585701666962,
      "guild_id": 1516397584942370836,
      "owner_id": 1516328637526179870,
      "hermes_session_id": "20260617_001234_abc123",
      "created_at": "2026-06-17T00:10:02.689",
      "last_activity": "2026-06-17T00:12:35.977",
      "topic": "Session Management",
      "is_active": true
    }
  ],
  "saved_at": "2026-06-17T00:12:35.978"
}
```

**Load**: On bot startup (`ThreadManager.__init__` → `_load_persistence()`)
**Save**: On every mutation (`_save_persistence()` called after register, archive, unarchive, cleanup)

## Background Tasks

| Task | Interval | Key Logic |
|------|----------|-----------|
| `_monitor_system_events` | 60s | `journalctl -u hermes-gateway --since "60s ago" -p err` → parse → create incident threads |
| `_cleanup_inactive_threads` | 3600s | Iterate `_threads`, if `!is_active` and age > 168h → remove from memory + JSON |
| `_sync_thread_sessions` | 300s | For each active thread: verify Discord thread exists, sync `last_activity` |

## Security

- Bot token only in `.env` (never in code)
- systemd hardening: `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`, `ReadWritePaths=/home/carlos/hermes-discord-bot`
- Guild-scoped slash commands (no global sync)
- Ephemeral responses for admin actions
- Reaction controls only on bot's own messages