---
name: discord-gateway-bot
category: devops
description: Discord Gateway WebSocket Bot with Hermes Agent integration — standalone bot process connecting via Discord Gateway WS and Hermes Gateway HTTP, with slash commands, thread management, auto-provisioning, background automation, and Discord UI components.
tags:
  - discord
  - gateway
  - websocket
  - hermes-agent
  - slash-commands
  - thread-management
  - auto-provisioning
  - discord-ui
---

# Discord Gateway Bot with Hermes Integration

## Overview

Standalone Discord bot process (`hermes-discord-bot`) that connects to Discord via **WebSocket Gateway** (not webhooks) and to Hermes Agent via **HTTP (localhost:8642)**. Provides full interactive control plane through Discord.

## Architecture

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

## Core Components

| File | Purpose |
|------|---------|
| `bot.py` | Main bot: Gateway WS, slash commands, event handlers, UI Views |
| `config.py` | Environment config loader (`.env`) |
| `gateway_client.py` | Async HTTP client → Hermes Gateway REST API |
| `thread_manager.py` | Thread ↔ Hermes session mapping with JSON persistence |
| `deploy.sh` | Install/update/manage script with systemd integration |
| `service/hermes-discord-bot.service` | systemd unit (hardened) |

## Key Capabilities

### Slash Commands (Guild-scoped, instant sync)
| Command | Description |
|---------|-------------|
| `/hermes panel` | Main control panel (7 Selects: Systems, Actions, Channels, Agents, CN-TECH, Workspace, Infra) |
| `/hermes status` | Gateway health + connected adapters |
| `/hermes health` | **Resilience dashboard**: circuit breakers, message queue, health checks, sync managers |
| `/hermes thread create` | Create isolated thread + Hermes session |
| `/hermes thread list/my/archive` | Thread lifecycle |
| `/hermes agent spawn/list` | Subagent orchestration (max 3 parallel) |
| `/hermes cron list/run` | Cron job management |
| `/hermes deploy` | Deploy with ▶️/❌/📋 buttons |
| `/hermes skills/help/logs` | Skills, help, gateway logs |
| `/hermes brain sync/memory/context/sessions/knowledge/clear` | Brain: sync vault, memory, context, sessions |
| `/hermes autothread on/off/channels/triggers/status` | Auto-threading: DM/channels keyword-triggered threads |
| `/hermes evolve analyze/apply/status` | Auto-evolution: analyze patterns, apply structure, metrics |
| `/hermes voice join/leave/speak/listen/status` | **Voice/JARVIS mode**: join voice channel, TTS speak, STT listen, auto-disconnect |
### Auto-Threading (New in v2.1)

Automatically creates threads when trigger keywords detected in DM or configured channels:

**Configuration (via `.env` or `/hermes autothread`):**
```bash
AUTO_THREAD_ENABLED=true
AUTO_THREAD_CHANNELS=1516397585701666962,1516397585701666963  # Channel IDs (empty = only DM)
AUTO_THREAD_TRIGGERS=@Hermes,/hermes,hermes ,oi hermes  # Keywords
```

**Default Channels (v2.2+):** If `AUTO_THREAD_CHANNELS` is empty but the bot has auto-provisioned structure, it automatically monitors all 28 provisioned channels + #geral (32 total). Override with `/hermes autothread channels <ids>`.

**Behavior:**
- DM: Any message with trigger → creates thread in DM + processes there
- Channel: Message in monitored channel with trigger → creates thread from message + processes
- Thread creation includes: original message, system panel, Hermes session isolation
- Bot mentions (`@Hermes`) handled separately (no auto-thread, direct mention handler)
- Post-unarchive messages auto-restore Hermes session context


### Voice / JARVIS Mode (v2.3+)

Full voice channel integration for real-time conversational AI:

| Command | Function |
|---------|----------|
| `/hermes voice join [channel]` | Join your current voice channel (or specified) |
| `/hermes voice leave` | Disconnect from voice channel |
| `/hermes voice speak` | Next text message → spoken via TTS in voice |
| `/hermes voice listen` | Activate STT transcription (Whisper-1) |
| `/hermes voice status` | Show voice connection status + latency |

