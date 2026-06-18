# Discord Interaction Timeout Pattern

## Problem

Discord slash commands have a **3-second timeout** for the initial response. If your command handler takes longer than 3 seconds, the interaction token expires and Discord returns:

```
NotFound: 404 Not Found (error code: 10062): Unknown interaction
```

## Common Operations That Exceed 3s

| Operation | Typical Duration | Context |
|-----------|------------------|---------|
| `await voice_channel.connect()` | 2-5s | Voice join |
| `await http_client.post()` | 1-10s | External API calls |
| `await deploy()` | 30-120s | Deploy pipelines |
| `await file_processing()` | 5-60s | Large file handling |
| `await database_migration()` | 10-300s | DB operations |

## Broken Pattern ❌

```python
@discord.app_commands.command(name="slow_command")
async def cmd_slow(interaction):
    await interaction.response.defer(ephemeral=True)  # Starts 3s clock
    result = await long_operation()  # 5s → TIMEOUT!
    await interaction.followup.send(f"Done: {result}")  # FAILS
```

## Fixed Pattern ✅

```python
@discord.app_commands.command(name="slow_command")
async def cmd_slow(interaction):
    # IMMEDIATE response - acknowledges interaction, resets timeout
    await interaction.response.send_message("⏳ Processing...", ephemeral=True)
    
    # Background task - no timeout
    async def do_work():
        try:
            result = await long_operation()
            await interaction.followup.send(f"✅ Done: {result}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
    
    asyncio.create_task(do_work())
    return  # Command returns immediately
```

## Key Principles

| Rule | Details |
|------|---------|
| **Always respond immediately** | Use `interaction.response.send_message()` for any operation > 1s |
| **Background tasks** | Use `asyncio.create_task()` for the actual work |
| **Follow-up when done** | Use `interaction.followup.send()` (available after initial response) |
| **Error handling** | Wrap background task in try/except, always followup on error |
| **Branch by action** | Fast actions (< 500ms) can use `defer()`, slow actions need immediate response |

## Decision Tree

```
Is the operation guaranteed to complete in < 500ms?
    ├─ YES → Use standard pattern:
    │       await interaction.response.defer(ephemeral=True)
    │       result = await fast_operation()
    │       await interaction.followup.send(result)
    └─ NO  → Use background task pattern:
            await interaction.response.send_message("Processing...", ephemeral=True)
            asyncio.create_task(do_work())
            # do_work() calls interaction.followup.send() when done
```

## Mixed Commands (Some Fast, Some Slow)

```python
@discord.app_commands.command(name="mixed")
async def cmd_mixed(interaction, action: str):
    if action in ["join", "deploy", "migrate"]:  # SLOW actions
        await interaction.response.send_message(f"⏳ {action}...", ephemeral=True)
        asyncio.create_task(do_slow_action(action, interaction))
        return
    
    # FAST actions - standard defer
    await interaction.response.defer(ephemeral=True)
    result = await do_fast_action(action)
    await interaction.followup.send(result)
```

## Voice Command Example (Real Implementation)

```python
@discord.app_commands.command(name="voice", description="Voice control")
@discord.app_commands.choices(action=[
    discord.app_commands.Choice(name="join", value="join"),
    # ... other actions
])
async def cmd_voice(interaction, action: str, channel: discord.VoiceChannel = None):
    bot = interaction.client
    target = channel or interaction.user.voice?.channel
    
    if action == "join":
        if not target:
            return await interaction.response.send_message("❌ Enter a voice channel", ephemeral=True)
        
        # IMMEDIATE response
        await interaction.response.send_message(f"🔊 Conectando a {target.mention}...", ephemeral=True)
        
        # Background connect
        async def do_connect():
            try:
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(target)
                else:
                    await target.connect()
                bot.voice_listening[interaction.guild.id] = True
                await interaction.followup.send(f"✅ Conectado a {target.mention}", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Falha: {e}", ephemeral=True)
        
        asyncio.create_task(do_connect())
        return
    
    # Fast actions
    await interaction.response.defer(ephemeral=True)
    # ... handle leave, speak, listen, status
```

## Testing the Pattern

```python
# Test: simulate slow operation
async def test_interaction_timeout():
    """Verify the pattern works under load."""
    interaction = mock_interaction()
    
    # This should NOT timeout
    await cmd_test_slow(interaction)
    
    # Verify immediate response was sent
    assert interaction.response._responded == True
    
    # Wait for background task
    await asyncio.sleep(0.5)
    
    # Verify followup was called
    assert interaction.followup.send.called
```

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Using `defer()` for slow ops | Timeout after 3s | Use immediate `send_message()` |
| Not awaiting background task | Task may be garbage collected | `asyncio.create_task()` keeps reference |
| No error handling in task | Silent failures | Always wrap in try/except + followup |
| Multiple `response.send_message()` | "Interaction already responded" | Only ONE initial response, then `followup` |
| Not returning after immediate response | Falls through to defer | `return` after creating background task |

## Related References

- `references/voice-jarvis.md` — Voice command implementation using this pattern
- `references/troubleshooting.md` — Interaction timeout troubleshooting entry
- Discord.py docs: <https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.InteractionResponse.send_message>