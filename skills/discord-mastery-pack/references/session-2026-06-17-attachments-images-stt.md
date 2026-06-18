# Session 2026-06-17: Attachments, Images, Vision, STT, File Operations

## Overview
Extended Discord bot with full attachment processing pipeline, image generation/analysis, STT via file upload, and file operations — all $0 open source via Nous subscription + local VPS.

---

## New Slash Commands Implemented

| Command | Description | Cost |
|---------|-------------|------|
| `/hermes image generate prompt:"..." model:"gpt-image-1\|dall-e-3\|fal-flux"` | Generate image via Hermes Gateway | $0 (Nous) |
| `/hermes image analyze image:(attachment) prompt:"..."` | Analyze attached image (vision) | $0 (Nous) |
| `/hermes file upload path:"/home/.../file.pdf"` | Upload file from server to Discord | $0 |
| `/hermes file download url:"https://..."` | Download URL and send to Discord | $0 |
| `/hermes file list path:"/home/.../"` | List files in shared directory | $0 |
| `/hermes stt audio:(attachment.ogg/.mp3/.wav) language:pt` | Transcribe audio via local Whisper | $0 (local) |

---

## Automatic Attachment Processing Pipeline

All message handlers (`_handle_dm`, `_handle_mention`, `_handle_thread_message`) now intercept `message.attachments`:

```python
# In bot.py - automatic processing
if message.attachments:
    await self._process_attachments(message, ...)
    return

async def _process_attachments(self, message, content=None, is_dm=False, hermes_session_id=None):
    for attachment in message.attachments:
        if attachment.content_type.startswith("image/"):
            await self._handle_image_attachment(message, attachment, content, is_dm, hermes_session_id)
        elif attachment.content_type.startswith("audio/"):
            await self._handle_audio_attachment(message, attachment, content, is_dm, hermes_session_id)
        else:
            await self._handle_file_attachment(message, attachment, content, is_dm, hermes_session_id)
```

### Image Attachment → Vision Analysis
1. Download attachment bytes
2. Save to temp file
3. Forward to gateway: `vision analyze image:{path} prompt:"{prompt}"`
4. Return analysis in thread/DM

### Audio Attachment → STT Transcription
1. Download audio bytes
2. Save to temp file
3. POST to local STT server: `http://localhost:8798/api/transcribe` (multipart/form-data)
4. Get transcript + language detection
5. **Wake word check**: if transcript contains "hermes"/"jarvis" → forward to Hermes automatically

### File Attachment → Save to Shared
1. Download file bytes
2. Save to `/home/carlos/.hermes/shared/{filename}`
3. Confirm with path + size

---

## Voice TTS (Working)

| Feature | Implementation | Cost |
|---------|----------------|------|
| **Join VC** | `/hermes voice join` | $0 |
| **Speak next message** | `/hermes voice speak` → next text message spoken via Edge TTS | $0 |
| **Auto-speak** | `bot.voice_speak_next[guild_id] = channel_id` set by speak command | $0 |
| **Voices** | `pt-BR-AntonioNeural`, `pt-BR-FranciscaNeural`, `pt-BR-ThalitaNeural`, `pt-BR-ErickNeural` | $0 |

```python
# In bot.py - _speak_in_voice()
communicate = edge_tts.Communicate(text[:4000], "pt-BR-AntonioNeural")
await communicate.save(temp_path)
source = discord.FFmpegPCMAudio(temp_path)
vc.play(source)
```

---

## Voice Receive (STT Real-time) — BLOCKED

**Blocker**: `discord.py[voice]` (VoiceRecvClient) not available in stable release (2.8.0a). Only in `main` branch.

```python
# Current status in bot.py
VOICE_RECV_AVAILABLE = False
voice_recv = None

# HermesAudioSink class guarded:
if VOICE_RECV_AVAILABLE:
    class HermesAudioSink(voice_recv.AudioSink): ...
else:
    class HermesAudioSink:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("voice_recv not available - install discord.py[voice] from main branch")
```

**Workaround implemented**: File-based STT via `/hermes stt` command (attachment upload).

