# Complete Service Mapping — Discord Channels ↔ Running Infrastructure

## Overview
Complete mapping of 28 Discord channels to actual running services in the infrastructure.

---

## Channel ↔ Service Mapping Table

| Channel | Service | Type | Port | Status | Category |
|---------|---------|------|------|--------|----------|
| #career-hub | cn-tech-career-hub | Docker | 2019 | ✅ Healthy | CN-TECH |
| #nexus-pim | cn-tech-nectar-summo | Docker | 9121/3001 | ✅ Healthy | CN-TECH |
| #nectar | cn-tech-nectar-summo | Docker | 9121/3001 | ✅ Healthy | CN-TECH |
| #central-comando | cn-tech-centraldecomando | Docker | 9130 | ✅ Healthy | CN-TECH |
| #control-daemon | cn-tech-control-daemon | Docker | 9120 | ✅ Healthy | CN-TECH |
| #redis | cn_tech-redis-1 | Docker | 6379 | ✅ Healthy | CN-TECH |
| #workspace | hermes-workspace.service | systemd | 3002 | ✅ Active | WORKSPACE |
| #dashboard | hermes-dashboard.service | systemd | ? | ✅ Active | WORKSPACE |
| #gateway | hermes-gateway.service | systemd | 8642 | ✅ Active | WORKSPACE |
| #webhook | Webhook HTTP | Docker | 8644 | ✅ Active | WORKSPACE |
| #deploy | hermes-gateway + bot | - | - | ✅ Active | HERMES-OPS |
| #monitor | hermes-gateway + bot | - | - | ✅ Active | HERMES-OPS |
| #incidents | hermes-gateway + bot | - | - | ✅ Active | HERMES-OPS |
| #logs | hermes-gateway + bot | - | - | ✅ Active | HERMES-OPS |
| #vps-health | VPS metrics | - | - | ✅ Active | INFRA |
| #docker | Docker containers | - | - | ✅ Active | INFRA |
| #network | Network/DNS | - | - | ✅ Active | INFRA |
| #backups | Backup systems | - | - | ✅ Active | INFRA |
| #active | Agent orchestrator | - | - | ✅ Active | AGENTS |
| #spawn | Agent spawner | - | - | ✅ Active | AGENTS |
| #history | Agent history | - | - | ✅ Active | AGENTS |
| #features | Feature tracking | - | - | ✅ Active | TASKS |
| #bugs | Bug tracking | - | - | ✅ Active | TASKS |
| #research | Research tasks | - | - | ✅ Active | TASKS |
| #docs | Documentation | - | - | ✅ Active | TASKS |
| #memory | Memory system | - | - | ✅ Active | BRAIN |
| #context | Context inspection | - | - | ✅ Active | BRAIN |
| #sessions | Session management | - | - | ✅ Active | BRAIN |
| #knowledge | Knowledge base | - | - | ✅ Active | BRAIN |

---

## Verification Commands

### Docker Services
```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
# cn-tech-career-hub      Up 43 minutes (healthy)      127.0.0.1:2019->2019/tcp
# cn-tech-nectar-summo    Up About an hour (healthy)   127.0.0.1:9121->3001/tcp
# cn_tech-redis-1         Up 5 hours (healthy)         6379/tcp
# cn-tech-control-daemon  Up 7 hours (healthy)         127.0.0.1:9120->9120/tcp
# cn-tech-centraldecomando Up 7 hours (healthy)        127.0.0.1:9130->9130/tcp
```

### Systemd Services
```bash
systemctl list-units --type=service --state=running | grep -E "(hermes|cn-tech)"
# hermes-dashboard.service       loaded active running Hermes Dashboard Service
# hermes-discord-bot.service     loaded active running Hermes Discord Bot
# hermes-workspace.service       loaded active running Hermes Workspace (port 3002)

# Note: hermes-gateway.service (system) is DISABLED
# User service is the active one:
systemctl --user status hermes-gateway
```

### Webhook HTTP
```bash
curl http://localhost:8644/health
# {"status": "ok", "platform": "webhook"}

# Webhook route test
BODY='{"content":"test"}'
SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac 'discord-webhook-secret-2026' | cut -d' ' -f2)
curl -s -X POST http://localhost:8644/webhooks/discord \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIG" \
  -d "$BODY"
# {"status": "accepted", "route": "discord", "event": "unknown", "delivery_id": "..."}
```

### Discord Bot
```bash
systemctl status hermes-discord-bot
./deploy.sh status
./deploy.sh logs
```

---

## Category Structure (7 Categories × 4 Channels = 28 Channels)

### 🚀 HERMES-OPS (4)
| Channel | Purpose |
|---------|---------|
| #deploy | Deploys & releases |
| #monitor | Monitoring & alerts |
| #incidents | Active incidents |
| #logs | Centralized logs |

### 🔧 CN-TECH (6)
| Channel | Service | Port |
|---------|---------|------|
| #career-hub | cn-tech-career-hub | 2019 |
| #nexus-pim | cn-tech-nectar-summo | 9121/3001 |
| #nectar | cn-tech-nectar-summo | 9121/3001 |
| #central-comando | cn-tech-centraldecomando | 9130 |
| #control-daemon | cn-tech-control-daemon | 9120 |
| #redis | cn_tech-redis-1 | 6379 |

### 🧱 WORKSPACE (5)
| Channel | Service | Port/Type |
|---------|---------|-----------|
| #workspace | hermes-workspace.service | 3002 |
| #dashboard | hermes-dashboard.service | systemd |
| #gateway | hermes-gateway.service | 8642 |
| #webhook | Webhook HTTP | 8644 |

### 🏗️ INFRA (4)
| Channel | Purpose |
|---------|---------|
| #vps-health | VPS health & metrics |
| #docker | Containers & images |
| #network | Network & DNS |
| #backups | Backups & restore |

### 🤖 AGENTS (3)
| Channel | Purpose |
|---------|---------|
| #active | Active agents |
| #spawn | Spawn new agent |
| #history | Agent history |

### 📋 TASKS (4)
| Channel | Purpose |
|---------|---------|
| #features | New features |
| #bugs | Bugs & hotfixes |
| #research | Research & spikes |
| #docs | Documentation |

### 🧠 BRAIN (4)
| Channel | Purpose |
|---------|---------|
| #memory | Memory & knowledge |
| #context | Context inspection |
| #sessions | Session management |
| #knowledge | Knowledge base |

---

## Auto-Provisioning Verification
```bash
# Check categories created
sudo journalctl -u hermes-discord-bot --since '10 minutes ago' --no-pager | grep "Created category"
# Created category: 🚀 HERMES-OPS
# Created category: 🔧 CN-TECH
# Created category: 🧱 WORKSPACE
# Created category: 🏗️ INFRA
# Created category: 🤖 AGENTS
# Created category: 📋 TASKS
# Created category: 🧠 BRAIN

# Check threads created
sudo journalctl -u hermes-discord-bot --since '10 minutes ago' --no-pager | grep "Created initial thread" | wc -l
# 28 (one per channel)
```

---

## Panel Auto-Post Channels
System panel auto-posted in key channels:
- #deploy
- #monitor  
- #spawn
- #memory

---

## Notes
- All 28 channels auto-created on bot startup
- Each gets initial thread with bot owner
- SystemSelectView panel posted in 4 key channels
- Background tasks monitor, cleanup, sync sessions
- Thread persistence preserves Hermes sessions