**TTS**: Edge TTS (free), voice `pt-BR-AntonioNeural`, generates MP3 → played via `discord.FFmpegPCMAudio` (requires `ffmpeg`)
**STT**: OpenAI Whisper-1 (configured in Hermes Gateway `stt.provider: openai`)
**Voice deps**: `PyNaCl` + `davey` + `edge-tts` (pip), `ffmpeg` (system)
**Auto-disconnect**: Bot leaves after 30s alone in voice channel (watches `on_voice_state_update`)

See `references/voice-jarvis.md` for full implementation details.

### Podcast Mode (v2.4+)

Automated audio content generation for briefings, meeting summaries, project updates, and scheduled episodes.

| Command | Function |
|---------|----------|
| `/hermes podcast briefing` | ☀️ Daily briefing (auto-topic: projects, tasks, systems, agenda) |
| `/hermes podcast meeting topic:"..."` | 📋 Meeting summary (decisions, actions, next steps) |
| `/hermes podcast project topic:"..."` | 📦 Project update (progress, blockers, milestones, risks) |
| `/hermes podcast generate topic:"..."` | Custom episode with full control |
| `/hermes podcast schedule name:"..." topic:"..." schedule:"0 7 * * *"` | 📅 Recurring podcast (cron) |
| `/hermes podcast list/cancel` | List or cancel scheduled |

**Formats**: `daily_briefing`, `meeting_summary`, `project_update`, `deep_dive`, `conversation`, `standup`
**Styles**: `professional`, `casual`, `technical`, `storytelling`
**Voices**: `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `pt-BR-ThalitaNeural`, `pt-BR-ErickNeural` (comma-separated for multi-voice)

See `references/podcast-mode.md` for complete implementation details.
- **Auto-disconnect**: Bot leaves after 30s alone in voice channel (watches `on_voice_state_update`)
- **Voice state tracking**: `voice_listening[guild_id]`, `voice_speak_next[guild_id]` dicts for per-guild state

**Flow (JARVIS style):**
```
You enter voice channel
    ↓
/hermes voice join     → "🔊 Conectado a #General — modo **escuta ativa**"
    ↓
/hermes voice speak
You type: "Hermes, status do deploy"
    ↓
Hermes processes via Gateway → replies in chat + **SPEAKS in voice** 🎙️
```

**Configuration in Hermes Gateway (`config.yaml`):**
```yaml
stt:
  enabled: true
  provider: openai          # Whisper-1
  openai:
    model: whisper-1

tts:
  provider: edge            # Edge TTS (free)
  edge:
    voice: pt-BR-AntonioNeural
  use_gateway: true
  enabled: true
```

**Requirements:** `ffmpeg` system binary (for audio playback), `PyNaCl`, `davey`, `edge-tts` in venv.

#### Critical Pitfall: `show_reasoning` must be **false** for Voice

**Problem:** With `show_reasoning: true` (default), the Gateway prepends internal reasoning to responses:
```
💭 **Reasoning:**
```
The user wants to understand X...
...
```
**Then** the actual response. This gets spoken by TTS → garbled voice output.

**Fix:** Disable `show_reasoning` for Discord platform in Gateway config:
```yaml
display:
  show_reasoning: false          # Global
  platforms:
    discord:
      streaming: false
      show_reasoning: false      # Discord-specific override
```

**Voice Interaction Timeout Pattern (Critical for `/voice join`)**

Voice connection takes 2-5s — exceeds Discord's 3s interaction timeout. **Must use immediate response + background task:**

```python
@discord.app_commands.command(name="voice")
async def cmd_voice(interaction, action: str, channel: discord.VoiceChannel = None):
    bot = interaction.client
    target = channel or interaction.user.voice?.channel
    
    if action == "join":
        if not target:
            return await interaction.response.send_message("❌ Enter a voice channel first", ephemeral=True)
        
        # IMMEDIATE response (resets 3s interaction timer)
        await interaction.response.send_message(f"🔊 Conectando a {target.mention}...", ephemeral=True)
        
        # Long operation in background
        async def do_connect():
            try:
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(target)
                else:
                    await target.connect()
                bot.voice_listening[interaction.guild.id] = True
                await interaction.followup.send(f"✅ Conectado a {target.mention}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Falha: {e}", ephemeral=True)
        
        asyncio.create_task(do_connect())
        return  # Command returns immediately — no timeout
    
    # Fast actions: defer is fine
    await interaction.response.defer(ephemeral=True)
    # ... handle leave, speak, listen, status
```

#### Voice TTS Clean Response (v2.3.1+)

