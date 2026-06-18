# Auto-Provisioning & UI Components Pattern

## Overview
Complete Discord server auto-provisioning on bot startup with rich UI components (Views, Selects, Modals, Buttons) for full command interface.

---

## Auto-Provisioning Architecture

### Structure Definition (AUTO_PROVISION_STRUCTURE)
```python
AUTO_PROVISION_STRUCTURE = {
    "🚀 HERMES-OPS": {
        "deploy": "🚀 Deploys & Releases",
        "monitor": "📊 Monitoramento & Alertas", 
        "incidents": "🚨 Incidentes Ativos",
        "logs": "📋 Logs Centralizados",
    },
    "🔧 CN-TECH": {
        "career-hub": "💼 Career Hub",
        "nexus-pim": "📦 Nexus PIM (Amazon/Tiny)",
        "central-comando": "🎮 Central de Comando",
        "control-daemon": "⚙️ Control Daemon",
    },
    "🏗️ INFRA": {
        "vps-health": "💻 VPS Health & Metrics",
        "docker": "🐳 Containers & Images",
        "network": "🌐 Network & DNS",
        "backups": "💾 Backups & Restore",
    },
    "🤖 AGENTS": {
        "active": "▶️ Agents Ativos",
        "spawn": "➕ Spawnar Novo Agent",
        "history": "📜 Histórico de Agents",
    },
    "📋 TASKS": {
        "features": "✨ Novas Features",
        "bugs": "🐛 Bugs & Hotfixes",
        "research": "🔬 Pesquisa & Spikes",
        "docs": "📝 Documentação",
    },
    "🧠 BRAIN": {
        "memory": "🧠 Memory & Knowledge",
        "context": "📍 Context Inspection",
        "sessions": "💬 Session Management",
        "knowledge": "📚 Knowledge Base",
    },
}
```

### Provisioning Flow (in `_auto_provision_structure()`)
1. **Check permissions** — Requires `Manage Channels` + `Manage Threads`
2. **Create Categories** — With bot-specific overwrites
3. **Create Channels** — In each category with topic + overwrites
4. **Create Initial Thread** — Per channel with bot as owner
5. **Post System Panel** — In key channels (deploy, monitor, spawn, memory)
6. **Mark Complete** — `_auto_provisioned = True` (idempotent)

### Key Implementation: `bot.py:367-488`
```python
async def _auto_provision_structure(self):
    if self._auto_provisioned:
        return
    
    guild = self.get_guild(self.config.guild_id)
    me = guild.me
    
    for cat_name, channels in AUTO_PROVISION_STRUCTURE.items():
        # Find or create category
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=True),
                me: discord.PermissionOverwrite(
                    manage_channels=True, manage_threads=True,
                    send_messages=True, view_channel=True
                ),
            }
            category = await guild.create_category(
                name=cat_name,
                overwrites=overwrites,
                reason="Auto-provisioned by Hermes Bot"
            )
        
        # Create channels in category
        for ch_name, ch_topic in channels.items():
            channel = discord.utils.get(category.text_channels, name=ch_name)
            if not channel:
                channel = await guild.create_text_channel(
                    name=ch_name,
                    category=category,
                    overwrites=overwrites,
                    topic=ch_topic,
                    reason="Auto-provisioned by Hermes Bot"
                )
            
            # Create initial thread
            threads = self.thread_manager.get_sessions_for_channel(channel.id)
            if not threads:
                thread = await self.thread_manager.create_thread(
                    channel=channel,
                    name=f"📋 {ch_topic}",
                    owner=me,
                    message=f"Thread principal de **{ch_topic}**\n..."
                )
            
            # Post system panel in key channels
            if ch_name in ("deploy", "monitor", "spawn", "memory"):
                await self._post_system_panel(channel, cat_name)
    
    self._auto_provisioned = True
```

---

## UI Components

### 1. Select Views (SystemSelectView)
Multi-select dropdowns organized by system domain:
- **HERMES-OPS** — Deploy, Restart, Logs, Status
- **CN-TECH** — Status, Career, Nexus, Central, Control, Sync
- **INFRA** — VPS Health, Docker, Network, Backup, Optimize
- **AGENTS** — Spawn (Modal), List, History
- **TASKS** — New Thread (Modal), My Threads, Channel Threads, Archive
- **BRAIN** — Memory, Context, Sessions, Knowledge, Clear

Each select option maps to gateway command via `gateway_client.py`.

### 2. Modals
**AgentSpawnModal** — Goal, Context, Toolsets
**ThreadCreateModal** — Name, Topic, Category

### 3. Button Views
**DeployConfirmView** — ▶️ Deploy / 📋 Logs / ❌ Cancel
**Reaction Controls** — ✅ Aprovar / ❌ Rejeitar / 🔄 Restart / 📋 Logs / 🧵 Info / 🤖 Agent Status

### 4. System Panel Posting
```python
async def _post_system_panel(self, channel: discord.TextChannel, category: str):
    # Check if already posted (last 10 messages)
    async for msg in channel.history(limit=10):
        if msg.author == self.user and msg.embeds and "Painel de Controle" in (msg.embeds[0].title or ""):
            return
    
    embed = discord.Embed(
        title="🎛️ Painel de Controle Hermes",
        description=f"Sistema: **{category}**\nCanal: {channel.mention}\n\nSelecione abaixo para operar:",
        color=0x0099ff
    )
    await channel.send(embed=embed, view=SystemSelectView(self))
```

---

## Background Automation Tasks

Started in `on_ready()` after provisioning:

| Task | Interval | Function |
|------|----------|----------|
| `_monitor_system_events` | 60s | Scan gateway logs for ERROR/FATAL/CRITICAL → auto-create alert threads in #incidents |
| `_cleanup_inactive_threads` | 1h | Remove threads > 1 week inactive |
| `_sync_thread_sessions` | 5min | Ensure Hermes sessions linked to active threads |

