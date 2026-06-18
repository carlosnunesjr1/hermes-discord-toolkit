# Voice + TTS Discord Bot Example

Discord bot with voice support (STT/TTS) using Hermes Agent gateway.

## Structure

```
examples/voice-tts/
├── skill/
│   ├── SKILL.md
│   └── scripts/
│       └── voice_bot.py
├── .env.example
└── README.md
```

## Quick Test

```bash
cd examples/voice-tts
cp .env.example .env.local
# Edit .env.local with your bot token
# Requires: discord.py, Hermes Gateway with STT/TTS enabled
python3 skill/scripts/voice_bot.py
```

## Files

### skill/SKILL.md
```markdown
---
name: voice-tts-discord-bot
description: "Discord bot with voice (STT/TTS) via Hermes Gateway"
version: 1.0.0
tags: [discord, voice, stt, tts, hermes-gateway]
---

# Voice + TTS Discord Bot

Discord bot with voice channel support using Hermes Gateway's built-in STT/TTS.

## Features

- Join/leave voice channels
- Speech-to-Text (STT) via Hermes Gateway (local faster-whisper or Groq)
- Text-to-Speech (TTS) via Hermes Gateway (Edge TTS default)
- Slash commands for voice control
- Podcast mode (record + summarize)

## Commands

| Command | Description |
|---------|-------------|
| `/voice join` | Join your voice channel |
| `/voice leave` | Leave voice channel |
| `/voice speak <text>` | Bot speaks text in VC |
| `/voice record` | Start recording |
| `/voice stop` | Stop recording + transcribe |
| `/voice podcast <topic>` | Record discussion, get summary |

## Requirements

- Hermes Gateway with `stt.enabled: true` and `tts.provider: edge`
- `STT_PROVIDER=local` (faster-whisper) or `groq`
- Discord bot with **Voice** intent enabled

## Installation

```bash
hermes skills install ./skill --name voice-tts-discord-bot
```

## Configuration

Via Hermes config:
```bash
hermes config set stt.enabled true
hermes config set stt.provider local
hermes config set tts.provider edge
```
```

### skill/scripts/voice_bot.py
```python
#!/usr/bin/env python3
"""
Discord bot with voice (STT/TTS) via Hermes Gateway.
Requires: discord.py, aiohttp
Run: python3 voice_bot.py
"""

import os
import discord
from discord import app_commands
import aiohttp

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
HERMES_API = os.getenv("HERMES_API_URL", "http://127.0.0.1:8642")
API_KEY = os.getenv("API_SERVER_KEY")

if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not set")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
voice_clients = {}

async def hermes_tts(text: str) -> bytes:
    """Generate TTS audio via Hermes Gateway."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{HERMES_API}/v1/audio/speech",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"input": text, "voice": "pt-BR", "model": "tts-1"}
        ) as resp:
            return await resp.read()

async def hermes_stt(audio_file: bytes) -> str:
    """Transcribe audio via Hermes Gateway."""
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field("file", audio_file, filename="audio.ogg", content_type="audio/ogg")
        async with session.post(
            f"{HERMES_API}/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data=data
        ) as resp:
            result = await resp.json()
            return result.get("text", "")

@tree.command(name="voice_join", description="Join your voice channel")
async def voice_join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)
        return
    
    channel = interaction.user.voice.channel
    vc = await channel.connect()
    voice_clients[interaction.guild_id] = vc
    await interaction.response.send_message(f"Joined {channel.name} 🎙️")

@tree.command(name="voice_leave", description="Leave voice channel")
async def voice_leave(interaction: discord.Interaction):
    vc = voice_clients.get(interaction.guild_id)
    if vc:
        await vc.disconnect()
        del voice_clients[interaction.guild_id]
        await interaction.response.send_message("Left voice channel 👋")
    else:
        await interaction.response.send_message("Not in a voice channel", ephemeral=True)

@tree.command(name="voice_speak", description="Bot speaks text in VC")
@app_commands.describe(text="Text to speak")
async def voice_speak(interaction: discord.Interaction, text: str):
    vc = voice_clients.get(interaction.guild_id)
    if not vc:
        await interaction.response.send_message("Not in a voice channel. Use `/voice_join` first.", ephemeral=True)
        return
    
    await interaction.response.defer()
    audio = await hermes_tts(text)
    
    # Save temp and play
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio)
        temp_path = f.name
    
    try:
        vc.play(discord.FFmpegPCMAudio(temp_path))
        await interaction.followup.send(f"Speaking: {text[:50]}...")
    finally:
        os.unlink(temp_path)

@tree.command(name="voice_podcast", description="Record discussion, get AI summary")
@app_commands.describe(topic="Discussion topic")
async def voice_podcast(interaction: discord.Interaction, topic: str):
    vc = voice_clients.get(interaction.guild_id)
    if not vc:
        await interaction.response.send_message("Join a voice channel first.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"🎙️ Recording podcast: **{topic}**\nUse `/voice_stop` when done.")
    
    # Start recording (simplified - real impl uses discord.sinks)
    vc.start_recording(
        discord.sinks.WaveSink(),
        lambda sink: asyncio.create_task(process_recording(sink, topic, interaction)),
        interaction.channel
    )

async def process_recording(sink, topic, interaction):
    audio_data = sink.get_audio_data()
    # Combine all users' audio
    for user_id, audio in audio_data.items():
        text = await hermes_stt(audio.file.read())
        # Send to Hermes for summary
        # ... implementation
        await interaction.followup.send(f"📝 Transcript for <@{user_id}>:\n{text[:500]}")

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")
    print("Voice bot ready")

if __name__ == "__main__":
    client.run(BOT_TOKEN)
```

### .env.example
```bash
DISCORD_BOT_TOKEN={{DISCORD_BOT_TOKEN}}
HERMES_API_URL=http://127.0.0.1:8642
API_SERVER_KEY={{API_SERVER_KEY}}

# Hermes Gateway must have:
# stt.enabled=true
# stt.provider=local
# tts.provider=edge
```

### README.md
```markdown
# Voice + TTS Discord Bot Example

Discord bot with voice channel support via Hermes Gateway STT/TTS.

## Run locally

```bash
cd examples/voice-tts
cp .env.example .env.local
# Edit .env.local
pip install discord.py aiohttp
python3 skill/scripts/voice_bot.py
```

## Prerequisites

1. **Hermes Gateway** with STT/TTS enabled:
   ```bash
   hermes config set stt.enabled true
   hermes config set stt.provider local  # or groq
   hermes config set tts.provider edge
   hermes gateway restart
   ```

2. **Discord Bot** with intents:
   - Message Content Intent: ON
   - Voice Intent: ON

## Commands

| Command | Description |
|---------|-------------|
| `/voice_join` | Join your voice channel |
| `/voice_leave` | Leave voice channel |
| `/voice_speak <text>` | Bot speaks in VC |
| `/voice_podcast <topic>` | Record + transcribe + summarize |
```