Only speak the **final response text**, stripped of reasoning/markdown:

```python
async def _speak_in_voice(self, guild_id: int, text: str):
    """Send TTS audio to voice channel using Edge TTS (clean response only)."""
    # Clean response for speech: strip markdown, reasoning tags, code blocks
    import re
    clean_text = re.sub(r'```[\s\S]*?```', '', text)  # Remove code blocks
    clean_text = re.sub(r'\*\*.*?\*\*', '', clean_text)  # Remove bold
    clean_text = re.sub(r'💭.*?Reasoning.*?\n', '', clean_text)  # Remove reasoning header
    clean_text = clean_text[:4000].strip()
    
    if not clean_text:
        return
    
    # Edge TTS generation with temp file cleanup
    communicate = edge_tts.Communicate(clean_text, "pt-BR-AntonioNeural")
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        temp_path = f.name
    await communicate.save(temp_path)
    
    source = discord.FFmpegPCMAudio(temp_path)
    vc.play(source)
    
    # Cleanup after playing
    def cleanup(_):
        try: os.unlink(temp_path)
        except: pass
    vc.after = cleanup
```

### Voice / JARVIS Mode (v2.3+)

Full voice channel integration for real-time conversational AI:

| Command | Function |
|---------|----------|
| `/hermes voice join [channel]` | Join your current voice channel (or specified) |
| `/hermes voice leave` | Disconnect from voice channel |
| `/hermes voice speak` | Next text message → spoken via TTS in voice |
| `/hermes voice listen` | Activate STT transcription (Whisper-1) |
| `/hermes voice status` | Show voice connection status + latency |

**TTS**: Edge TTS (free), voice `pt-BR-AntonioNeural`, generates MP3 → played via `discord.FFmpegPCMAudio` (requires `ffmpeg`)
**STT**: OpenAI Whisper-1 (configured in Hermes Gateway `stt.provider: openai`)
**Voice deps**: `PyNaCl` + `davey` + `edge-tts` (pip), `ffmpeg` (system)
**Auto-disconnect**: Bot leaves after 30s alone in voice channel (watches `on_voice_state_update`)

See `references/voice-jarvis.md` for full implementation details.

### Podcast Mode (v2.4+)

Automated audio content generation for briefings, meeting summaries, project updates, and scheduled episodes.

| Command | Function |
|---------|----------|
| `/hermes podcast briefing` | ☀️ Daily briefing (auto-topic: projects, tasks, systems, agenda) |
| `/hermes podcast meeting topic:"..."` | 📋 Meeting summary (decisions, actions, next steps) |
| `/hermes podcast project topic:"..."` | 📦 Project update (progress, blockers, milestones, risks) |
| `/hermes podcast generate topic:"..."` | Custom episode with full control |
| `/hermes podcast schedule name:"..." topic:"..." schedule:"0 7 * * *"` | 📅 Recurring podcast (cron) |
| `/hermes podcast list/cancel` | List or cancel scheduled |

