# Resilience Layer Implementation

## Overview
Production-grade resilience patterns for the Discord bot, preventing cascade failures, guaranteeing message delivery, and enabling self-healing.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ResilienceManager                            │
├──────────────────┬──────────────────┬──────────────────────────────┤
│  Circuit Breaker │  Message Queue   │   Health Monitor + Sync      │
│  (per target)    │  (persistent)    │   (every 30s)                │
└──────────────────┴──────────────────┴──────────────────────────────┘
```

## 1. Circuit Breakers (`resilience.py`)

### Configuration
| Circuit | Failure Threshold | Recovery Timeout | Protects |
|---------|------------------|------------------|----------|
| `gateway` | 3 | 30s | Hermes Gateway HTTP |
| `discord_ws` | 5 | 60s | Discord Gateway WebSocket |
| `webhook_http` | 3 | 30s | Webhook HTTP delivery |

### State Machine
```
CLOSED (normal) ──N failures──► OPEN (rejecting) ──timeout──► HALF_OPEN (testing) ──success──► CLOSED
                                                               │
                                                               └──failure──► OPEN
```

### Implementation
```python
class CircuitBreaker:
    def __init__(self, name, failure_threshold=3, recovery_timeout=30.0):
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = 0
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN allows one test call
```

### Usage
```python
async def call_with_breaker(self, circuit_name: str, func, *args, **kwargs):
    breaker = self.circuits[circuit_name]
    if not breaker.can_execute():
        raise CircuitOpenError(f"Circuit {circuit_name} is OPEN")
    
    try:
        result = await func(*args, **kwargs)
        breaker.record_success()
        return result
    except Exception as e:
        breaker.record_failure()
        raise
```

## 2. Persistent Message Queue

### Storage
- **File**: `~/.hermes/resilience/outbound_queue.json`
- **Survives**: bot restart, gateway restart, system reboot

### Queue Entry Schema
```json
{
  "id": "msg_abc123",
  "content": "Message text...",
  "channel_id": 1234567890,
  "thread_id": 9876543210,
  "priority": 0,
  "attempts": 0,
  "max_attempts": 5,
  "created_at": "2026-06-17T02:30:00.000",
  "next_retry": "2026-06-17T02:30:01.000",
  "metadata": {}
}
```

### Retry Strategy
| Attempt | Backoff | Max |
|---------|---------|-----|
| 1 | 1s | |
| 2 | 2s | |
| 3 | 4s | |
| 4 | 8s | |
| 5 | 16s | max 60s |

### Priority Ordering
1. `priority < 0` → Urgent (errors, alerts)
2. `priority == 0` → Normal
3. `priority > 0` → Background (logs, metrics)

### Cleanup
- Completed messages → removed immediately
- Old completed (> 24h) → removed on startup
- Failed max attempts → moved to dead letter log

## 3. Fallback Delivery Chain

### Automatic Priority (Implemented in `gateway/platforms/webhook.py`)

```python
async def _deliver_discord_webhook(self, content: str, delivery: dict):
    # 1. FIRST: Discord WS Adapter (Bot Gateway) — PREFERRED
    if self.gateway_runner:
        adapter = self.gateway_runner.adapters.get(Platform.DISCORD)
        if adapter and adapter.is_connected:
            result = await adapter.send(chat_id, content, metadata=metadata)
            if result.success:
                return result  # Success via WS, zero config
            # Log warning, fall through
    
    # 2. SECOND: HTTP Webhook (manual URL) — FALLBACK
    webhook_url = extra.get("webhook_url") or os.getenv(f"DISCORD_WEBHOOK_{channel_id}") or os.getenv("DISCORD_DEFAULT_WEBHOOK_URL")
    if webhook_url:
        return await self._deliver_via_http_webhook(webhook_url, content)
    
    # 3. THIRD: Local Queue (guaranteed eventual)
    return await self._queue_for_retry(content, delivery)