### Alert Thread Auto-Creation
```python
async def _check_gateway_alerts(self):
    result = await self.gateway.get_logs(100)
    logs = result.get("logs", "")
    
    alert_keywords = [
        ("ERROR", "🔴"), ("FATAL", "💀"), ("CRITICAL", "🚨"),
        ("Exception", "⚠️"), ("Traceback", "🔥"),
        ("OutOfMemory", "💾"), ("Connection refused", "🔌"), ("Timeout", "⏱️"),
    ]
    
    for keyword, emoji in alert_keywords:
        if keyword.lower() in logs.lower():
            existing = self._find_alert_thread(keyword)
            if not existing:
                await self._create_alert_thread(keyword, emoji, logs)
                break  # One per cycle
```

---

## Thread Persistence with Session Preservation

### ThreadManager Enhancements (`thread_manager.py`)

**Persistence File:** `~/.hermes/discord_threads.json`

**ThreadSession Dataclass:**
```python
@dataclass
class ThreadSession:
    thread_id: int
    channel_id: int
    guild_id: int
    owner_id: int
    hermes_session_id: Optional[str] = None  # KEY: preserves Hermes context
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    topic: str = ""
    is_active: bool = True
```

**Archive with Session Preservation:**
```python
async def archive_thread_by_id(self, thread_id: int, reason: str = "Archived via Hermes") -> bool:
    session = self.get_session(thread_id)
    if session and session.hermes_session_id:
        logger.info(f"Preserving Hermes session {session.hermes_session_id} for archived thread {thread_id}")
    
    await thread.edit(archived=True, reason=reason)
    self.archive_thread(thread_id)
    self._save_persistence()
    return True
```

**Auto-Restore on Unarchive:**
```python
def unarchive_thread(self, thread_id: int) -> bool:
    if thread_id in self._threads:
        self._threads[thread_id].is_active = True
        self._threads[thread_id].last_activity = datetime.now()
        
        if self._threads[thread_id].hermes_session_id:
            logger.info(f"Thread {thread_id} unarchived, Hermes session {self._threads[thread_id].hermes_session_id} will be restored")
        
        self._save_persistence()
        return True
    return False
```

**Event Handlers:**
```python
async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
    if before.archived != after.archived:
        if after.archived:
            self.thread_manager.archive_thread(after.id)
        else:
            self.thread_manager.unarchive_thread(after.id)

async def _handle_thread_message(self, message: discord.Message):
    session = self.thread_manager.get_session(thread.id)
    if not session:
        return
    
    # Auto-unarchive if archived thread receives message
    if not session.is_active:
        self.thread_manager.unarchive_thread(thread.id)
    
    # Forward with Hermes session ID
    payload = self._build_interaction_payload(
        message,
        hermes_session_id=session.hermes_session_id
    )
```

---

## Webhook Outbound Discord Delivery

Added to `gateway/platforms/webhook.py`:

```python
async def _deliver_discord_webhook(self, content: str, delivery: dict) -> SendResult:
    """Deliver message to Discord via webhook URL."""
    import aiohttp
    
    extra = delivery.get("deliver_extra", {})
    webhook_url = extra.get("webhook_url", "")
    
    # Allow channel_id -> webhook_url mapping via env
    if not webhook_url:
        channel_id = extra.get("channel_id", "")
        if channel_id:
            import os
            env_key = f"DISCORD_WEBHOOK_{channel_id}"
            webhook_url = os.getenv(env_key, "")
            if not webhook_url:
                webhook_url = os.getenv("DISCORD_DEFAULT_WEBHOOK_URL", "")
    
    if not webhook_url:
        return SendResult(success=False, error="Missing webhook_url")
    
    payload = {
        "content": content[:2000],
        "username": "Hermes",
        "avatar_url": "https://cdn.discordapp.com/avatars/BOT_ID/avatar.png"
    }
    
    thread_id = extra.get("thread_id") or extra.get("message_thread_id")
    if thread_id:
        payload["thread_id"] = thread_id
    
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status in (200, 204):
                return SendResult(success=True)
            else:
                text = await resp.text()
                return SendResult(success=False, error=f"HTTP {resp.status}: {text}")
```

**Config Example:**
```yaml
# config.yaml
webhook:
  extra:
    routes:
      deploy-status:
        secret: "deploy-secret"
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"
          # OR via env: DISCORD_WEBHOOK_CHANNELID=...
```

---

## Gateway Integration Workaround

Since `/v1/discord/interaction` endpoint doesn't exist in Hermes Gateway, the Discord bot uses existing endpoints:

```python
# gateway_client.py - forward_interaction()
async def forward_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Option A: Spawn agent directly (current)
    return await self.spawn_agent(
        goal=payload.get("message", ""),
        context=f"Discord interaction from user {payload.get('user_id')}",
        toolsets=["terminal", "file", "web", "browser", "coding"]
    )
    
    # Option B: Use /v1/agent/chat if implemented
    # return await self._request("POST", "/v1/agent/chat", json=payload)
```

---

## Deployment Checklist

- [ ] Bot has `Manage Channels` + `Manage Threads` permissions
- [ ] `AUTO_PROVISION_STRUCTURE` matches desired categories/channels
- [ ] System panel posts in key channels on startup
- [ ] Background tasks started (monitor, cleanup, sync)
- [ ] Thread persistence file created at `~/.hermes/discord_threads.json`
- [ ] Webhook URLs configured in env for outbound delivery
- [ ] Reaction handlers registered for ✅❌🔄📋🧵🤖
- [ ] Gateway integration via `/v1/agents/spawn` working