**Formats**: `daily_briefing`, `meeting_summary`, `project_update`, `deep_dive`, `conversation`, `standup`
**Styles**: `professional`, `casual`, `technical`, `storytelling`
**Voices**: `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `pt-BR-ThalitaNeural`, `pt-BR-ErickNeural` (comma-separated for multi-voice)

See `references/podcast-mode.md` for complete implementation details.

### Thread Persistence & Legacy Format Handling
| Command | Gateway Route | Function |
|---------|---------------|----------|
| `/hermes brain sync all` | `brain sync scope:all areas:...` | Syncs Obsidian Vault → Hermes Memory (areas: projetos, financas, saude, carreira, pessoal) |
| `/hermes brain sync areas projetos,financas` | `brain sync scope:areas areas:...` | Syncs specific areas |
| `/hermes evolve analyze` | `evolve analyze` | Analyzes channel/thread usage patterns → proposes structure |
| `/hermes evolve apply` | `evolve apply` | Applies proposed structure changes |
| `/hermes evolve status` | `evolve status` | Dashboard: threads/day, agent spawns, compression ratio, memory growth |

### Thread ↔ Hermes Session Mapping
- **Each thread = isolated Hermes session** (context preserved)
- `ThreadSession` dataclass: `thread_id`, `channel_id`, `guild_id`, `owner_id`, `hermes_session_id`, `topic`, `is_active`
- **JSON persistence** at `~/.hermes/discord_threads.json` (survives restarts)
- **Archive = preserve** `hermes_session_id`; unarchive → auto-restore context
- Cleanup: inactive > 1 week auto-removed
- **Legacy format handling**: Old persistence was array of thread ID strings. `_load_persistence()` detects `list` format, logs warning, starts fresh (overwritten on next save). New format: object with `threads` array + `saved_at` timestamp.

### Thread Persistence Schema
### Thread Persistence Schema
### Thread Persistence Schema
Creates complete Discord structure automatically:
```
🚀 HERMES-OPS:      #deploy #monitor #incidents #logs
🔧 CN-TECH:         #career-hub #nexus-pim #nectar #central-comando #control-daemon #redis
🧱 WORKSPACE:       #workspace #dashboard #gateway #webhook
🏗️ INFRA:           #vps-health #docker #network #backups
🤖 AGENTS:          #active #spawn #history
📋 TASKS:           #features #bugs #research #docs
🧠 BRAIN:           #memory #context #sessions #knowledge
```
Each channel gets initial thread + panel message. **Total: 7 categories, 32 channels, 32 threads.**

### Auto-Provisioning Configuration
The structure is defined in `AUTO_PROVISION_STRUCTURE` dict in `bot.py`. To modify:
1. Edit the dict in `bot.py`
2. Restart bot: `./deploy.sh restart`
3. Bot re-provisions missing items only (idempotent)

### Background Automation Tasks
| Task | Interval | Function |
|------|----------|----------|
| `_monitor_system_events` | 60s | Scans gateway logs → auto-creates incident threads in #incidents |
| `_cleanup_inactive_threads` | 1h | Removes threads inactive > 1 week |
| `_sync_thread_sessions` | 5min | Syncs Hermes sessions with active threads |
| **Resilience: Queue Processor** | 5s | Processes message queue with exponential backoff |
| **Resilience: Health Monitor** | 30s | Runs health checks, logs degraded/unhealthy |

### Resilience Layer (New in v2.2)

Added `resilience.py` with production-grade resilience patterns:

#### Circuit Breakers
Prevents cascade failures when external services degrade:
| Circuit | Threshold | Recovery | Purpose |
|---------|-----------|----------|---------|
| `gateway` | 3 failures | 30s | Hermes Gateway HTTP |
| `discord_ws` | 5 failures | 60s | Discord Gateway WS |
| `webhook_http` | 3 failures | 30s | Webhook HTTP delivery |

States: `CLOSED` (normal) → `OPEN` (rejecting) → `HALF_OPEN` (testing recovery)

#### Persistent Message Queue (`~/.hermes/resilience/outbound_queue.json`)
- Survives bot/gateway restarts
- Exponential backoff: 1s → 2s → 4s → 8s → 16s (max 60s)
- Priority ordering (urgent first)
- Max 5 retries per message
- Auto-cleanup: completed > 24h removed

#### Fallback Delivery Chain (Automatic Priority)
```
1. Discord WS (Bot connected via Gateway)     ← PREFERRED, zero config
2. Webhook HTTP (configured URL)              ← Manual fallback
3. Local Queue (persistent)                   ← Guaranteed eventual delivery
```

#### Health Checks (Every 30s)
Registers: `discord_ws` (latency + connected), `gateway` (/health), `webhook` (port 8644/health)
Overall status: `healthy` / `degraded` / `unhealthy`

#### Sync Managers
For operations needing retry/conflict resolution (brain sync, etc.):
- Queue operations with metadata
- Track attempts, mark success/failure
- Persistent state in `~/.hermes/resilience/{name}_sync.json`

#### Systemd Watchdog Integration
- `WatchdogSec=60` in systemd unit — systemd kills if bot hangs 60s
- `StartLimitBurst=3` in 60s — prevents restart loops
- Bot sends `WATCHDOG=1` every 30s via `sdnotify`
- Graceful `STOPPING=1` on shutdown

### Slash Commands (Guild-scoped, instant sync)
- **HermesPanelView**: 4 Selects (Systems, Actions, Channels, Agents) + buttons
- **DeployView**: ▶️ Deploy / ❌ Cancel / 📋 Logs
- **AgentSpawnModal**: Goal, toolsets, context input
- **ThreadCreateModal**: Name, topic, channel select
- **Reaction Controls**: ✅ approve, ❌ reject, 🔄 restart gateway, 📋 logs, 🧵 thread info, 🤖 agents

### Event Automation (Zero Manual)
| Trigger | Auto-Action |
|---------|-------------|
| Gateway ERROR log | Creates `#incidents/🔴 ALERT: ERROR - HH:MM` with action panel |
| Mention in non-Hermes thread | Creates new thread + links Hermes session |
| Archived thread receives message | Auto-unarchives + restores Hermes session |
| Bot restart | Re-provisions missing structure |

