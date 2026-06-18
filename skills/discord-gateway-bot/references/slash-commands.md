# Discord Gateway Bot - Slash Command Registry

## Command Group: `/hermes`

All commands are guild-scoped, synced instantly on startup to `DISCORD_GUILD_ID`.

---

### `/hermes panel`
**Main Control Panel** — Interactive UI with 4 Select menus + action buttons.

**Response**: Ephemeral embed with `HermesPanelView`
- **Systems Select**: Gateway, CN Tech, VPS, Workspace, Brain
- **Actions Select**: Deploy, Logs, Restart Gateway, Health Check
- **Channels Select**: Jump to any provisioned channel
- **Agents Select**: List active, spawn new, view history

---

### `/hermes status`
**Gateway Health** — Shows Hermes Gateway status + connected adapters.

**Response**: Embed with:
- Gateway status (🟢/🔴)
- Version
- Connected platforms (Telegram, Discord, Webhook, API Server)
- Uptime
- Quick action buttons: 🔄 Refresh, 📋 Logs, 🔧 Restart

---

### `/hermes help`
**Command Reference** — Lists all commands with descriptions.

**Response**: Embed with categorized command list.

---

### `/hermes thread create`
**Create Isolated Thread** — Modal inputs: name, topic, channel (Select).

**Flow**:
1. Modal opens
2. User fills: name (required), topic (optional), channel (Select, defaults to current)
3. Bot creates thread in target channel
4. Registers `ThreadSession` (no Hermes session yet)
5. Posts initial message with context hint
6. Adds user to thread

**Response**: Thread mention + "Thread created. Start with `@Hermes`..."

---

### `/hermes thread list`
**List Active Threads** — All active threads in current channel.

**Response**: Embed with thread list (name, topic, owner, age, status).

---

### `/hermes thread my`
**My Threads** — All active threads owned by user in current guild.

**Response**: Embed grouped by channel.

---

### `/hermes thread archive`
**Archive Current Thread** — Archives Discord thread, preserves `hermes_session_id`.

**Requirements**: Must be used inside a thread.

**Response**: Confirmation + "Context preserved. Send message to restore."

---

### `/hermes agent spawn`
**Spawn Subagent** — Modal with goal, toolsets (multi-select), context (optional).

**Modal Fields**:
- `goal` (required, textarea): What the agent should accomplish
- `toolsets` (multi-select): terminal, file, web, browser, coding, skills, etc.
- `context` (optional, textarea): Additional context for the agent

**Response**: Ephemeral "Agent spawned" + agent ID. Output appears in `#active` thread.

---

### `/hermes agent list`
**List Active Agents** — Shows all running/completed agents.

**Response**: Embed table: ID, Goal, Status, Thread, Started, Duration.

---

### `/hermes agent logs`
**Agent Logs** — Option: agent_id (autocomplete from active agents).

**Response**: Recent output from agent (last 100 lines).

---

### `/hermes cron list`
**List Cron Jobs** — All scheduled jobs from Hermes Gateway.

**Response**: Embed per job: name, schedule, status, last run, next run. Buttons: ▶️ Run, ⏸️ Pause, 📋 Logs.

---

### `/hermes cron run`
**Run Cron Job Manually** — Option: job_name (autocomplete).

**Response**: "Job triggered" + execution ID. Output in `#monitor`.

---

### `/hermes deploy`
**Trigger Deploy** — Interactive deploy with confirmation.

**Response**: Embed with ▶️ Deploy / ❌ Cancel / 📋 Logs buttons.

**On ▶️ Deploy**:
1. Gateway executes deploy (git pull + restart services)
2. Progress updates in same message
3. Final status with 🔄 Rollback button if failed

---

### `/hermes skills`
**Available Skills** — Categorized skill listing from Hermes Gateway.

**Response**: Embed with categories as fields, skills as values. Select to view details.

---

