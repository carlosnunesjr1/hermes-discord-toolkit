# Discord UI Components (Views, Selects, Buttons, Modals)

## Overview

All interactive UI built with `discord.ui` components. Views are persistent (attached to messages) and survive bot restarts via `custom_id` registration.

## Architecture

```
Interaction (User clicks/selects)
    │
    ▼
bot.py → View callback (registered via custom_id)
    │
    ▼
Gateway Client → Hermes Gateway API
    │
    ▼
Response → Edit original interaction / Followup / New message
```

## View Classes

### 1. HermesPanelView (`HermesPanelView`)

**Purpose**: Main control panel with 4 Select menus + action buttons.

**Components**:
```python
class HermesPanelView(discord.ui.View):
    def __init__(self, bot, current_channel=None):
        super().__init__(timeout=None)  # Persistent
        
        # Systems Select
        self.add_item(SystemsSelect(bot))
        
        # Actions Select  
        self.add_item(ActionsSelect(bot))
        
        # Channels Select
        self.add_item(ChannelsSelect(bot, current_channel))
        
        # Agents Select
        self.add_item(AgentsSelect(bot))
        
        # Quick Action Buttons
        self.add_item(DeployButton())
        self.add_item(LogsButton())
        self.add_item(RestartButton())
```

**SystemsSelect Options**:
```python
SYSTEMS = [
    discord.SelectOption(label="Gateway Status", value="gateway_status", emoji="🌐"),
    discord.SelectOption(label="CN Tech", value="cntech_status", emoji="🔧"),
    discord.SelectOption(label="VPS Health", value="vps_health", emoji="🏗️"),
    discord.SelectOption(label="Workspace", value="workspace_status", emoji="💻"),
    discord.SelectOption(label="Brain", value="brain_status", emoji="🧠"),
]
```

**Callback Flow**:
```
User selects "CN Tech" → SystemsSelect.callback()
    → gateway_client.get("/v1/cntech/status")
    → Build embed with service table
    → interaction.response.edit_message(embed=embed, view=self)
```

### 2. DeployView (`DeployView`)

**Purpose**: Deploy confirmation with progress updates.

**Components**:
```python
class DeployView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.add_item(DeployButton())      # ▶️ Deploy
        self.add_item(CancelButton())      # ❌ Cancel
        self.add_item(LogsButton())        # 📋 Logs
```

**DeployButton Callback**:
```python
async def callback(self, interaction):
    # Disable buttons
    for item in self.children: item.disabled = True
    await interaction.response.edit_message(view=self)
    
    # Start deploy
    result = await bot.gateway.post("/v1/deploy")
    
    # Update with progress
    embed = discord.Embed(title="🚀 Deploying...", description=result.get("message"))
    await interaction.edit_original_response(embed=embed)
    
    # Poll for completion
    while True:
        status = await bot.gateway.get("/v1/deploy/status")
        if status["done"]:
            break
        await asyncio.sleep(5)
        await interaction.edit_original_response(embed=progress_embed)
    
    # Final result with Rollback button if failed
    if status["success"]:
        embed = success_embed
    else:
        embed = fail_embed
        self.add_item(RollbackButton())  # 🔄 Rollback
    await interaction.edit_original_response(embed=embed, view=self)
```

### 3. AgentSpawnModal (`AgentSpawnModal`)

**Purpose**: Spawn subagent with goal, toolsets, context.

**Modal Fields**:
```python
class AgentSpawnModal(discord.ui.Modal, title="Spawn Subagent"):
    goal = discord.ui.TextInput(
        label="Goal",
        style=discord.TextStyle.paragraph,
        placeholder="What should the agent accomplish?",
        required=True,
        max_length=2000
    )
    toolsets = discord.ui.TextInput(
        label="Toolsets (comma-separated)",
        placeholder="terminal,file,web,browser,coding,skills",
        required=False,
        max_length=500
    )
    context = discord.ui.TextInput(
        label="Additional Context",
        style=discord.TextStyle.paragraph,
        placeholder="Any extra context for the agent...",
        required=False,
        max_length=1000
    )
```

**Submit Callback**:
```python
async def on_submit(self, interaction):
    toolsets = [t.strip() for t in self.toolsets.value.split(",")] if self.toolsets.value else []
    result = await interaction.client.gateway.post("/v1/agent/spawn", {
        "goal": self.goal.value,
        "toolsets": toolsets,
        "context": self.context.value
    })
    await interaction.response.send_message(
        f"✅ Agent spawned: `{result['agent_id']}`\nGoal: {self.goal.value[:100]}",
        ephemeral=True
    )
```

### 4. ThreadCreateModal (`ThreadCreateModal`)

**Purpose**: Create new thread with name, topic, channel.

**Fields**:
```python
class ThreadCreateModal(discord.ui.Modal, title="Create Thread"):
    name = discord.ui.TextInput(
        label="Thread Name",
        placeholder="e.g., bug-login-loop",
        required=True,
        max_length=100
    )
    topic = discord.ui.TextInput(
        label="Topic/Description",
        style=discord.TextStyle.paragraph,
        placeholder="What is this thread about?",
        required=False,
        max_length=500
    )
    channel = discord.ui.TextInput(
        label="Channel (optional, defaults to current)",
        placeholder="#deploy or leave empty",
        required=False,
        max_length=100
    )
```