### Hermes Gateway Integration
- **HTTP Client** (`gateway_client.py`): `aiohttp` async client to `http://localhost:8642`
- Endpoints used:
  - `GET /health` — gateway status
  - `POST /v1/discord/interaction` — slash command execution
  - `POST /v1/agent/spawn` — subagent creation
  - `GET /v1/cron/jobs` — cron listing
  - `POST /v1/cron/run` — manual cron execution
  - `POST /v1/deploy` — deploy trigger
  - `GET /v1/skills` — skills listing
- **Brain/Context Commands** (via webhook `/webhooks/discord`):
  - `brain sync scope:all areas:projetos,financas,saude,carreira,pessoal` — Vault → Memory sync
  - `memory show` — display memory
  - `context inspect` — inspect context
  - `sessions list` — list sessions
  - `evolve analyze/apply/status` — Discord auto-evolution
- **Webhook HMAC**: Shared secret `discord-webhook-secret-2026` (configurable)

## Deployment

```bash
cd /home/carlos/hermes-discord-bot

# 1. Configure .env with tokens from Discord Developer Portal
cp .env.template .env
# DISCORD_BOT_TOKEN=*** (Bot → Reset Token)
# DISCORD_APP_ID=... (General Information → Application ID)
# DISCORD_GUILD_ID=... (Dev Mode → Right-click server → Copy ID)

# 2. Install & start
./deploy.sh install
./deploy.sh start

# 3. Verify
./deploy.sh status
./deploy.sh logs
```

### Discord Developer Portal Setup
1. **Application** → New Application → "Hermes Agent"
2. **Bot** → Reset Token → Copy to `DISCORD_BOT_TOKEN`
3. **Bot → Privileged Gateway Intents** → Enable:
   - ✅ Message Content Intent
   - ✅ Server Messages Intent
   - ✅ Guild Members Intent (optional)
4. **OAuth2 → URL Generator** → Scopes: `bot` + `applications.commands`
   - Bot Permissions: Manage Channels, Manage Threads, Send Messages, Send Messages in Threads, Embed Links, Read Message History, Use Slash Commands, Add Reactions, Manage Messages
5. **General Information** → Application ID → `DISCORD_APP_ID`
6. **Discord (Dev Mode)** → Right-click server → Copy ID → `DISCORD_GUILD_ID`
### Environment Variables (`.env`)

```bash
# Required
DISCORD_BOT_TOKEN=***           # Bot token from Developer Portal
DISCORD_APP_ID=1234567890       # Application ID
DISCORD_GUILD_ID=1234567890     # Server/Guild ID

# Optional
HERMES_GATEWAY_URL=http://localhost:8642
LOG_LEVEL=INFO

# Auto-threading (v2.1+)
AUTO_THREAD_ENABLED=true
AUTO_THREAD_CHANNELS=1516641040352673924,1516643818873557114
AUTO_THREAD_TRIGGERS=@Hermes,/hermes,hermes ,oi hermes

# Voice/JARVIS (v2.3+) — installed in venv
# PyNaCl + davey + edge-tts (pip install PyNaCl davey edge-tts)
# ffmpeg (system: apt-get install ffmpeg)

# Webhook outbound (set in Hermes Gateway .env, not bot .env)
# DISCORD_WEBHOOK_{channel_id}=https://discord.com/api/webhooks/ID/TOKEN
```

### Hermes Gateway Config (`config.yaml`) for Voice

```yaml
stt:
  enabled: true
  provider: openai          # Whisper-1
  openai:
    model: whisper-1
  use_gateway: true

tts:
  provider: edge            # Edge TTS (free)
  edge:
    voice: pt-BR-AntonioNeural
  use_gateway: true
  enabled: true
```

### Webhook Outbound (Discord Delivery) — With WS Fallback

Implemented in Hermes Gateway webhook adapter (`gateway/platforms/webhook.py`):

