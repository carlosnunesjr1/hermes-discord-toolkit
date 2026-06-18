#!/bin/bash
# setup.sh — Interactive setup for hermes-discord-toolkit
# Creates ~/.config/hermes-discord-toolkit/.env.local
# Run once per machine

set -euo pipefail

CONFIG_DIR="$HOME/.config/hermes-discord-toolkit"
CONFIG_FILE="$CONFIG_DIR/.env.local"
TEMPLATE_FILE="$(dirname "$0")/../templates/env/.env.example"

mkdir -p "$CONFIG_DIR"

echo "🔧 Hermes Discord Toolkit — Setup"
echo "   Config will be saved to: $CONFIG_FILE"
echo ""

if [[ -f "$CONFIG_FILE" ]]; then
    read -p "Config already exists. Overwrite? [y/N]: " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Discord
echo "📱 Discord Bot Configuration"
read -p "Discord Bot Token: " DISC_BOT_TOKEN
read -p "Allowed User IDs (comma-separated): " DISCORD_ALLOWED_USERS
read -p "Home Channel ID: " DISCORD_HOME_CHANNEL

# Domain
echo ""
echo "🌐 Domain Configuration"
read -p "Base domain (e.g. example.com): " DOMAIN

# Ports (with defaults)
echo ""
echo "🔌 Ports (press Enter for defaults)"
read -p "Gateway Port [8642]: " GW_PORT; GW_PORT=${GW_PORT:-8642}
read -p "Workspace Port [3002]: " WS_PORT; WS_PORT=${WS_PORT:-3002}
read -p "Dashboard Port [9119]: " DASH_PORT; DASH_PORT=${DASH_PORT:-9119}
read -p "Career Port [2019]: " CAREER_PORT; CAREER_PORT=${CAREER_PORT:-2019}
read -p "PIM Port [9121]: " PIM_PORT; PIM_PORT=${PIM_PORT:-9121}
read -p "Terminal Port [7681]: " TERMINAL_PORT; TERMINAL_PORT=${TERMINAL_PORT:-7681}
read -p "Central Port [9130]: " CENTRAL_PORT; CENTRAL_PORT=${CENTRAL_PORT:-9130}
read -p "Control Port [9120]: " CONTROL_PORT; CONTROL_PORT=${CONTROL_PORT:-9120}
read -p "Nexus Port [9121]: " NEXUS_PORT; NEXUS_PORT=${NEXUS_PORT:-9121}

# Generate secrets
API_SERVER_KEY=$(openssl rand -hex 32)
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Optional features
echo ""
echo "⚙️  Optional Features"
read -p "Enable Headroom (context compression)? [y/N]: " HEADROOM_ENABLED
HEADROOM_ENABLED=${HEADROOM_ENABLED:-false}
read -p "Allow all users on gateway? [y/N]: " GATEWAY_ALLOW_ALL_USERS
GATEWAY_ALLOW_ALL_USERS=${GATEWAY_ALLOW_ALL_USERS:-false}

# Generate .env.local
cat > "$CONFIG_FILE" <<EOF
# Generated on $(date)
# Hermes Discord Toolkit — Personal Configuration
# DO NOT COMMIT THIS FILE

# Discord Bot
DISCORD_BOT_TOKEN=$DISC_BOT_TOKEN
DISCORD_ALLOWED_USERS=$DISCORD_ALLOWED_USERS
DISCORD_HOME_CHANNEL=$DISCORD_HOME_CHANNEL

# Domain
DOMAIN=$DOMAIN

# Subdomains
SUBDOMAIN_GATEWAY=gateway
SUBDOMAIN_WORKSPACE=workspace
SUBDOMAIN_CAREER=career
SUBDOMAIN_PIM=pim
SUBDOMAIN_TERMINAL=terminal
SUBDOMAIN_CENTRAL=centraldecomando
SUBDOMAIN_CONTROL=control-daemon
SUBDOMAIN_NEXUS=nexus-pim

# Ports
GW_PORT=$GW_PORT
WS_PORT=$WS_PORT
DASH_PORT=$DASH_PORT
CAREER_PORT=$CAREER_PORT
PIM_PORT=$PIM_PORT
TERMINAL_PORT=$TERMINAL_PORT
CENTRAL_PORT=$CENTRAL_PORT
CONTROL_PORT=$CONTROL_PORT
NEXUS_PORT=$NEXUS_PORT

# API Server
API_SERVER_ENABLED=true
API_SERVER_KEY=$API_SERVER_KEY
API_SERVER_PORT=$GW_PORT
API_SERVER_HOST=127.0.0.1
API_SERVER_MODEL_NAME=hermes-agent

# Webhook
WEBHOOK_ENABLED=true
WEBHOOK_PORT=$((GW_PORT + 2))
WEBHOOK_SECRET=$WEBHOOK_SECRET

# STT/TTS
STT_ENABLED=true
STT_PROVIDER=local
TTS_PROVIDER=edge

# Gateway
GATEWAY_ALLOW_ALL_USERS=$GATEWAY_ALLOW_ALL_USERS

# Optional: Headroom
HEADROOM_ENABLED=$HEADROOM_ENABLED
HEADROOM_URL=http://127.0.0.1:8799
EOF

chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ Config saved to $CONFIG_FILE"
echo ""
echo "Next steps:"
echo "  1. ./scripts/render-templates.sh"
echo "  2. ./scripts/deploy.sh"