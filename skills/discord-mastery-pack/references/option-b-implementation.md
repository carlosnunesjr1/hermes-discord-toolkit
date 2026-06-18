# Option B Implementation — Complete Discord Gateway Bot Deployment

**Session:** 2026-06-16 | **Status:** ✅ Validated E2E

---

## Project Structure

```
/home/carlos/hermes-discord-bot/
├── bot.py                 # Main bot - discord.py 2.7, slash commands, events
├── config.py              # Environment config + slash command definitions
├── gateway_client.py      # Async HTTP client → Hermes Gateway (localhost:8642)
├── thread_manager.py      # Thread ↔ Hermes session mapping
├── deploy.sh              # Install/update/manage script (systemd + venv)
├── service/
│   └── hermes-discord-bot.service  # systemd unit (hardened)
├── requirements.txt       # discord.py>=2.3, aiohttp>=3.9, python-dotenv, pyyaml
├── .env                   # DISCORD_BOT_TOKEN, DISCORD_APP_ID, DISCORD_GUILD_ID, HERMES_GATEWAY_URL
├── .env.template          # Template for new deployments
└── README.md              # Full documentation
```

---

## bot.py — Key Components

### Intents (Fixed)
```python
INTENTS = discord.Intents(
    guilds=True,           # Includes threads (guild_threads INVALID)
    guild_messages=True,
    message_content=True,
    dm_messages=True,
    reactions=True,
    members=True,
)
```

### Bot Class
```python
class HermesDiscordBot(commands.Bot):
    def __init__(self, config: BotConfig):
        self.config = config
        self.gateway = get_gateway_client(config.gateway_url)
        self.thread_manager = get_thread_manager(self)
        self._synced = False
        
        super().__init__(
            command_prefix="!",
            intents=INTENTS,
            application_id=config.app_id,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, roles=False, users=True, replied_user=True
            ),
        )
```

### Event Handlers
| Event | Handler | Purpose |
|-------|---------|---------|
| `on_ready` | Sync slash commands to guild, log readiness | Startup confirmation |
| `on_message` | Handle mentions, route to thread sessions | DM + mention inbound |
| `on_thread_create` | Register Hermes session for new thread | Auto-session binding |
| `on_thread_delete` | Cleanup thread session mapping | Memory management |
| `on_reaction_add` | Reaction controls (✅❌🔄📋) | Interactive controls |

---

## gateway_client.py — Hermes Gateway Integration

### HTTP Client Pattern
```python
class GatewayClient:
    def __init__(self, base_url: str = "http://localhost:8642"):
        self.base_url = base_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300),
                headers={"Content-Type": "application/json"}
            )
    
    async def chat(self, payload: dict) -> dict:
        await self.ensure_session()
        async with self.session.post(f"{self.base_url}/v1/agent/chat", json=payload) as resp:
            return await resp.json()
```

### Request Payload Format
```json
{
  "platform": "discord",
  "user_id": "123456789012345678",
  "chat_id": "1516397584942370836",
  "thread_id": "987654321098765432",
  "message": "user message content",
  "session_id": "hermes-session-uuid"
}
```

---

## thread_manager.py — Thread ↔ Session Mapping

### Core Logic
```python
class ThreadManager:
    def __init__(self, bot: HermesDiscordBot):
        self.bot = bot
        self._thread_sessions: Dict[int, ThreadSession] = {}
    
    def get_or_create_session(self, thread: discord.Thread) -> ThreadSession:
        if thread.id not in self._thread_sessions:
            self._thread_sessions[thread.id] = ThreadSession(
                thread_id=thread.id,
                channel_id=thread.parent_id,
                session_id=self._generate_session_id()
            )
        return self._thread_sessions[thread.id]
    
    def get_session(self, thread_id: int) -> Optional[ThreadSession]:
        return self._thread_sessions.get(thread_id)
```

### ThreadSession Dataclass
```python
@dataclass
class ThreadSession:
    thread_id: int
    channel_id: int
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
```

---

## deploy.sh — Complete Management Script

### Commands Available
| Command | Action |
|---------|--------|
| `install` | Create venv, install deps, install systemd service |
| `update` | Git pull, update deps, restart service |
| `start` | Start systemd service |
| `stop` | Stop systemd service |
| `restart` | Restart service + status |
| `status` | Show systemd status |
| `logs` | Follow live journalctl |
| `tail [N]` | Last N lines (default 100) |
| `test-gateway` | Test HTTP connection to Hermes Gateway |
| `setup-discord` | Print Discord Developer Portal setup guide |

### Install Flow
```bash
./deploy.sh install
# 1. python3 -m venv venv
# 2. venv/bin/pip install -r requirements.txt
# 3. cp .env.template .env (if missing)
# 4. sudo cp service/hermes-discord-bot.service /etc/systemd/system/
# 5. sudo systemctl daemon-reload && sudo systemctl enable hermes-discord-bot
```

---

## systemd Service — Hardened Configuration

```ini
[Unit]
Description=Hermes Discord Bot - Gateway WebSocket Integration
After=network.target hermes-gateway.service
Wants=hermes-gateway.service

[Service]
Type=simple
User=carlos
Group=carlos
WorkingDirectory=/home/carlos/hermes-discord-bot
Environment=PATH=/home/carlos/hermes-discord-bot/venv/bin:/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/home/carlos/hermes-discord-bot/.env
ExecStart=/home/carlos/hermes-discord-bot/venv/bin/python bot.py
Restart=always
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hermes-discord-bot

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/carlos/hermes-discord-bot
```

