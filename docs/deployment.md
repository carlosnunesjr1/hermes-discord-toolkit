# Deployment Guide

Step-by-step deployment to a fresh Ubuntu 24.04 VPS.

## Prerequisites

- VPS with Ubuntu 24.04 (4 vCPU, 8GB RAM minimum)
- Domain managed by Cloudflare
- SSH access as root or sudo user
- Local machine with this repo cloned

## 1. VPS Initial Setup

```bash
# On VPS as root
apt update && apt upgrade -y
apt install -y curl git python3 python3-venv nodejs npm caddy

# Install Hermes Agent
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Create deploy user (replace 'carlos' with your username)
useradd -m -s /bin/bash -G sudo carlos
passwd carlos
```

## 2. Cloudflare DNS

In Cloudflare Dashboard → DNS → Records, add **Proxied** CNAME records:

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | gateway | @ | ✅ |
| CNAME | workspace | @ | ✅ |
| CNAME | career | @ | ✅ |
| CNAME | pim | @ | ✅ |
| CNAME | terminal | @ | ✅ |
| CNAME | centraldecomando | @ | ✅ |
| CNAME | control-daemon | @ | ✅ |
| CNAME | nexus-pim | @ | ✅ |

SSL/TLS → **Full (Strict)**
Edge Certificates → **Always Use HTTPS: On**

## 3. Local Configuration

```bash
# On your local machine
cd hermes-discord-toolkit
./scripts/setup.sh
# Enter your values when prompted
```

## 4. Render Templates

```bash
./scripts/render-templates.sh
# Review rendered output
cat rendered/caddy/Caddyfile
cat rendered/env/.env
```

## 5. Deploy

```bash
# Set deploy target (if different from DOMAIN)
export DEPLOY_HOST=your-vps-ip-or-domain
export DEPLOY_USER=root  # or your sudo user

./scripts/deploy.sh
```

## 6. Verify Deployment

```bash
# Health checks (run locally)
curl https://gateway.yourdomain.com/health
curl https://workspace.yourdomain.com
curl https://yourdomain.com

# On VPS - check services
systemctl status hermes-gateway@carlos
systemctl status hermes-workspace@carlos
systemctl status caddy

# Logs
journalctl -u hermes-gateway@carlos -f
journalctl -u hermes-workspace@carlos -f
```

## 7. Post-Deploy

### Hermes Gateway Config

```bash
# On VPS
hermes config set api_server.enabled true
hermes config set api_server.port 8642
hermes config set api_server.key YOUR_API_SERVER_KEY
hermes gateway restart
```

### Discord Bot Setup

```bash
# In Discord Developer Portal:
# 1. Bot → Privileged Gateway Intents → Enable ALL
# 2. Copy Token → paste in setup.sh
# 3. OAuth2 → URL Generator → bot + applications.commands
# 4. Invite to your server
```

### Install Skills

```bash
# On VPS (as deploy user)
hermes skills install https://github.com/carlosnunesjr1/hermes-discord-toolkit/raw/main/skills/discord-gateway-bot/SKILL.md
hermes skills install https://github.com/carlosnunesjr1/hermes-discord-toolkit/raw/main/skills/discord-forum-idea-incubator/SKILL.md
```

## Troubleshooting

### Gateway not responding

```bash
# Check logs
journalctl -u hermes-gateway@carlos -n 50

# Check port
ss -tlnp | grep 8642

# Test locally
curl http://127.0.0.1:8642/health
```

### Caddy SSL issues

```bash
# Check Caddy logs
journalctl -u caddy -n 50

# Test config
caddy validate --config /etc/caddy/Caddyfile

# Force reload
systemctl reload caddy
```

### Workspace not starting

```bash
# Check workspace logs
journalctl -u hermes-workspace@carlos -n 50

# Common fix: clear Vite cache
cd /home/carlos/hermes-workspace
rm -rf node_modules/.vite .tanstack dist src/routeTree.gen.ts
systemctl restart hermes-workspace@carlos
```

### Discord bot not receiving messages

1. Discord Developer Portal → Bot → **Message Content Intent: ON**
2. Check `DISCORD_ALLOWED_USERS` in `.env.local`
3. Verify bot is in the server with correct permissions

## Rollback

```bash
# Stop services
systemctl stop hermes-gateway@carlos hermes-workspace@carlos

# Restore previous config (if backed up)
cp /opt/hermes/.env.backup /opt/hermes/.env

# Restart
systemctl start hermes-gateway@carlos hermes-workspace@carlos
```

## Backup Strategy

```bash
# Add to cron on VPS
# /etc/cron.daily/hermes-backup
#!/bin/bash
tar -czf /backup/hermes-$(date +%F).tar.gz /home/carlos/.hermes /opt/hermes/.env
find /backup -name "hermes-*.tar.gz" -mtime +7 -delete
```

## Scaling Notes

- Each subdomain = one upstream service
- Add new services by adding Caddy block + systemd unit
- Hermes Gateway handles multiple skills/platforms on single port
- Dashboard (port 9119) required for Workspace enhanced features