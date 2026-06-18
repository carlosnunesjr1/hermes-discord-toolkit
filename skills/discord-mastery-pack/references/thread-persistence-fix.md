# Thread Persistence — Implementation & Bug Fix Reference

## Overview
Discord thread ↔ Hermes session persistence with automatic archive/unarchive context preservation.

---

## File Location
- **Persistence**: `~/.hermes/discord_threads.json`
- **Manager**: `/home/carlos/hermes-discord-bot/thread_manager.py`

---

## Data Structure (CORRECT Format)
```json
{
  "threads": [
    {
      "thread_id": 1516641685302546472,
      "channel_id": 1516397585701666962,
      "guild_id": 1516397584942370836,
      "owner_id": 1516328637526179870,
      "hermes_session_id": "20260616_165539_3c46c198",
      "created_at": "2026-06-17T00:12:35.977000",
      "last_activity": "2026-06-17T00:12:35.977000",
      "topic": "ola",
      "is_active": true
    }
  ],
  "saved_at": "2026-06-17T00:28:36.987000"
}
```

---

## Bug Fixed: List vs Dict Format
**Error**: `'list' object has no attribute 'get'`

**Root Cause**: Old persistence file was a raw list `[]` instead of dict with `threads` key.

**Invalid Format (causes error)**:
```json
[]  // or [{...}, {...}]
```

**Valid Format (required)**:
```json
{
  "threads": [...],
  "saved_at": "2026-06-17T00:28:36.987000"
}
```

**Fix Applied**: 
```python
# In thread_manager.py _load_persistence()
for session_data in data.get("threads", []):  # .get() requires dict
    session = ThreadSession.from_dict(session_data)
    self._threads[session.thread_id] = session
```

---

## ThreadSession Dataclass
```python
@dataclass
class ThreadSession:
    thread_id: int
    channel_id: int
    guild_id: int
    owner_id: int
    hermes_session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    topic: str = ""
    is_active: bool = True
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["last_activity"] = self.last_activity.isoformat()
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "ThreadSession":
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        return cls(**data)
```

---

## Persistence Methods
```python
def _load_persistence(self):
    """Load thread sessions from disk."""
    if not PERSISTENCE_FILE.exists():
        logger.info("No thread persistence file found, starting fresh")
        return
    
    try:
        with open(PERSISTENCE_FILE, "r") as f:
            data = json.load(f)
        
        for session_data in data.get("threads", []):
            session = ThreadSession.from_dict(session_data)
            self._threads[session.thread_id] = session
            # ... register in _channel_threads
        
        logger.info(f"Loaded {len(self._threads)} thread sessions from persistence")
    except Exception as e:
        logger.error(f"Failed to load thread persistence: {e}")

def _save_persistence(self):
    """Save thread sessions to disk."""
    try:
        PERSISTENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "threads": [s.to_dict() for s in self._threads.values()],
            "saved_at": datetime.now().isoformat()
        }
        with open(PERSISTENCE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved {len(self._threads)} thread sessions to persistence")
    except Exception as e:
        logger.error(f"Failed to save thread persistence: {e}")
```

---

## Archive/Unarchive with Session Preservation

### Archive (preserves session)
```python
async def archive_thread_by_id(self, thread_id: int, reason: str = "Archived via Hermes") -> bool:
    session = self.get_session(thread_id)
    if not session:
        return False
    
    thread = self.bot.get_channel(thread_id)
    if isinstance(thread, discord.Thread):
        try:
            # Preserve Hermes session ID
            if session.hermes_session_id:
                logger.info(f"Preserving Hermes session {session.hermes_session_id} for archived thread {thread_id}")
            
            await thread.edit(archived=True, reason=reason)
            self.archive_thread(thread_id)  # sets is_active=False
            self._save_persistence()
            return True
        except discord.HTTPException as e:
            logger.error(f"Failed to archive thread {thread_id}: {e}")
            return False
    return False
```

### Unarchive (restores session)
```python
def unarchive_thread(self, thread_id: int) -> bool:
    if thread_id in self._threads:
        self._threads[thread_id].is_active = True
        self._threads[thread_id].last_activity = datetime.now()
        
        if self._threads[thread_id].hermes_session_id:
            logger.info(f"Thread {thread_id} unarchived, Hermes session {self._threads[thread_id].hermes_session_id} will be restored")
        
        self._save_persistence()
        return True
    return False
```

### Auto-Unarchive on Message
```python
async def _handle_thread_message(self, message: discord.Message):
    thread = message.channel
    session = self.thread_manager.get_session(thread.id)
    
    if not session:
        return
    
    # Auto-unarchive if archived thread receives message
    if not session.is_active:
        self.thread_manager.unarchive_thread(thread.id)
        logger.info(f"Auto-unarchived thread {thread.id} on new message")
    
    self.thread_manager.update_activity(thread.id)
    # ... process message
```

---

## File Location
- **Persistence file**: `~/.hermes/discord_threads.json`
- **Manager**: `/home/carlos/hermes-discord-bot/thread_manager.py`
- **PERSISTENCE_FILE**: `Path.home() / ".hermes" / "discord_threads.json"`

---

## Cleanup Task
```python
async def _cleanup_inactive_threads(self):
    while not self.is_closed():
        await asyncio.sleep(3600)  # 1 hour
        removed = self.thread_manager.cleanup_inactive(max_age_hours=168)  # 1 week
        if removed:
            logger.info(f"Cleaned up {removed} inactive threads (>1 week)")
```

---

## Fix Checklist for New Deployments
- [ ] Ensure `~/.hermes/discord_threads.json` exists with correct format
- [ ] Verify `_load_persistence()` handles missing file gracefully
- [ ] Test archive → message → auto-unarchive preserves `hermes_session_id`
- [ ] Test bot restart loads persisted threads correctly
- [ ] Verify cleanup task removes old inactive threads