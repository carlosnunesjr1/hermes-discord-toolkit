# Configuration Guide

Complete reference for all configuration variables in `~/.config/hermes-discord-toolkit/.env.local`.

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Discord bot token from Developer Portal | `MTIz...` |
| `DISCORD_ALLOWED_USERS` | Comma-separated user IDs allowed to use bot | `123456789,987654321` |
| `DISCORD_HOME_CHANNEL` | Default channel ID for bot messages | `111222333` |
| `DOMAIN` | Base domain (Cloudflare managed) | `example.com` |

## Subdomains (auto-configured)

| Variable | Default | Full URL |
|----------|---------|----------|
| `SUBDOMAIN_GATEWAY` | `gateway` | `gateway.example.com` |
| `SUBDOMAIN_WORKSPACE` | `workspace` | `workspace.example.com` |
| `SUBDOMAIN_CAREER` | `career` | `career.example.com` |
| `SUBDOMAIN_PIM` | `pim` | `pim.example.com` |
| `SUBDOMAIN_TERMINAL` | `terminal` | `terminal.example.com` |
| `SUBDOMAIN_CENTRAL` | `centraldecomando` | `centraldecomando.example.com` |
| `SUBDOMAIN_CONTROL` | `control-daemon` | `control-daemon.example.com` |
| `SUBDOMAIN_NEXUS` | `nexus-pim` | `nexus-pim.example.com` |

## Ports (Hermes defaults)

| Variable | Default | Service |
|----------|---------|---------|
| `GW_PORT` | `8642` | Hermes Gateway API |
| `WS_PORT` | `3002` | Hermes Workspace UI |
| `DASH_PORT` | `9119` | Hermes Dashboard |
| `CAREER_PORT` | `2019` | Career Hub |
| `PIM_PORT` | `9121` | Nexus PIM |
| `TERMINAL_PORT` | `7681` | ttyd Terminal |
| `CENTRAL_PORT` | `9130` | Central de Comando |
| `CONTROL_PORT` | `9120` | Control Daemon |
| `NEXUS_PORT` | `9121` | Nexus PIM (alt) |

## API Server (Gateway)

| Variable | Default | Description |
|----------|---------|-------------|
| `API_SERVER_ENABLED` | `true` | Enable API server on gateway |
| `API_SERVER_KEY` | **required** | 32-char hex key (`openssl rand -hex 32`) |
| `API_SERVER_PORT` | `{{GW_PORT}}` | Same as gateway port |
| `API_SERVER_HOST` | `127.0.0.1` | Bind address |
| `API_SERVER_MODEL_NAME` | `hermes-agent` | Model name for `/v1/models` |

## Webhook (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBHOOK_ENABLED` | `true` | Enable webhook endpoint |
| `WEBHOOK_PORT` | `{{GW_PORT}}+2` | Webhook port (e.g. 8644) |
| `WEBHOOK_SECRET` | **required** | 32-char hex secret (`openssl rand -hex 32`) |

## STT/TTS (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `STT_ENABLED` | `true` | Enable voice-to-text |
| `STT_PROVIDER` | `local` | `local`, `groq`, `openai`, `mistral` |
| `TTS_PROVIDER` | `edge` | `edge`, `elevenlabs`, `openai`, `minimax`, `mistral` |

## Gateway

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_ALLOW_ALL_USERS` | `false` | Allow any Discord user (dev only) |

## Headroom (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADROOM_ENABLED` | `false` | Enable context compression proxy |
| `HEADROOM_URL` | `http://127.0.0.1:8799` | Headroom proxy URL |

## Generating Secrets

```bash
# API Server Key (32 chars = 256 bits)
openssl rand -hex 32

# Webhook Secret
openssl rand -hex 32
```

## Cloudflare DNS Setup

For each subdomain, create a **Proxied** CNAME record:

```
Type: CNAME
Name: gateway
Target: @
Proxy: Enabled (orange cloud)

Name: workspace
Target: @
Proxy: Enabled

...repeat for all subdomains
```

SSL mode: **Full (Strict)** — Cloudflare handles TLS, Caddy runs HTTP only on port 80.

## Systemd Service Names

Services install as templated units:

```bash
systemctl enable hermes-gateway@carlos
systemctl enable hermes-workspace@carlos
systemctl start hermes-gateway@carlos
systemctl start hermes-workspace@carlos
```

Replace `carlos` with your VPS username.

## Environment File Locations

| File | Location | Purpose |
|------|----------|---------|
| Personal config | `~/.config/hermes-discord-toolkit/.env.local` | Your values (never committed) |
| Rendered env | `./rendered/env/.env` | Deployed to `/opt/hermes/.env` on VPS |
| Template | `templates/env/.env.example` | Placeholders only (committed) |

## Validation

```bash
# Check config exists
./scripts/validate.sh

# Render and inspect
./scripts/render-templates.sh
cat rendered/caddy/Caddyfile
cat rendered/env/.env
```