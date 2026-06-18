# Podcast Mode Implementation

## Overview
Full podcast generation capability enabling automated audio content creation for daily briefings, meeting summaries, project updates, and recurring scheduled episodes.

## Architecture

```
┌─────────────────┐     Gateway API      ┌──────────────────────┐
│  Discord Bot    │ ◄────────────────────► │ Hermes Gateway       │
│  (Commands)     │   /v1/tts/podcast      │ (orchestration)      │
└─────────────────┘                         └──────────┬───────────┘
                                                       │
                         ┌─────────────────────────────┼─────────────────────────┐
                         ▼                             ▼                         ▼
                ┌─────────────────┐           ┌─────────────────┐      ┌─────────────────┐
                │   Edge TTS      │           │  Hermes Agent   │      │   Multi-Voice   │
                │  pt-BR-Antonio  │           │  (script gen)   │      │   Synthesis     │
                │  + Francisca    │           └─────────────────┘      └─────────────────┘
                └─────────────────┘
```

## Components

### 1. Podcast Commands (`/hermes podcast`)

| Subcommand | Description | Parameters |
|------------|-------------|------------|
| `generate` | Single episode creation | `topic`, `format`, `duration`, `voices`, `style` |
| `briefing` | Daily briefing (auto-topic) | `voices`, `style` |
| `meeting` | Meeting summary | `topic` (meeting name), `format`, `duration` |
| `project` | Project update | `topic` (project name), `format`, `duration` |
| `schedule` | Recurring podcast | `name`, `topic`, `schedule` (cron), `format` |
| `list` | List scheduled podcasts | - |
| `cancel` | Cancel scheduled | `name` |

### 2. Formats

| Format | Use Case | Typical Duration |
|--------|----------|------------------|
| `daily_briefing` | Morning summary | 3-5 min |
| `meeting_summary` | Post-meeting recap | 5 min |
| `project_update` | Progress report | 5 min |
| `deep_dive` | Technical analysis | 10-15 min |
| `conversation` | Dual-host dialogue | 5-10 min |
| `standup` | Daily standup | 2-3 min |

### 3. Styles

| Style | Tone |
|-------|------|
| `professional` | Executive, formal |
| `casual` | Conversational, relaxed |
| `technical` | Developer-focused, detailed |
| `storytelling` | Narrative, engaging |

### 4. Voices (Edge TTS pt-BR)

| Voice ID | Gender |
|----------|--------|
| `pt-BR-AntonioNeural` | Male (default) |
| `pt-BR-FranciscaNeural` | Female |
| `pt-BR-ThalitaNeural` | Female |
| `pt-BR-ErickNeural` | Male |

**Multi-voice**: Use comma-separated list:
```
voices: "pt-BR-AntonioNeural,pt-BR-FranciscaNeural"
```

## Implementation

### Gateway Client

```python
async def podcast_generate(
    self,
    topic: str,
    format: str = "daily_briefing",
    duration_minutes: int = 5,
    voices: Optional[List[str]] = None,
    style: str = "professional",
    language: str = "pt-BR"
) -> Dict[str, Any]:
    voices_list = voices or ["pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"]
    voices_str = ",".join(voices_list)
    
    prompt = (
        f"podcast generate topic:\"{topic}\" "
        f"format:{format} "
        f"duration:{duration_minutes} "
        f"voices:{voices_str} "
        f"style:{style} "
        f"lang:{language}"
    )
    
    return await self._send_via_webhook(prompt, channel_id="discord-podcast")

async def podcast_schedule(
    self,
    name: str,
    topic_template: str,
    schedule: str,  # cron format
    format: str = "daily_briefing",
    channel_id: Optional[int] = None
) -> Dict[str, Any]:
    channel = channel_id or self.config.get("default_podcast_channel")
    prompt = (
        f"podcast schedule name:\"{name}\" "
        f"topic:\"{topic_template}\" "
        f"schedule:\"{schedule}\" "
        f"format:{format} "
        f"channel:{channel}"
    )
    
    return await self._send_via_webhook(prompt, channel_id="discord-podcast")
```

### Bot Commands

```python
@discord.app_commands.command(name="podcast")
@discord.app_commands.choices(action=[...], format=[...], style=[...])
async def cmd_podcast(...):
    # Actions: generate, briefing, meeting, project, schedule, list, cancel
    # Formats: daily_briefing, meeting_summary, project_update, deep_dive, conversation, standup
    # Styles: professional, casual, technical, storytelling
    # Voices: pt-BR-AntonioNeural, pt-BR-FranciscaNeural, etc.
```

## Quick Shortcuts

| Shortcut | Full Command Equivalent | Use Case |
|----------|------------------------|----------|
| `/hermes podcast briefing` | generate with auto-topic | Morning routine |
| `/hermes podcast meeting topic:"Planning Q3"` | meeting_summary | Post-meeting recap |
| `/hermes podcast project topic:"Nexus PIM"` | project_update | Project status |

## Configuration

### Hermes Gateway `config.yaml`

```yaml
tts:
  provider: edge
  edge:
    voice: pt-BR-AntonioNeural
  elevenlabs:
    voice_id: pNInz6obpgDQGcFmaJgB
    model_id: eleven_multilingual_v2
  use_gateway: true
  enabled: true
```

### Bot `.env` (dependencies)

```bash
# Podcast/TTS deps
edge-tts>=7.2.0
```

## Usage Examples

### 1. Daily Morning Briefing
```
/hermes podcast briefing
```
Generates 3-min professional briefing with: date, active projects, priority tasks, system status, calendar agenda.

### 2. Meeting Summary
```
/hermes podcast meeting topic:"Planning Q3"
```
Generates 5-min summary with: decisions, action items, next steps, risks.

### 3. Project Update
```
/hermes podcast project topic:"Nexus PIM"
```
Generates 5-min technical update with: progress, blockers, milestones, team status, risks.

### 4. Scheduled Recurring Podcast
```
/hermes podcast schedule name:"Daily Briefing" topic:"Briefing diário" schedule:"0 7 * * *" format:daily_briefing channel:#podcasts
```
Runs daily at 07:00, posts to #podcasts channel.

## Output

Generated podcasts are:
1. **TTS audio** (MP3 via Edge TTS) — played in voice channel if connected
2. **Text response** — posted in Discord chat/thread
3. **Metadata** — format, duration, voices used, generation timestamp

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Podcast generation failed" | Check Hermes Gateway has TTS configured, Edge TTS installed |
| Audio not playing in voice | Verify voice channel connected, `ffmpeg` in PATH |
| Scheduled podcast not running | Check cron syntax, bot running, Gateway cron jobs enabled |
| Multi-voice not working | Verify voice IDs exist in Edge TTS, use comma-separated |
| Topic too long | Trim to < 4000 chars (Edge TTS limit) |

## Cron Schedule Reference

| Schedule | Cron Expression |
|----------|-----------------|
| Daily 07:00 | `0 7 * * *` |
| Weekdays 08:00 | `0 8 * * 1-5` |
| Weekly Monday 09:00 | `0 9 * * 1` |
| Every hour | `0 * * * *` |
| Every 15 min | `*/15 * * * *` |