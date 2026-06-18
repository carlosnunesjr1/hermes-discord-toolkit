# Voice / JARVIS Mode Implementation

## Overview
Full Discord voice channel integration enabling real-time conversational AI — "JARVIS style" from Iron Man.

## Architecture

```
┌─────────────────┐     Voice WS      ┌──────────────────────┐
│  Discord Voice  │ ◄────────────────► │  hermes-discord-bot  │
│   Channel       │   opus audio      │  (discord.py voice)  │
└─────────────────┘                   └──────────┬───────────┘
                                                  │
                         ┌────────────────────────┼────────────────────────┐
                         ▼                        ▼                        ▼
                ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
                │   Edge TTS      │      │  Hermes Gateway │      │   OpenAI STT    │
                │  pt-BR-Antonio  │      │  (orchestration)│      │   Whisper-1     │
                └─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Components

### 1. Voice State Management (`bot.py`)

```python
# Per-guild voice state
self.voice_listening: Dict[int, bool] = {}      # STT active?
self.voice_speak_next: Dict[int, int] = {}      # channel_id to speak next response
```

## Voice Commands (`/hermes voice`)

| Subcommand | Implementation |
|------------|----------------|
| `join` | **Immediate response + background connect** (avoids 3s interaction timeout). Sets `voice_listening[guild_id]=True` |
| `leave` | `await vc.disconnect()` + clear state |
| `speak` | Set `voice_speak_next[guild_id] = channel_id`; next response triggers `_speak_in_voice()` |
| `listen` | Set `voice_listening[guild_id] = True` (STT via Gateway) |
| `status` | Embed with channel, listening state, latency |

### Interaction Timeout Fix (Critical for `/voice join`)

The `target_channel.connect()` operation takes 2-5 seconds, exceeding Discord's 3-second interaction timeout. 

**Fixed Pattern:**
```python
if action == "join":
    # IMMEDIATE response (acknowledges interaction)
    await interaction.response.send_message(f"🔊 Conectando a {target.mention}...", ephemeral=True)
    
    # Background task for long operation
    async def do_connect():
        try:
            await target.connect()
            bot.voice_listening[interaction.guild.id] = True
            await interaction.followup.send(f"✅ Conectado a {target.mention}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Falha: {e}", ephemeral=True)
    
    asyncio.create_task(do_connect())
    return
```

See `references/interaction-timeout-pattern.md` for full details.

### 3. TTS Pipeline (`_speak_in_voice`)

```python
async def _speak_in_voice(self, guild_id: int, text: str):
    vc = self.get_guild(guild_id).voice_client
    
    # 1. Generate MP3 via Edge TTS
    communicate = edge_tts.Communicate(text[:4000], "pt-BR-AntonioNeural")
    await communicate.save(temp_path)
    
    # 2. Play via discord.py FFmpegPCMAudio
    source = discord.FFmpegPCMAudio(temp_path)
    vc.play(source)
    
    # 3. Cleanup temp file after playback
    vc.after = lambda _: os.unlink(temp_path)
```

**Dependencies:** `edge-tts` (pip), `ffmpeg` (system)

### 4. STT Pipeline (Gateway-side)

Configured in Hermes Gateway `config.yaml`:
```yaml
stt:
  enabled: true
  provider: openai
  openai:
    model: whisper-1
```

Discord voice audio → Gateway STT → Text → Hermes processing

### 5. Auto-Disconnect Logic

```python
async def on_voice_state_update(self, member, before, after):
    # Bot disconnected
    if member.id == self.user.id and before.channel and not after.channel:
        self.voice_listening[guild_id] = False
        self.voice_speak_next[guild_id] = None
    
    # Alone in channel → 30s timeout → disconnect
    vc = member.guild.voice_client
    if vc:
        humans = [m for m in vc.channel.members if not m.bot]
        if len(humans) == 0:
            await asyncio.sleep(30)
            if still_alone: await vc.disconnect()
```

## Configuration

### Bot `.env`
```bash
# Voice deps (installed in venv)
# PyNaCl, davey, edge-tts

# System
# ffmpeg (apt-get install ffmpeg)
```

### Hermes Gateway `config.yaml`
```yaml
stt:
  enabled: true
  provider: openai
  openai:
    model: whisper-1
  use_gateway: true

tts:
  provider: edge
  edge:
    voice: pt-BR-AntonioNeural
  use_gateway: true
  enabled: true
```

## Discord Developer Portal — Voice Permissions

Bot needs: **Connect**, **Speak**, **Use Voice Activity**, **Priority Speaker** (optional)

## Usage Flow

```
1. User enters Discord voice channel
2. /hermes voice join
   → "🔊 Conectado a #General — modo escuta ativa"
3. User: /hermes voice speak
4. User types: "Hermes, qual o status do deploy?"
5. Hermes processes via Gateway
6. Response sent to text channel
7. _speak_in_voice() triggers → TTS → plays in voice channel 🎙️
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Voice not working" | `pip install PyNaCl davey edge-tts` + `apt-get install ffmpeg` |
| TTS silent | Check `ffmpeg` in PATH, verify voice channel connected, MP3 generated |
| STT not working | Verify `stt.provider: openai` in Gateway config, `OPENAI_API_KEY` set |
| Bot won't join | Check permissions: Connect, Speak, Use Voice Activity |
| Auto-disconnect too fast | Adjust 30s timeout in `on_voice_state_update` |
| "Opus not loaded" | Install `libopus` system lib (`apt-get install libopus0`) |