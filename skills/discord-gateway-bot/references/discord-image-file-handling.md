# Discord Image & File Handling Patterns

## Current Gaps (v2.4)

| Capability | Status | Blockers |
|------------|--------|----------|
| Receive image attachments | ❌ Not implemented | `on_message` ignores `message.attachments` |
| Analyze images (Vision) | ❌ Not integrated | No pipeline: attachment → download → vision tool → response |
| Generate & send images | ❌ Not implemented | Gateway creates, bot doesn't send as `discord.File` |
| Receive file attachments | ❌ Not implemented | Same as images |
| Send files to Discord | ❌ Not implemented | No `/hermes file upload` command |
| Podcast audio delivery | ❌ Partial | Generates MP3 but doesn't upload/play |

---

## Implementation Plan

### 1. Image Attachment Reception (`bot.py` → `on_message`)

```python
# In on_message, after existing handlers:
if message.attachments:
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            await self._handle_image_attachment(message, attachment)
        elif attachment.size > 0:
            await self._handle_file_attachment(message, attachment)

async def _handle_image_attachment(self, message: discord.Message, attachment: discord.Attachment):
    """Download image, analyze with vision tool, respond in thread."""
    # 1. Download to temp file
    import tempfile, aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            img_data = await resp.read()
    
    with tempfile.NamedTemporaryFile(suffix=f".{attachment.filename.split('.')[-1]}", delete=False) as f:
        f.write(img_data)
        temp_path = f.name
    
    # 2. Call vision tool via gateway
    # Use gateway's vision capability (auxiliary.vision)
    payload = self._build_interaction_payload(
        message,
        content=f"[IMAGE ATTACHED: {temp_path}] Analise esta imagem",
        hermes_session_id=session.hermes_session_id if isinstance(message.channel, discord.Thread) else None
    )
    result = await self.gateway.forward_interaction(payload)
    
    # 3. Send response
    await self._send_interaction_response(message, result)
    
    # 4. Cleanup
    try: os.unlink(temp_path)
    except: pass
```

### 2. Image Generation Command (`/hermes image generate`)

```python
@discord.app_commands.command(name="image", description="Gerar e enviar imagens")
@discord.app_commands.describe(
    action="Ação",
    prompt="Prompt da imagem",
    aspect_ratio="Proporção"
)
@discord.app_commands.choices(action=[
    discord.app_commands.Choice(name="generate", value="generate"),
])
async def cmd_image(
    interaction: discord.Interaction,
    action: str,
    prompt: str,
    aspect_ratio: str = "landscape"
):
    await interaction.response.defer(ephemeral=True)
    bot: HermesDiscordBot = interaction.client
    
    # Call gateway image generation
    result = await bot.gateway.image_generate(
        prompt=prompt,
        aspect_ratio=aspect_ratio
    )
    
    if "error" in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    # Gateway returns image path or URL
    image_path = result.get("image") or result.get("path")
    if image_path and os.path.exists(image_path):
        # Send as Discord file attachment
        file = discord.File(image_path, filename="generated.png")
        await interaction.followup.send("🎨 Imagem gerada:", file=file, ephemeral=True)
    else:
        await interaction.followup.send(f"✅ {result.get('text', 'Gerado')}", ephemeral=True)
```

### 3. File Upload/Download Commands

```python
@discord.app_commands.command(name="file", description="Upload/download arquivos via Discord")
@discord.app_commands.describe(
    action="Ação",
    path="Caminho do arquivo (upload)",
    url="URL para download",
    filename="Nome do arquivo (download)"
)
@discord.app_commands.choices(action=[
    discord.app_commands.Choice(name="upload", value="upload"),
    discord.app_commands.Choice(name="download", value="download"),
])
async def cmd_file(
    interaction: discord.Interaction,
    action: str,
    path: str = None,
    url: str = None,
    filename: str = None
):
    await interaction.response.defer(ephemeral=True)
    bot: HermesDiscordBot = interaction.client
    
    if action == "upload":
        if not path or not os.path.exists(path):
            await interaction.followup.send("❌ Arquivo não encontrado", ephemeral=True)
            return
        file = discord.File(path, filename=filename or os.path.basename(path))
        await interaction.followup.send("📎 Arquivo:", file=file, ephemeral=True)
    
    elif action == "download":
        if not url:
            await interaction.followup.send("❌ URL obrigatória", ephemeral=True)
            return
        import aiohttp, tempfile
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
        ext = filename.split(".")[-1] if filename and "." in filename else "bin"
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as f:
            f.write(data)
            temp_path = f.name
        file = discord.File(temp_path, filename=filename or f"download.{ext}")
        await interaction.followup.send("📥 Baixado:", file=file, ephemeral=True)
        try: os.unlink(temp_path)
        except: pass
```

### 4. Podcast Audio Delivery

Add `deliver` parameter to podcast generation:

```python
# In cmd_podcast generate:
result = await bot.gateway.podcast_generate(
    topic=topic,
    format=format,
    duration_minutes=duration,
    voices=voice_list,
    style=style,
    language="pt-BR",
    deliver="discord_file"  # NEW: "discord_file" | "voice_channel" | "both" | "none"
)

# If deliver in ("discord_file", "both") and result has audio_path:
if deliver in ("discord_file", "both") and result.get("audio_path"):
    audio_path = result["audio_path"]
    if os.path.exists(audio_path):
        file = discord.File(audio_path, filename=f"podcast_{topic[:30]}.mp3")
        await interaction.followup.send("🎙️ Podcast gerado:", file=file, ephemeral=True)

# If deliver in ("voice_channel", "both") and bot in voice:
if deliver in ("voice_channel", "both") and interaction.guild.voice_client:
    await bot._speak_audio_file(interaction.guild.id, result["audio_path"])
```

### 5. Gateway Webhook Attachment Extraction

In `gateway/platforms/webhook.py` → Discord webhook handler:

```python
# Payload Discord includes attachments[]
async def _parse_discord_payload(self, payload: dict) -> str:
    content = payload.get("content", "")
    attachments = payload.get("attachments", [])
    
    if attachments:
        attachment_info = []
        for att in attachments:
            attachment_info.append(
                f"[Attachment: {att.get('filename')} ({att.get('content_type')}) "
                f"URL: {att.get('url')} Size: {att.get('size')} bytes]"
            )
        content += "\n\n" + "\n".join(attachment_info)
    
    return content
```

---

## Dependencies to Add

```bash
# In hermes-discord-bot/venv
pip install aiohttp edge-tts  # Already present
pip install "discord.py[voice]"  # For real-time voice receive (STT)
```

---

## Voice Receive (STT Real-time) - Blocked

**Current state:** `VOICE_RECV_AVAILABLE = False` in `bot.py` line 20 because `discord.py[voice]` not installed.

**To enable:**
```bash
cd /home/carlos/hermes-discord-bot && source venv/bin/activate
pip install "discord.py[voice]" --upgrade
```

After install:
- `VOICE_RECV_AVAILABLE = True`
- `HermesAudioSink` class works (already implemented in bot.py)
- Real-time voice → Whisper STT → thread transcript → Hermes response → TTS

**Architecture ready in bot.py:**
- `_start_voice_listening()` - starts Discord voice receive with custom AudioSink
- `_monitor_voice_listening()` - auto-stop after 5min silence
- `_check_wake_word()` - filters for "hermes", "jarvis", "computer", "h"
- Meeting thread auto-creation for transcripts
- Whisper model loaded (base, int8, CPU)