### `/hermes logs`
**Gateway Logs** — Option: lines (default 50, max 500).

**Response**: Code block with recent `journalctl -u hermes-gateway` output.

---

### `/hermes cntech status`
**CN Tech Ecosystem Status** — Health of all 4 containerized services.

**Response**: Embed table:
| Service | Container | Port | Health | Status |
|---------|-----------|------|--------|--------|
| Career Hub | cn-tech-career-hub | 2019 | 🟢 | Running |
| Nexus PIM | cn-tech-nexus-pim | 9121 | 🟢 | Running |
| Central Comando | cn-tech-centraldecomando | 9130 | 🟢 | Running |
| Control Daemon | cn-tech-control-daemon | 9120 | 🟢 | Running |

---

### `/hermes cntech deploy`
**Deploy Individual Service** — Option: service (autocomplete: career-hub, nexus-pim, central-comando, control-daemon).

---

### `/hermes vps health`
**VPS Health Audit** — Runs `vps-health-audit` skill.

**Response**: Embed with CPU, RAM, Disk, Network, Docker, Systemd status.

---

### `/hermes workspace status`
**Workspace Modules Status** — Lists all PWA modules and their health.

---

### `/hermes brain memory`
**Memory/Knowledge Base** — Shows memory stats, allows search/clear.

---

### `/hermes brain context`
**Current Context Inspection** — Shows active session context, token usage, memory.

---

### `/hermes brain sessions`
**Session Management** — List all Hermes sessions, switch/clear.

---

### `/hermes brain sync`
**Sync Vault → Memory** — Syncs Obsidian Vault content to Hermes Memory.

**Options**:
- `all` — All areas (default)
- `scope` — `all`, `areas`, `projetos`, `financas`, `saude`, `carreira`, `pessoal`
- `areas` — Comma-separated specific areas (e.g., `projetos,financas`)

**Payload sent to Gateway**: `brain sync scope:all areas:projetos,financas,saude,carreira,pessoal`

**Response**: Embed with sync progress + areas being processed.

---

### `/hermes autothread`
**Auto-Threading Configuration** — Automatic thread creation on keyword triggers.

| Subcommand | Parameters | Description |
|------------|------------|-------------|
| `on` | — | Enable auto-threading for DM + configured channels |
| `off` | — | Disable auto-threading |
| `channels` | `channels` (comma-separated IDs) | Set monitored channels (empty = all provisioned) |
| `triggers` | `triggers` (comma-separated keywords) | Set trigger keywords |
| `status` | — | Show current config + active channels |

**Default Triggers**: `@Hermes`, `/hermes`, `hermes `, `oi hermes`, `hermes bot`

**Default Channels** (v2.2+): All 31 provisioned channels + #geral = 32 channels.

**Response**: Embed with current config + channels list.

---

### `/hermes evolve`
**Auto-Evolution of Discord Structure** — Analyze patterns, propose, apply changes.

| Subcommand | Description |
|------------|-------------|
| `analyze` | Analyzes channel/thread usage → proposes new structure |
| `apply` | Applies proposed changes (creates channels/threads) |
| `status` | Dashboard: threads/day, agent spawns, compression, memory growth |

---

### `/hermes voice`
**Voice / JARVIS Mode** — Full voice channel integration.

| Subcommand | Description |
|------------|-------------|
| `join [channel]` | Join your current voice channel (or specified). **Immediate response + background connect** to avoid 3s interaction timeout. |
| `leave` | Disconnect from voice channel + clear state |
| `speak` | Next text message → spoken via TTS in voice channel |
| `listen` | Activate STT transcription (Whisper-1 via Gateway) |
| `status` | Embed with channel, listening state, latency |

**JARVIS Flow**:
1. Enter voice channel → `/hermes voice join` → "🔊 Conectado a #General — modo escuta ativa"
2. `/hermes voice speak` → "🎙️ Próxima mensagem será falada"
3. Type message → Hermes processes → Response in chat + **TTS in voice** 🎙️

