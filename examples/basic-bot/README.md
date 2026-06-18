# Basic Discord Bot Example

Minimal Hermes skill for a Discord bot with slash commands.

## Structure

```
examples/basic-bot/
├── skill/
│   ├── SKILL.md
│   └── scripts/
│       └── bot.py
├── .env.example
└── README.md
```

## Quick Test

```bash
cd examples/basic-bot
cp .env.example .env.local
# Edit .env.local with your bot token
python3 skill/scripts/bot.py
```

## Files

### skill/SKILL.md
```markdown
---
name: basic-discord-bot
description: "Minimal Discord bot with slash commands for Hermes"
version: 1.0.0
tags: [discord, bot, slash-commands, example]
---

# Basic Discord Bot

Minimal example of a Discord bot running on Hermes Agent.

## Commands

- `/ping` — Replies with "Pong!"
- `/echo <text>` — Echoes back the text
- `/info` — Shows bot info

## Usage

Install as Hermes skill:

```bash
hermes skills install ./skill --name basic-discord-bot
```

Or run directly:

```bash
export DISCORD_BOT_TOKEN=your-token
python3 scripts/bot.py
```
```

### skill/scripts/bot.py
```python
#!/usr/bin/env python3
"""
Minimal Discord bot with slash commands.
Run: python3 bot.py
Requires: discord.py (pip install discord.py)
"""

import os
import discord
from discord import app_commands

# Load config
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not set")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

@tree.command(name="echo", description="Echoes back your text")
@app_commands.describe(text="Text to echo")
async def echo(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"You said: {text}")

@tree.command(name="info", description="Shows bot info")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Basic Discord Bot",
        description="Minimal example for Hermes Discord Toolkit",
        color=0x5865F2
    )
    embed.add_field(name="Latency", value=f"{client.latency*1000:.0f}ms")
    embed.add_field(name="Guilds", value=len(client.guilds))
    await interaction.response.send_message(embed=embed)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Slash commands synced")

if __name__ == "__main__":
    client.run(BOT_TOKEN)
```

### .env.example
```bash
DISCORD_BOT_TOKEN={{DISC...n
```

### README.md
```markdown
# Basic Discord Bot Example

Minimal Discord bot with slash commands for Hermes Agent.

## Run locally

```bash
cd examples/basic-bot
cp .env.example .env.local
# Edit .env.local with your bot token
pip install discord.py
python3 skill/scripts/bot.py
```

## Install as Hermes Skill

```bash
hermes skills install ./skill --name basic-discord-bot
```

## Commands

| Command | Description |
|---------|-------------|
| `/ping` | Replies with "Pong!" |
| `/echo <text>` | Echoes back text |
| `/info` | Shows bot latency and guild count |
```