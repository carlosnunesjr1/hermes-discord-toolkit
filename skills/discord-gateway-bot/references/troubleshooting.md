# Troubleshooting Guide

## Bot Won't Start

### `guild_threads` Intent Error
```
TypeError: 'guild_threads' is not a valid flag name.
```
**Fix**: Use `guilds=True` (includes threads), not `guild_threads=True`.

```python
# Wrong
INTENTS = discord.Intents(guilds=True, guild_threads=True, ...)

# Correct
INTENTS = discord.Intents(guilds=True, guild_messages=True, ...)
```

### Token Invalid / Not Found
### Token Invalid / Not Found
```discord.errors.LoginFailure: Improper token has been passed.
```
**Fix**: Verify `.env` has correct `DISCORD_BOT_TOKEN` (Bot → Reset Token in Developer Portal).

**⚠️ SECURITY**: If you ever exposed your token publicly (chat, logs, code), **regenerate it immediately** in Developer Portal → Bot → Reset Token. Discord invalidates exposed tokens automatically.

### Syntax Error in gateway_client.py
```
SyntaxError: keyword argument repeated: headers
```
**Fix**: Duplicate `headers=` keyword in `session.post()` call (lines ~119 and ~381). Remove the first standalone `headers={"Content-Type": "application/json"},` — keep only the merged headers dict with both Content-Type and X-Webhook-Signature.

```python
# Broken (duplicate headers=)
async with session.post(
    url,
    data=_body,
    headers={"Content-Type": "application/json"},
    headers={
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    },
    ...
)

# Fixed (single headers dict)
async with session.post(
    url,
    data=_body,
    headers={
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    },
    ...
)
```

### Application ID Mismatch
```
discord.errors.HTTPException: 400 Bad Request (error code: 50035): Invalid Form Body
```
**Fix**: `DISCORD_APP_ID` must match the bot's application ID (General Information).

### Guild ID Wrong
```
Slash commands synced to guild 123... but bot not in that guild
```
**Fix**: `DISCORD_GUILD_ID` must be the server where bot is added.

## Slash Commands Not Appearing

### Not Synced
**Fix**: Restart bot (`./deploy.sh restart`) — syncs on startup.

### Wrong Guild
**Fix**: Ensure `DISCORD_GUILD_ID` matches target server.

### Missing Permissions
Bot needs `applications.commands` OAuth2 scope when invited.

### Global vs Guild Commands
This bot uses **guild-scoped** commands (instant sync). No 1-hour global delay.

## Gateway Connection Failed

### `Gateway connection failed: Cannot connect to host localhost:8642`
**Fix**: 
1. Check Hermes Gateway running: `systemctl status hermes-gateway`
2. Test: `curl http://localhost:8642/health`
3. Check firewall: `ss -ltnp | grep 8642`

### Gateway Returns 500/502
**Fix**: Check gateway logs: `journalctl -u hermes-gateway -n 100`

## Thread Issues

### Thread Not Created
**Missing Permissions**: Bot needs `Manage Threads` and `Send Messages in Threads`.

### Thread Not Registered (No Hermes Session)
**Cause**: Thread created externally (Discord UI, not bot).
**Fix**: Mention `@Hermes` in thread → auto-registers.

### Archived Thread Not Restoring
**Check**: `thread_manager.get_session(thread_id).hermes_session_id` exists.
**Fix**: Message in thread → auto-unarchive → session restored.

### Persistence File Corrupt
```
json.decoder.JSONDecodeError
```
**Fix**: Delete `~/.hermes/discord_threads.json` and restart bot.

## Auto-Provisioning Failures

### "Could not post panel in #channel: could not find open space for item"
**Cause**: Discord thread message limit or rate limit.
**Fix**: Increase delay between channel creations, or reduce panel complexity.

### Missing `Manage Channels` Permission
**Fix**: Grant bot `Manage Channels` permission in Discord.

## Background Tasks Stopped

### Check Task Status
```python
# In bot status command
for i, task in enumerate(bot._bg_tasks):
    print(f"Task {i}: {'running' if not task.done() else 'STOPPED'}")
```

### Common Causes
- Unhandled exception in task loop → check logs
- `asyncio.CancelledError` on shutdown → normal
- Rate limit from Discord API → backoff implemented

## Webhook Outbound Failures

### "Missing webhook_url"
**Fix**: Add `webhook_url` to route's `deliver_extra` or set `DISCORD_WEBHOOK_{channel_id}` env var.

### HTTP 404 from Discord
**Cause**: Webhook URL invalid or deleted.
**Fix**: Recreate webhook in Discord, update URL.