**Requirements**: `PyNaCl`, `davey`, `edge-tts` (pip), `ffmpeg` (system)

---

### `/hermes podcast`
**Podcast Mode** — Automated audio content generation.

| Subcommand | Parameters | Description |
|------------|------------|-------------|
| `generate` | `topic`, `format`, `duration`, `voices`, `style` | Single custom episode |
| `briefing` | `voices`, `style` | ☀️ **Daily briefing** (auto-topic: date, projects, tasks, systems, agenda) |
| `meeting` | `topic`, `format`, `duration`, `voices`, `style` | 📋 **Meeting summary** (decisions, actions, next steps) |
| `project` | `topic`, `format`, `duration`, `voices`, `style` | 📦 **Project update** (progress, blockers, milestones, risks) |
| `schedule` | `name`, `topic`, `schedule` (cron), `format`, `channel` | 📅 **Recurring podcast** (cron) |
| `list` | — | List scheduled podcasts |
| `cancel` | `name` | Cancel scheduled podcast |

**Formats**: `daily_briefing` (3-5min), `meeting_summary` (5min), `project_update` (5min), `deep_dive` (10-15min), `conversation` (5-10min), `standup` (2-3min)

**Styles**: `professional`, `casual`, `technical`, `storytelling`

**Voices** (comma-separated): `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `pt-BR-ThalitaNeural`, `pt-BR-ErickNeural`

**Examples**:
```bash
/hermes podcast briefing
/hermes podcast meeting topic:"Planning Q3"
/hermes podcast project topic:"Nexus PIM"
/hermes podcast schedule name:"Daily" topic:"Briefing" schedule:"0 7 * * *" format:daily_briefing channel:#podcasts
```

---

### `/hermes health`
**Resilience Dashboard** — Complete system health check.

**Response**: Embed with:
- Overall status: 🟢 Healthy / 🟡 Degraded / 🔴 Unhealthy
- Discord WS latency
- Gateway status
- **Circuit Breakers**: `gateway` (3/30s), `discord_ws` (5/60s), `webhook_http` (3/30s)
- **Message Queue**: Pending / Total
- **Health Checks**: Per-service status + latency
- **Sync Managers**: Pending ops, last sync time

---

## Autocomplete Sources

| Parameter | Source |
|-----------|--------|
| `toolsets` (agent spawn) | `["terminal", "file", "web", "browser", "coding", "skills", "memory", "delegation", "cronjob"]` |
| `job_name` (cron run) | `GET /v1/cron/jobs` → names |
| `service` (cntech deploy) | `["career-hub", "nexus-pim", "central-comando", "control-daemon"]` |
| `agent_id` (agent logs) | Active agents from gateway |
| `channel` (thread create) | Provisioned channels in guild |
| `format` (podcast) | `["daily_briefing", "meeting_summary", "project_update", "deep_dive", "conversation", "standup"]` |
| `style` (podcast) | `["professional", "casual", "technical", "storytelling"]` |

---

## Permission Model

| Command | Required Permission |
|---------|---------------------|
| `/hermes panel/status/help/thread*/agent*/cron*/logs/skills` | None (all users) |
| `/hermes deploy/cntech*/vps*/workspace*/brain*` | `Manage Messages` (or configured admin role) |
| `/hermes voice/podcast` | `Connect` + `Speak` voice perms |

Admin check: `interaction.user.guild_permissions.manage_messages` or `user_id == config.admin_user_id`.

---

## Error Handling

All commands wrapped in try/except:
- Gateway connection errors → "⚠️ Gateway unreachable. Check `hermes-gateway` service."
- Discord HTTP errors → "⚠️ Discord API error. Retry or check permissions."
- Validation errors → Ephemeral "❌ Invalid input: {detail}"
- Unexpected errors → Logged + "⚠️ Internal error. Check bot logs."