# Auto-Provisioning Discord Structure

## Overview

On bot startup (`on_ready`), the `_auto_provision_structure()` method creates the complete Discord organization: categories, channels, threads, and initial messages. This runs idempotently — safe to run multiple times.

## Structure Definition

```python
STRUCTURE = {
    "🚀 HERMES-OPS": {
        "deploy": "🚀 Deploys & Releases",
        "monitor": "📊 Monitoring & Alerts", 
        "incidents": "🔴 Incidents & Hotfixes",
        "logs": "📋 Gateway & System Logs",
    },
    "🔧 CN-TECH": {
        "career-hub": "💼 Career Hub Service",
        "nexus-pim": "📦 Nexus PIM (Amazon Sync)",
        "nectar": "🍯 Nectar Summo",
        "central-comando": "🎛️ Central de Comando",
        "control-daemon": "⚙️ Control Daemon",
        "redis": "🗄️ Redis Cache",
    },
    "🧱 WORKSPACE": {
        "workspace": "🧱 Hermes Workspace",
        "dashboard": "📊 Hermes Dashboard",
        "gateway": "🌐 Hermes Gateway",
        "webhook": "🔗 Webhook Receiver",
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

## Provisioning Algorithm

### 1. Get/Create Categories
```python
for category_name in STRUCTURE:
    category = discord.utils.get(guild.categories, name=category_name)
    if not category:
        category = await guild.create_category(category_name)
        log(f"Created category: {category_name}")
```

### 2. Get/Create Channels
```python
for channel_name, topic in STRUCTURE[category_name].items():
    channel = discord.utils.get(category.text_channels, name=channel_name)
    if not channel:
        channel = await category.create_text_channel(
            name=channel_name,
            topic=topic,
            reason="Hermes auto-provisioning"
        )
        log(f"Created channel: {channel_name}")
```

### 3. Create Initial Thread (with panel)
```python
thread_name = f"📋 {topic.split(' ')[-1]}"  # e.g., "📋 Deploys"
thread = await thread_manager.create_thread(
    channel=channel,
    name=thread_name,
    owner=bot.user,
    message=f"## {topic}\n\nInitial thread for **{channel_name}**. Use `@Hermes` here."
)
```

### 4. Post Panel Message in Thread
```python
embed = build_channel_embed(channel_name, topic)
view = HermesPanelView(bot, channel_name)
await thread.send(embed=embed, view=view)
```

### 5. Set Permissions (Optional)
```python
# Restrict @everyone from sending in control channels
if channel_name in CONTROL_CHANNELS:
    await channel.set_permissions(
        guild.default_role,
        send_messages=False,
        send_messages_in_threads=False
    )
```

## Idempotency Guarantees

| Resource | Check | Action if Exists |
|----------|-------|------------------|
| Category | `guild.categories` by name | Reuse |
| Channel | `category.text_channels` by name | Reuse |
| Thread | `channel.threads` by name prefix | Reuse (or create new if archived) |
| Panel Message | Last bot message in thread | Update if stale |

## Error Handling

| Failure | Recovery |
|---------|----------|
| Missing `Manage Channels` | Log warning, skip channel creation |
| Missing `Manage Threads` | Log warning, skip thread creation |
| Rate limit (429) | Exponential backoff, retry |
| Discord API error | Log, continue with next item |

## Configuration Constants

```python
# Maximum threads per channel (Discord limit: 1000 active, but practical)
MAX_THREADS_PER_CHANNEL = 50

# Panel refresh interval (if message older than this, update)
PANEL_TTL_HOURS = 24

# Channels that get restricted permissions
CONTROL_CHANNELS = {"deploy", "incidents", "monitor"}

# Channels that get webhook creation
WEBHOOK_CHANNELS = {
    "deploy": "Hermes Deploy",
    "monitor": "Hermes Alerts",
    "incidents": "Hermes Incidents",
}
```

## Post-Provisioning

After structure creation:
1. Starts background automation tasks
2. Logs completion: `✅ Auto-provisioning complete`
3. Logs: `🔄 Background automation tasks started`

## Testing

```bash
# Force re-provision (delete channels first)
# Then restart bot: ./deploy.sh restart

# Or call manually in Discord:
# (Not exposed as command currently - could add /hermes admin reprovision)
```

## Customization

To modify structure:
1. Edit `STRUCTURE` dict in `bot.py`
2. Restart bot: `./deploy.sh restart`
3. Bot will create missing items, preserve existing

## Permissions Required

Bot needs these permissions for auto-provisioning:
- `Manage Channels` — create categories/channels
- `Manage Threads` — create threads
- `Send Messages` — post panel messages
- `Embed Links` — panel embeds
- `Read Message History` — check existing threads
- `Manage Messages` — update panel messages

## Observability

Logs created:
```
Created category: 🚀 HERMES-OPS
Created channel: 🚀 HERMES-OPS > #deploy
Thread created: 📋 🚀 Deploys (ID: 1516641040352673924)
Registered thread 1516641040352673924 for user 1516328637526179870
✅ Auto-provisioning complete
```

Total: ~24 channels + 24 threads in ~10 seconds on fresh server.