```python
# Route config in config.yaml:
webhook:
  extra:
    routes:
      deploy-status:
        secret: "deploy-secret"
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"
          # OR channel_id + env var DISCORD_WEBHOOK_{channel_id}
```

**Delivery method (updated with WS-first fallback):**

```python
async def _deliver_discord_webhook(self, content: str, delivery: dict) -> SendResult:
    extra = delivery.get("deliver_extra", {})
    
    # FIRST: Try cross-platform via Discord adapter (WS) - no webhook URL needed
    if self.gateway_runner:
        try:
            from gateway.config import Platform
            target_platform = Platform("discord")
            adapter = self.gateway_runner.adapters.get(target_platform)
            if adapter and adapter.is_connected:
                chat_id = extra.get("chat_id", "")
                if not chat_id:
                    home = self.gateway_runner.config.get_home_channel(target_platform)
                    if home:
                        chat_id = home.chat_id
                
                if chat_id:
                    metadata = None
                    thread_id = extra.get("message_thread_id") or extra.get("thread_id")
                    if thread_id:
                        metadata = {"thread_id": thread_id}
                    
                    result = await adapter.send(chat_id, content, metadata=metadata)
                    if result.success:
                        logger.info("[webhook] Delivered to Discord via WS adapter")
                        return result
                    else:
                        logger.warning(f"[webhook] Discord WS adapter failed: {result.error}, falling back to webhook")
        except Exception as e:
            logger.debug(f"[webhook] Discord WS adapter not available: {e}")
    
    # FALLBACK: HTTP webhook URL (requires manual config)
    webhook_url = extra.get("webhook_url", "")
    if not webhook_url:
        channel_id = extra.get("channel_id", "")
        if channel_id:
            import os
            env_key = f"DISCORD_WEBHOOK_{channel_id}"
            webhook_url = os.getenv(env_key, "")
        if not webhook_url:
            webhook_url = os.getenv("DISCORD_DEFAULT_WEBHOOK_URL", "")
    
    if not webhook_url:
        logger.error("[webhook] discord delivery missing webhook_url in deliver_extra or env, and WS adapter not available")
        return SendResult(
            success=False, 
            error="Missing webhook_url. Add to route's deliver_extra, set DISCORD_DEFAULT_WEBHOOK_URL env var, or ensure Discord WS adapter is connected."
        )
    
    # ... rest of HTTP webhook delivery (unchanged)
```

**Priority order (automatic):**
1. **Discord Bot WS** (connected via Gateway) — zero config, preferred
2. **HTTP Webhook** (manual URL) — fallback only

This eliminates the "404: Not Found" error when webhook URLs aren't configured, since the WS bot is already running.

## Thread Persistence Schema

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

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `guild_threads` intent error | Use `guilds=True` (includes threads), not `guild_threads=True` |
| Slash commands not appearing | Kick/re-invite bot, or `./deploy.sh restart` |
| Gateway connection failed | Verify Hermes Gateway running on `:8642` (`curl localhost:8642/health`) |
| **Interaction timeout ("Unknown interaction")** | **Long operations (>3s) in slash commands expire the interaction token. Fix: Use `interaction.response.send_message()` immediately, then run async work in background task, then `interaction.followup.send()` when done.** |
| Permissions errors | Verify bot has `Manage Threads`, `Manage Channels` |
| Voice not working | Install `PyNaCl` + `davey` in venv, `ffmpeg` on system |
| TTS not speaking | Check `edge-tts` installed, `ffmpeg` in PATH, voice channel connected |
| STT not transcribing | Verify `stt.provider: openai` in Hermes Gateway config, API key set |
| "404: Not Found" on webhook | WS fallback handles it — ensure Discord bot is running and connected |
| **Real-time voice receive (STT) not working** | `discord.py[voice]` NOT installed — run `pip install "discord.py[voice]"` in venv. Current `VOICE_RECV_AVAILABLE = False` blocks `HermesAudioSink`. |
| **Bot ignores image attachments** | `on_message` doesn't process `message.attachments`. Need pipeline: download → vision tool → response. |
| **Generated images not sent to Discord** | Gateway creates image but bot doesn't `channel.send(file=discord.File(...))`. Add `/hermes image generate` command. |
| **Podcast audio not delivered** | Grows MP3 but doesn't upload as attachment nor play in voice. Add `deliver: "discord_file"` or `deliver: "voice_channel"` option. |
| **File upload/download via Discord** | No `/hermes file upload/download` commands. Need implementation. |

