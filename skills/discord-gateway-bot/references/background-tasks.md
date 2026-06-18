# Background Automation Tasks

## Overview

Three async tasks run continuously in the bot's event loop, started in `on_ready()` after auto-provisioning.

## Task 1: System Event Monitor (`_monitor_system_events`)

### Interval: 60 seconds

### Purpose
Scan Hermes Gateway logs for ERROR-level events and auto-create incident threads in `#incidents`.

### Implementation
```python
async def _monitor_system_events(self):
    while not self.is_closed():
        try:
            # Get ERROR logs from last 60s
            proc = await asyncio.create_subprocess_exec(
                "journalctl", "-u", "hermes-gateway", 
                "--since", "60 seconds ago",
                "-p", "err", "--no-pager",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            logs = stdout.decode().strip().split('\n')
            
            # Parse new errors (dedup by timestamp + message)
            for log_line in logs:
                if log_line and not self._is_known_error(log_line):
                    self._mark_error_known(log_line)
                    await self._create_incident_thread(log_line)
                    
        except Exception as e:
            logger.error(f"Event monitor error: {e}")
        
        await asyncio.sleep(60)
```

### Error Deduplication
- Tracks seen errors in `self._known_errors: set[str]`
- Key: hash of `timestamp + message`
- Persists across restarts via JSON file (TODO)

### Incident Thread Creation
```python
async def _create_incident_thread(self, error_log: str):
    # Extract timestamp, service, message
    # Create thread in #incidents
    thread = await self.thread_manager.create_thread(
        channel=self.incidents_channel,
        name=f"🔴 ALERT: {service} - {timestamp}",
        owner=self.user,
        message=f"## Automated Incident\n\n**Service:** {service}\n**Time:** {timestamp}\n\n**Error:**\n```\n{error_log}\n```"
    )
    
    # Post action panel
    view = IncidentActionView(self, thread.id)
    await thread.send(
        embed=discord.Embed(
            title="🚨 Incident Actions",
            description="Choose action:",
            color=discord.Color.red()
        ),
        view=view
    )
```

### IncidentActionView Buttons
| Button | Custom ID | Action |
|--------|-----------|--------|
| 🔍 Investigate | `investigate:{thread_id}` | Spawns agent to analyze logs |
| 📋 View Logs | `logs:{thread_id}` | Shows last 100 gateway log lines |
| 🔄 Restart Gateway | `restart_gateway:{thread_id}` | `sudo systemctl restart hermes-gateway` |
| ✅ Resolve | `resolve:{thread_id}` | Archives thread, marks resolved |

## Task 2: Inactive Thread Cleanup (`_cleanup_inactive_threads`)

### Interval: 1 hour (3600 seconds)

### Purpose
Remove threads inactive > 1 week (168 hours) from memory and persistence.

### Implementation
```python
async def _cleanup_inactive_threads(self):
    while not self.is_closed():
        try:
            removed = self.thread_manager.cleanup_inactive(max_age_hours=168)
            if removed:
                logger.info(f"Cleaned up {removed} inactive thread(s)")
        except Exception as e:
            logger.error(f"Thread cleanup error: {e}")
        await asyncio.sleep(3600)
```

### Cleanup Policy
- Only removes threads where `is_active=False` (archived)
- Age calculated from `last_activity` timestamp
- Default threshold: 168 hours (7 days)
- Removes from `_threads` dict, `_channel_threads` index, and JSON persistence

### Configuration
```python
CLEANUP_INTERVAL_HOURS = 1
CLEANUP_MAX_AGE_HOURS = 168  # 1 week
```

## Task 3: Thread Session Sync (`_sync_thread_sessions`)

### Interval: 5 minutes (300 seconds)

### Purpose
Ensure thread sessions stay in sync with Discord reality:
- Thread still exists
- Thread not deleted
- Activity timestamps current

### Implementation
```python
async def _sync_thread_sessions(self):
    while not self.is_closed():
        try:
            for thread_id, session in list(self.thread_manager._threads.items()):
                # Verify thread still exists in Discord
                thread = self.get_channel(thread_id)
                if not thread:
                    # Thread deleted externally
                    logger.warning(f"Thread {thread_id} deleted externally, removing")
                    del self.thread_manager._threads[thread_id]
                    if session.channel_id in self.thread_manager._channel_threads:
                        self.thread_manager._channel_threads[session.channel_id].discard(thread_id)
                    continue
                
                # Update activity if thread has recent messages
                if hasattr(thread, 'last_message_id') and thread.last_message_id:
                    # Could fetch last message time, but skip for performance
                    pass
                    
            self.thread_manager._save_persistence()
            
        except Exception as e:
            logger.error(f"Thread sync error: {e}")
        
        await asyncio.sleep(300)
```

### Sync Checks
1. **Existence**: Thread still in Discord cache
2. **Archived state**: Matches `session.is_active` (if Discord says archived but we think active, or vice versa)
3. **Permissions**: Bot still has access to channel/thread

## Task Management

### Startup (in `on_ready`)
```python
self._bg_tasks = [
    asyncio.create_task(self._monitor_system_events()),
    asyncio.create_task(self._cleanup_inactive_threads()),
    asyncio.create_task(self._sync_thread_sessions()),
]
```

### Shutdown (in `close`)
```python
async def close(self):
    for task in self._bg_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    await super().close()
```

### Error Handling
- Each task has try/except around main loop
- Errors logged but don't crash other tasks
- Tasks continue running after errors

## Monitoring

### Health Check
```python
# In /hermes status or panel
bg_task_status = {
    "event_monitor": "running" if not bg_tasks[0].done() else "stopped",
    "thread_cleanup": "running" if not bg_tasks[1].done() else "stopped", 
    "thread_sync": "running" if not bg_tasks[2].done() else "stopped",
}
```

### Logs
```
🔄 Background automation tasks started
Cleaned up 3 inactive thread(s)
Event monitor error: [error details]  # non-fatal
```

## Configuration

| Task | Interval | Config Key |
|------|----------|------------|
| Event Monitor | 60s | `MONITOR_INTERVAL=60` |
| Thread Cleanup | 1h | `CLEANUP_INTERVAL=3600` |
| Thread Sync | 5m | `SYNC_INTERVAL=300` |

All intervals configurable via environment variables in `.env`.

## Adding New Background Tasks

Pattern for new tasks:
```python
async def _my_new_task(self):
    while not self.is_closed():
        try:
            # Do work
        except Exception as e:
            logger.error(f"My task error: {e}")
        await asyncio.sleep(INTERVAL)

# In on_ready:
asyncio.create_task(self._my_new_task())
```

## Future Enhancements

- **Event-driven**: Replace polling with Discord webhook events
- **Metrics**: Prometheus metrics for task health
- **Alerting**: Notify if background task stops
- **Persistence**: Save known errors across restarts
- **Dynamic intervals**: Adjust based on load/error rate