# Thread Management & Hermes Session Mapping

## ThreadSession Dataclass

```python
@dataclass
class ThreadSession:
    thread_id: int              # Discord thread ID (snowflake)
    channel_id: int             # Parent channel ID
    guild_id: int               # Guild/server ID
    owner_id: int               # Creator user ID
    hermes_session_id: Optional[str] = None  # Hermes session (when linked)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    topic: str = ""             # Thread topic/description
    is_active: bool = True      # False = archived
```

## Lifecycle Methods

### `register_thread(thread, owner_id, topic, hermes_session_id=None)`
Called when:
- `/hermes thread create` executed
- Auto-provisioning creates initial threads
- Mention in non-Hermes thread creates new thread

**Actions**:
1. Creates `ThreadSession` with metadata
2. Stores in `_threads[thread_id]`
3. Indexes in `_channel_threads[channel_id]`
4. Calls `_save_persistence()`

### `get_session(thread_id) → Optional[ThreadSession]`
Primary lookup for message routing. Returns session if thread is registered and active.

### `update_activity(thread_id)`
Called on every message in a registered thread. Updates `last_activity` for cleanup tracking.

### `set_hermes_session(thread_id, session_id)`
Links thread to Hermes session. Called when:
- First `@Hermes` message in thread → Gateway creates session → callback stores ID
- Thread unarchived → existing `hermes_session_id` restored

### `archive_thread(thread_id) → bool`
Marks `is_active = False`. **Preserves** `hermes_session_id` in JSON.
Called by:
- `/hermes thread archive`
- `archive_thread_by_id()` (Discord API archive)

### `unarchive_thread(thread_id) → bool`
Marks `is_active = True`, updates `last_activity`.
If `hermes_session_id` exists → logs restoration info.
Called by:
- Message in archived thread (auto-unarchive in `on_message`)
- Manual unarchive via Discord UI (detected in `on_thread_update`)

## Persistence

### File Location
`~/.hermes/discord_threads.json`

### Schema
```json
{
  "threads": [
    {
      "thread_id": 1516641040352673924,
      "channel_id": 1516397585701666962,
      "guild_id": 1516397584942370836,
      "owner_id": 1516328637526179870,
      "hermes_session_id": "20260617_001234_abc123",
      "created_at": "2026-06-17T00:10:02.689",
      "last_activity": "2026-06-17T00:12:35.977",
      "topic": "Session Management",
      "is_active": true
    }
  ],
  "saved_at": "2026-06-17T00:12:35.978"
}
```

### Load (`_load_persistence()`)
- Called in `ThreadManager.__init__`
- Reads JSON, reconstructs `ThreadSession` objects
- Rebuilds `_threads` and `_channel_threads` indexes
- Logs count loaded

### Save (`_save_persistence()`)
- Called after EVERY mutation: register, archive, unarchive, cleanup
- Writes atomic (via temp file + rename in `atomic_json_write` utility)
- Includes timestamp

## Message Routing (bot.py `on_message`)

```python
async def on_message(self, message):
    # Skip bot messages, DMs handled separately
    if message.author.bot: return
    
    # Thread message
    if isinstance(message.channel, discord.Thread):
        thread_id = message.channel.id
        session = self.thread_manager.get_session(thread_id)
        
        if session:
            # Update activity
            self.thread_manager.update_activity(thread_id)
            
            # Auto-unarchive if needed
            if not session.is_active:
                self.thread_manager.unarchive_thread(thread_id)
                # Notify user context restored
                await message.channel.send(
                    "🧵 Thread restored. Hermes session reattached.",
                    delete_after=10
                )
            
            # Route to Hermes
            if session.hermes_session_id:
                # Continue existing session
                await self.gateway.chat(session.hermes_session_id, message.content)
            else:
                # First message → create session via mention handler
                await self.handle_mention(message)
        else:
            # Thread not registered (created externally) → register it
            self.thread_manager.register_thread(
                message.channel, message.author.id, topic=message.channel.name
            )
```

## Auto-Unarchive on Message

In `on_message`:
1. Check if thread is registered but `is_active=False`
2. Call `thread_manager.unarchive_thread(thread_id)`
3. Send ephemeral "Context restored" notice
4. Proceed with Hermes routing using preserved `hermes_session_id`

## Discord Event Handlers

### `on_thread_update(before, after)`
- Detects archive/unarchive via `before.archived != after.archived`
- If unarchived via Discord UI → calls `unarchive_thread(after.id)`
- If archived via Discord UI → calls `archive_thread(after.id)` (preserves session)

### `on_thread_delete(thread)`
- Removes from `_threads` and `_channel_threads`
- Calls `_save_persistence()`

## Cleanup Policy

### `_cleanup_inactive_threads(max_age_hours=168)` (1 week)
- Runs hourly via background task
- Iterates all sessions where `!is_active`
- Calculates age: `(now - last_activity).hours`
- If age > 168h: removes from memory, calls `_save_persistence()`
- Returns count cleaned

### Preservation Rules
| State | Preserved in JSON? | Hermes Session Kept? |
|-------|-------------------|---------------------|
| Active | ✅ | ✅ |
| Archived (manual) | ✅ | ✅ |
| Archived (Discord UI) | ✅ | ✅ |
| Deleted (Discord UI) | ❌ (removed) | ❌ |
| Cleaned (1 week inactive) | ❌ (removed) | ❌ |

## Hermes Session Linking

### First Mention in Thread
When user mentions `@Hermes` in a thread without `hermes_session_id`:
1. `handle_mention(message)` creates Gateway session via API
2. Gateway returns `session_id`
3. `thread_manager.set_hermes_session(thread_id, session_id)`
4. Subsequent messages use this session

### Session Restore on Unarchive
When archived thread receives message:
1. `unarchive_thread()` called
2. If `hermes_session_id` exists → logs "will be restored"
3. Next `@Hermes` or message routes to that session
4. Gateway resumes context from session store

## Concurrency

- `ThreadManager` is single-threaded (asyncio event loop)
- All mutations happen in event loop → no locks needed
- `_save_persistence()` is sync I/O but fast (<10ms)
- For high frequency: could batch saves, but current rate is low

## Testing Scenarios

| Scenario | Expected |
|----------|----------|
| Create thread → @Hermes → archive → message → @Hermes | Session preserved, context continues |
| Discord UI archive → Discord UI unarchive → message | Session restored |
| Bot restart → message in thread | Session loaded from JSON, context continues |
| 1 week inactive → cleanup → message | New session created (old removed) |
| Thread deleted in Discord | Removed from manager, JSON updated |