```

### Priority Rationale
| Method | Config Required | Latency | Reliability | Use Case |
|--------|----------------|---------|-------------|----------|
| Discord WS | Bot running | ~50ms | High (connected) | **Default, preferred** |
| HTTP Webhook | Manual URL | ~200ms | Medium (retries) | When WS down |
| Local Queue | None | Deferred | Guaranteed (persisted) | All down |

## 4. Health Checks (Every 30s)

### Registered Checks
```python
health_checker.register("discord_ws", bot._check_discord_ws)  # latency + connected
health_checker.register("gateway", bot._check_gateway)         # GET /health
health_checker.register("webhook", bot._check_webhook)         # GET :8644/health
```

### Status Aggregation
```python
def get_overall_status() -> str:
    statuses = [check_result for check_result in results]
    if all(s.get("status") == "healthy" for s in statuses):
        return "healthy"
    elif any(s.get("status") == "unhealthy" for s in statuses):
        return "unhealthy"
    else:
        return "degraded"
```

### Discord Command: `/hermes health`
Shows:
- Overall status (🟢/🟡/🔴)
- Discord WS latency
- Gateway status
- Circuit breaker states (🟢 CLOSED / 🟡 HALF_OPEN / 🔴 OPEN)
- Queue pending/total counts
- Health check latencies
- Sync manager states

## 5. Sync Managers

For operations needing retry with state tracking (brain sync, etc.):

### State File
`~/.hermes/resilience/{name}_sync.json`
```json
{
  "pending": 2,
  "last_sync": 1718600000.123,
  "operations": [
    {"id": "sync_001", "status": "in_progress", "attempts": 1},
    {"id": "sync_002", "status": "queued", "attempts": 0}
  ]
}
```

### Usage
```python
sync_mgr = resilience.get_sync_manager("brain_sync")
op_id = sync_mgr.queue_operation({"areas": ["projetos", "financas"]})
# Later, when operation completes:
sync_mgr.mark_success(op_id)
# Or on failure:
sync_mgr.mark_failure(op_id, error="timeout")
```

## 6. Systemd Watchdog Integration

### Service Unit (`hermes-discord-bot.service`)
```ini
WatchdogSec=60              # systemd kills if no notify in 60s
StartLimitIntervalSec=60    # restart loop prevention
StartLimitBurst=3           # max 3 restarts in 60s
NotifyAccess=main
```

### Bot Implementation
```python
# Startup
if SDNOTIFY_AVAILABLE:
    self._sd_notifier = sdnotify.SystemdNotifier()
    self._watchdog_task = asyncio.create_task(self._watchdog_notifier())

async def _watchdog_notifier(self):
    while not self.is_closed():
        self._sd_notifier.notify("WATCHDOG=1")
        await asyncio.sleep(30)  # Every 30s (half of WatchdogSec)

# Shutdown
async def close(self):
    if self._sd_notifier:
        self._sd_notifier.notify("STOPPING=1")
    if self._watchdog_task:
        self._watchdog_task.cancel()
```

### Benefits
- **Hang detection**: If event loop blocks > 60s → systemd kills & restarts
- **Restart loop prevention**: Max 3 restarts/60s prevents thrashing
- **Graceful shutdown**: `STOPPING=1` tells systemd it's intentional

## Configuration

### No `.env` config needed — all internal
```python
# In bot.py __init__
self.resilience = ResilienceManager(self)

# In on_ready
self.resilience.health_checker.register("discord_ws", self._check_discord_ws)
self.resilience.health_checker.register("gateway", self._check_gateway)
self.resilience.health_checker.register("webhook", self._check_webhook)
await self.resilience.start()
```

## Monitoring

### `/hermes health` Output
```
🟢 System Health Check
Overall: HEALTHY
Discord WS Latency: 42.3ms
Gateway: ok

Circuit Breakers:
🟢 gateway: closed
🟢 discord_ws: closed
🟢 webhook_http: closed

Queue:
Pending: 0
Total: 0

Checks:
discord_ws: healthy (42ms)
gateway: healthy (15ms)
webhook: healthy (8ms)

Sync Managers:
brain_sync: 0 pending, last sync 3600s ago
```

## Troubleshooting

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| Circuit OPEN | External service failing | Check target service logs, wait for recovery |
| Queue growing | Delivery failing persistently | Check webhook URLs, Discord bot connection |
| Overall DEGRADED | One check unhealthy | Run `/hermes health` for details |
| Watchdog killing bot | Event loop blocked > 60s | Check for blocking calls, add async |
| Restart loop | `StartLimitBurst` hit | Fix root cause, don't just restart |