### HTTP 403 Forbidden
**Cause**: Webhook token incorrect.
**Fix**: Recreate webhook, copy new URL.

### Rate Limited (429)
**Behavior**: Returns error, does not retry automatically.
**Fix**: Implement retry with backoff in `_deliver_discord_webhook`.

## Voice Not Working

### "PyNaCl is not installed, voice will NOT be supported"
**Fix**: 
```bash
cd /home/carlos/hermes-discord-bot
./venv/bin/pip install PyNaCl
```

### "davey is not installed, voice will NOT be supported"
**Fix**:
```bash
./venv/bin/pip install davey
```

## Permission Errors

### "Missing Permissions" on Action
**Fix**: Bot needs appropriate permissions:
- `Manage Channels` — create channels/threads
- `Manage Threads` — create/archive threads
- `Send Messages` — post messages
- `Send Messages in Threads` — post in threads
- `Embed Links` — panel embeds
- `Read Message History` — check existing threads
- `Add Reactions` — reaction controls
- `Manage Messages` — admin actions (cleanup, etc.)

## Interaction Failed / Unknown Interaction

### "Unknown Interaction" / "Interaction Already Acknowledged"
**Cause**: Interaction token expired (3s timeout) or double-handled.
**Fix**: 
- Use `defer()` for operations > 3s
- Ensure single handler per custom_id

## Systemd Service Issues

### Service Won't Start (Exit Code 1)
```bash
sudo journalctl -u hermes-discord-bot -n 50
```
Check for:
- `.env` missing or invalid
- Python import errors
- Port conflicts (not applicable for WS bot)

### Service Restarting Constantly
**Cause**: Crash on startup → systemd restarts → crash loop.
**Fix**: Check logs, fix root cause.

## Deployment Issues

### `./deploy.sh install` Fails
**Common**: Python 3.11+ required, `venv` module missing.
**Fix**: `apt install python3.11-venv`

### `./deploy.sh test-gateway` Fails
**Fix**: Ensure `aiohttp` installed in venv, Hermes Gateway running.

## Logs to Check

| Issue | Log Location |
|-------|--------------|
| Bot startup | `sudo journalctl -u hermes-discord-bot -n 100` |
| Gateway | `sudo journalctl -u hermes-gateway -n 100` |
| Webhook | `sudo journalctl -u hermes-gateway -n 100 | grep webhook` |
| Thread persistence | `cat ~/.hermes/discord_threads.json` |

## Debug Commands

```bash
# Bot status
./deploy.sh status

# Live logs
./deploy.sh logs

# Last 200 lines
./deploy.sh tail 200

# Test gateway
./deploy.sh test-gateway

# Check tokens loaded
cd /home/carlos/hermes-discord-bot && ./venv/bin/python -c "
from config import BotConfig
c = BotConfig.from_env()
print(f'Bot token: {c.token[:20]}...')
print(f'App ID: {c.app_id}')
print(f'Guild ID: {c.guild_id}')
print(f'Gateway: {c.gateway_url}')
"

# Check persistence
cat ~/.hermes/discord_threads.json | jq '.threads | length'

# Test slash command sync
cd /home/carlos/hermes-discord-bot && ./venv/bin/python -c "
import discord, asyncio
from config import BotConfig
async def test():
    c = BotConfig.from_env()
    intents = discord.Intents(guilds=True, guild_messages=True, message_content=True)
    bot = discord.Client(intents=intents)
    @bot.event
    async def on_ready():
        cmds = await bot.tree.fetch_commands(guild=discord.Object(c.guild_id))
        print(f'Synced commands: {[c.name for c in cmds]}')
        await bot.close()
    await bot.start(c.token)
asyncio.run(test())
"
```

## Health Check Endpoints

| Service | Endpoint | Expected |
|---------|----------|----------|
| Hermes Gateway | `http://localhost:8642/health` | `{"status":"ok","platform":"hermes-agent"}` |
| Webhook | `http://localhost:8644/health` | `{"status":"ok","platform":"webhook"}` |
| Discord Bot | N/A (WS) | Check service status |

## Version Compatibility

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| discord.py | 2.3+ |
| aiohttp | 3.9+ |
| Hermes Gateway | 0.16+ |

## Emergency Recovery

### Reset Everything
```bash
# Stop services
sudo systemctl stop hermes-discord-bot hermes-gateway

# Clean persistence
rm ~/.hermes/discord_threads.json

# Restart
sudo systemctl start hermes-gateway
sleep 5
./deploy.sh start
```

### Re-create Discord Structure
1. Manually delete categories/channels in Discord
2. `./deploy.sh restart`
3. Bot auto-provisions fresh structure