**Future fix**: When discord.py 2.9+ releases with voice_recv:
```bash
pip install git+https://github.com/Rapptz/discord.py@main --upgrade
# Then set VOICE_RECV_AVAILABLE = True and import voice_recv
```

---

## Cost Breakdown — ALL $0

| Component | Provider | Cost |
|-----------|----------|------|
| LLM (nvidia/nemotron-3-ultra:free) | Nous subscription | $0 (included) |
| Image Gen (gpt-image-1, dall-e-3, fal-flux) | Nous subscription | $0 (included) |
| Vision (image analysis) | Hermes Gateway / Nous | $0 (included) |
| TTS (Edge TTS) | Microsoft Edge voices | $0 |
| STT (faster-whisper) | Local on VPS (CPU/GPU) | $0 |
| Discord Bot | discord.py (MIT) | $0 |
| VPS | Oracle Free Tier / existing | $0 |
| Redis, SQLite, Docker | Open source | $0 |

---

## Gateway Client Extension

Added `image_generate()` method to `gateway_client.py`:

```python
async def image_generate(self, prompt: str, model: str = "gpt-image-1") -> Dict[str, Any]:
    prompt_str = f"image generate prompt:\"{prompt}\" model:{model}"
    return await self._send_via_webhook(prompt_str, channel_id="discord-image")
```

---

## Key Files Modified

| File | Changes |
|------|---------|
| `bot.py` | +Attachment handlers, +image/file/stt commands, +voice TTS, HermesAudioSink guard |
| `gateway_client.py` | +image_generate() method |

---

## Test Commands for Discord

```
# Image generation
/hermes image generate prompt:"cyberpunk city at night, neon, 4k" model:fal-flux

# Image analysis (attach image + command)
/hermes image analyze prompt:"describe the architecture diagram"

# STT transcription (attach .ogg/.mp3)
/hermes stt

# File operations
/hermes file upload path:"/home/carlos/.hermes/shared/report.pdf"
/hermes file download url:"https://example.com/doc.pdf"
/hermes file list

# Voice TTS
/hermes voice join
/hermes voice speak
# then type: "Olá, tudo funcionando?"

# Podcast (generates TTS audio)
/hermes voice join
/hermes podcast briefing
```

---

## Architecture Notes

### Attachment Flow
```
User attaches image/audio/file
        │
        ▼
on_message() intercepts
        │
        ▼
_process_attachments() routes by content_type
        │
        ├─► image/* → _handle_image_attachment → vision analyze → response
        ├─► audio/* → _handle_audio_attachment → STT server → transcript → wake word? → Hermes
        └─► other   → _handle_file_attachment → save to /shared → confirm
```

### STT Server (Existing)
- Runs on port 8798: `python /home/carlos/stt-server.py`
- Uses `faster-whisper` with `large-v3` model (CUDA)
- Endpoints: `POST /api/transcribe`, `WS /api/transcribe/stream`

### Hermes Gateway Image/Vision
- Toolset `image_gen` active
- Toolset `vision` active
- Routes via webhook to Discord channel `discord-image` / `discord-vision`

---

## Pitfalls & Gotchas

| Issue | Solution |
|-------|----------|
| `discord.py[voice]` not in stable | Use file-based STT (`/hermes stt`) until 2.9+ release |
| Large image uploads timeout | Gateway has 120s timeout; keep prompts concise |
| STT language detection | Default `pt` works well; specify `language` param if needed |
| Voice TTS temp file cleanup | `vc.after = cleanup` callback removes temp MP3 |
| Wake word in transcript | Case-insensitive check: "hermes", "jarvis", "computer", "h" |
| Thread context preservation | Hermes session ID passed in `hermes_session_id` for threaded replies |

---

## Next Steps (When voice_recv Available)

1. Enable `VOICE_RECV_AVAILABLE = True`
2. Import `voice_recv` 
3. Implement `_start_voice_listening()` with `HermesAudioSink`
4. Real-time wake word → Hermes → TTS response loop
5. Meeting transcription thread with live updates

---

*Generated: 2026-06-17 | Session: Voice/Image/File Pipeline Implementation*