## Interaction Timeout Pattern (Critical for Slash Commands)

### Problem
Discord slash commands have a **3-second timeout** for responding to interactions. If your command handler takes longer than 3 seconds (e.g., `await channel.connect()`, HTTP calls, heavy processing), the interaction token expires and Discord returns `NotFound: 404 Unknown interaction (error code: 10062)`.

### Broken Pattern ❌
```python
@discord.app_commands.command(name="voice")
async def cmd_voice(interaction, action, channel):
    await interaction.response.defer(ephemeral=True)  # Starts 3s clock
    if action == "join":
        await target_channel.connect()  # Takes 2-5s → TIMEOUT!
        await interaction.followup.send("Connected!")  # FAILS: token expired
```

### Fixed Pattern ✅
```python
@discord.app_commands.command(name="voice")
async def cmd_voice(interaction, action, channel):
    bot = interaction.client
    
    if action == "join":
        # IMMEDIATE response (resets interaction timer)
        await interaction.response.send_message(f"🔊 Conectando a {channel.mention}...", ephemeral=True)
        
        # Background task for long operation
        async def connect_voice():
            try:
                await target_channel.connect()
                await interaction.followup.send(f"✅ Conectado a {channel.mention}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)
        
        asyncio.create_task(connect_voice())
        return  # Command returns immediately
    
    # For fast actions, defer is fine
    await interaction.response.defer(ephemeral=True)
    # ... rest of handling
```

### Key Rules

| Scenario | Pattern |
|----------|---------|
| **Fast operations** (< 500ms) | `defer()` + `followup` (standard) |
| **Long operations** (> 2s) | `response.send_message()` immediate → background task → `followup` |
| **Mixed** (some fast, some slow) | Branch by action: fast = defer, slow = immediate response + task |
| **Background task errors** | Always wrap in try/except, use `interaction.followup.send()` for error |

### Why This Works
1. `interaction.response.send_message()` **acknowledges** the interaction immediately
2. Discord considers the interaction "responded" — no 3s timeout
3. Background task runs independently (no timeout)
4. `interaction.followup.send()` can be called anytime after initial response
5. Works for any long operation: voice connect, HTTP calls, file processing, deployments

### Voice Command Example (Full)
```python
@discord.app_commands.command(name="voice")
async def cmd_voice(interaction, action: str, channel: discord.VoiceChannel = None):
    bot = interaction.client
    target = channel or interaction.user.voice?.channel
    
    if action == "join":
        if not target:
            return await interaction.response.send_message("❌ Enter a voice channel first", ephemeral=True)
        
        # Immediate acknowledgment
        await interaction.response.send_message(f"🔊 Conectando a {target.mention}...", ephemeral=True)
        
        # Async connect in background
        async def do_connect():
            try:
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(target)
                else:
                    await target.connect()
                bot.voice_listening[interaction.guild.id] = True
                await interaction.followup.send(f"✅ Conectado a {target.mention}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Falha: {e}", ephemeral=True)
        
        asyncio.create_task(do_connect())
        return
    
    # Fast actions: defer is fine
    await interaction.response.defer(ephemeral=True)
    # ... handle leave, speak, listen, status
```

## References

- `references/architecture.md` — Detailed architecture diagram and data flows
- `references/slash-commands.md` — Complete slash command registry
- `references/thread-management.md` — ThreadSession lifecycle and persistence
- `references/ui-components.md` — View/Select/Modal/Button patterns
- `references/auto-provisioning.md` — Structure creation logic
- `references/background-tasks.md` — Automation task implementations
- `references/webhook-outbound.md` — Discord webhook delivery from Gateway
- `references/interaction-timeout-pattern.md` — Discord interaction timeout (3s) fix pattern for long-running slash commands
- `references/resilience-layer.md` — Circuit breakers, message queue, fallback chain, health checks, sync managers, systemd watchdog
- `references/troubleshooting.md` — Common issues and fixes
- `references/discord-image-file-handling.md` — **NEW**: Image receive/analyze/generate, file upload/download, podcast audio delivery, voice receive (STT) gap
- `templates/.env.template` — Configuration template
- `templates/hermes-discord-bot.service` — systemd unit template
- `scripts/deploy.sh` — Management script
- `scripts/test-gateway.py` — Gateway connectivity test