---

## Discord Developer Portal — Complete Setup Checklist

### Application Creation
1. https://discord.com/developers/applications → New Application
2. Name: `Hermes Agent` (or preferred)

### Bot Tab
1. **Build-A-Bot** → Create Bot
2. **Reset Token** → Copy → `.env` as `DISCORD_BOT_TOKEN`
3. **Privileged Gateway Intents** → Enable:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MESSAGES INTENT
   - ✅ GUILD MEMBERS INTENT (optional, for member lists)
4. Save Changes

### OAuth2 → URL Generator
1. **Scopes**: ✅ `bot` ✅ `applications.commands`
2. **Bot Permissions**:
   - ✅ Manage Channels
   - ✅ Manage Threads
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
   - ✅ Add Reactions
   - ✅ Manage Messages (optional)
3. Copy URL → Open in browser → Invite to server

### General Information
1. **Application ID** → Copy → `.env` as `DISCORD_APP_ID`

### Discord Client (Dev Mode)
1. User Settings → Advanced → ✅ Developer Mode
2. Right-click server → Copy ID → `.env` as `DISCORD_GUILD_ID`

---

## Slash Command Definitions (config.py)

```python
SLASH_COMMANDS = [
    SlashCommandConfig(
        name="status",
        description="Gateway health + connected adapters",
        handler="cmd_status"
    ),
    SlashCommandConfig(
        name="help",
        description="Lista todos comandos disponíveis",
        handler="cmd_help"
    ),
    SlashCommandConfig(
        name="thread",
        description="Thread management",
        subcommands=[
            SubCommandConfig(name="create", description="Cria thread isolada + sessão Hermes", handler="cmd_thread_create"),
            SubCommandConfig(name="list", description="Lista threads no canal", handler="cmd_thread_list"),
            SubCommandConfig(name="my", description="Lista suas threads", handler="cmd_thread_my"),
            SubCommandConfig(name="archive", description="Arquiva thread atual", handler="cmd_thread_archive"),
        ]
    ),
    SlashCommandConfig(
        name="agent",
        description="Subagent management",
        subcommands=[
            SubCommandConfig(name="spawn", description="Spawna subagent com objetivo", handler="cmd_agent_spawn"),
            SubCommandConfig(name="list", description="Lista agents ativos", handler="cmd_agent_list"),
        ]
    ),
    SlashCommandConfig(
        name="cron",
        description="Cron job management",
        subcommands=[
            SubCommandConfig(name="list", description="Lista cron jobs", handler="cmd_cron_list"),
            SubCommandConfig(name="run", description="Executa cron job manualmente", handler="cmd_cron_run"),
        ]
    ),
    SlashCommandConfig(
        name="deploy",
        description="Trigger deploy (git pull + restart)",
        handler="cmd_deploy"
    ),
    SlashCommandConfig(
        name="skills",
        description="Skills disponíveis no Hermes",
        handler="cmd_skills"
    ),
    SlashCommandConfig(
        name="logs",
        description="Logs recentes do gateway",
        handler="cmd_logs"
    ),
]
```

---

## Reaction Controls Mapping

| Reaction | Action | Implementation |
|----------|--------|----------------|
| ✅ | Approve | Confirm pending action |
| ❌ | Reject | Cancel pending action |
| 🔄 | Restart Gateway | `POST /v1/gateway/restart` |
| 📋 | Show Logs | `GET /v1/gateway/logs?lines=50` |

---

## Validation Results (E2E)

| Test | Result |
|------|--------|
| Service starts | ✅ `systemctl status hermes-discord-bot` → active (running) |
| Gateway WS connects | ✅ Logs show "Shard ID None has connected to Gateway" |
| Slash commands sync | ✅ "Slash commands synced to guild 1516397584942370836" |
| Bot login | ✅ "Logged in as Carlos Alberto Nunes Avatar#6897" |
| Gateway HTTP reachable | ✅ `./deploy.sh test-gateway` → `{"status": "ok", "platform": "hermes-agent", "version": "0.16.0"}` |
| Mention handling | ✅ `@Hermes` in thread routes to session |
| Thread session mapping | ✅ New thread → new Hermes session |
| Reaction handlers | ✅ Registered on bot messages |

---

## Troubleshooting Quick Reference

| Symptom | Check | Fix |
|---------|-------|-----|
| Service fails immediately | `journalctl -u hermes-discord-bot -n 20` | Check intents, token, imports |
| Slash commands not showing | Kick/re-invite bot, or restart service | `./deploy.sh restart` |
| "Unknown interaction" | Bot restarted mid-interaction | Retry command |
| Gateway connection failed | `./deploy.sh test-gateway` | Verify Hermes Gateway on :8642 |
| Voice not working | PyNaCl/davey warnings | `pip install pynacl davey` (optional) |
| Permission errors | Verify bot role has Manage Threads/Channels | Check Discord server settings |

---

## Files for Quick Copy

### .env.template
```bash
# Hermes Discord Bot Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_APP_ID=your_application_id_here
DISCORD_GUILD_ID=your_guild_id_here
HERMES_GATEWAY_URL=http://localhost:8642
LOG_LEVEL=INFO
```

### Minimal requirements.txt
```text
discord.py>=2.3.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
pyyaml>=6.0
```