### 5. IncidentActionView (`IncidentActionView`)

**Purpose**: Actions for auto-created incident threads.

**Buttons**:
```python
class IncidentActionView(discord.ui.View):
    def __init__(self, bot, thread_id):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        
        self.add_item(InvestigateButton(thread_id))    # 🔍
        self.add_item(LogsButton(thread_id))           # 📋
        self.add_item(RestartGatewayButton(thread_id)) # 🔄
        self.add_item(ResolveButton(thread_id))        # ✅
```

**InvestigateButton**:
```python
async def callback(self, interaction):
    bot = interaction.client
    await bot.gateway.post("/v1/agent/spawn", {
        "goal": f"Investigate incident in thread {self.thread_id}. Analyze gateway logs, find root cause, propose fix.",
        "toolsets": ["terminal", "file", "web", "skills"]
    })
    await interaction.response.send_message("🔍 Investigation agent spawned.", ephemeral=True)
```

### 6. Reaction Controls (Message-based)

**Not Views** — uses raw reactions on bot messages.

**Reaction Map**:
| Emoji | Custom ID | Action |
|-------|-----------|--------|
| ✅ | `approve` | Confirm deploy/action |
| ❌ | `reject` | Cancel deploy/action |
| 🔄 | `restart_gateway` | `sudo systemctl restart hermes-gateway` |
| 📋 | `show_logs` | Show last 50 gateway log lines |
| 🧵 | `thread_info` | Show thread metadata (session, owner, age) |
| 🤖 | `agent_status` | Show active agents in this thread |

**Handler** (`on_raw_reaction_add`):
```python
async def on_raw_reaction_add(self, payload):
    if payload.user_id == self.user.id: return
    if payload.emoji.name not in REACTION_ACTIONS: return
    
    message = await channel.fetch_message(payload.message_id)
    if message.author.id != self.user.id: return  # Only on bot messages
    
    action = REACTION_ACTIONS[payload.emoji.name]
    await action.execute(self, payload)
```

## Persistent Views

### Registration (in `on_ready`)
```python
# Register persistent views for custom_id handling
self.add_view(HermesPanelView(self))
self.add_view(DeployView(self))
self.add_view(IncidentActionView(self, thread_id=0))  # thread_id filled at runtime
```

### Custom ID Format
```
view_name:action:param
examples:
  "panel:systems:cntech_status"
  "deploy:confirm"
  "incident:investigate:1516641040352673924"
  "agent:logs:abc123"
```

## Embed Builders

### Standard Colors
```python
COLORS = {
    "success": discord.Color.green(),
    "error": discord.Color.red(),
    "warning": discord.Color.orange(),
    "info": discord.Color.blue(),
    "deploy": discord.Color.purple(),
    "agent": discord.Color.teal(),
}
```

### Panel Embed Template
```python
def build_panel_embed(title, description, fields=None):
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS["info"],
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Hermes Agent", icon_url=BOT_AVATAR_URL)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed
```

### Service Status Embed
```python
def build_service_embed(services):
    embed = discord.Embed(title="🔧 CN Tech Services", color=COLORS["info"])
    for svc in services:
        status_emoji = "🟢" if svc["healthy"] else "🔴"
        embed.add_field(
            name=f"{status_emoji} {svc['name']}",
            value=f"Container: `{svc['container']}`\nPort: {svc['port']}\nUptime: {svc['uptime']}",
            inline=True
        )
    return embed
```

## Interaction Response Patterns

### 1. Ephemeral (User-only)
```python
await interaction.response.send_message("Done!", ephemeral=True)
```

### 2. Edit Original (Update panel)
```python
await interaction.response.edit_message(embed=new_embed, view=self)
```

### 3. Deferred + Followup (Long operations)
```python
await interaction.response.defer(ephemeral=True)
# ... do work ...
await interaction.followup.send("Complete!", ephemeral=True)
```

### 4. Modal Submit
```python
await interaction.response.send_message("Submitted!", ephemeral=True)
```

## Code Organization

```
bot.py
├── class HermesDiscordBot
├── class HermesPanelView(View)
├── class DeployView(View)
├── class IncidentActionView(View)
├── class AgentSpawnModal(Modal)
├── class ThreadCreateModal(Modal)
├── SystemsSelect(Select)
├── ActionsSelect(Select)
├── ChannelsSelect(Select)
├── AgentsSelect(Select)
├── DeployButton(Button)
├── CancelButton(Button)
├── LogsButton(Button)
├── RollbackButton(Button)
├── InvestigateButton(Button)
├── RestartGatewayButton(Button)
├── ResolveButton(Button)
└── REACTION_ACTIONS dict + on_raw_reaction_add()
```

## Best Practices

1. **Always `timeout=None`** for persistent views
2. **Register views in `on_ready`** for custom_id handling
3. **Use `ephemeral=True`** for user-specific responses
4. **Disable buttons after click** to prevent double-submit
5. **Catch `discord.NotFound`** for deleted messages
6. **Use `defer()`** for operations > 3 seconds
7. **Prefixed custom_ids** for easy routing
8. **Separate View classes** per interaction type