#!/bin/bash
# deploy.sh — Deploy to VPS using rendered templates
# Requires: render-templates.sh run first, SSH access to VPS

set -euo pipefail

CONFIG_FILE="$HOME/.config/hermes-discord-toolkit/.env.local"
RENDERED_DIR="$(dirname "$0")/../rendered"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config not found: $CONFIG_FILE"
    echo "   Run ./scripts/setup.sh first"
    exit 1
fi

if [[ ! -d "$RENDERED_DIR" ]]; then
    echo "❌ Rendered templates not found: $RENDERED_DIR"
    echo "   Run ./scripts/render-templates.sh first"
    exit 1
fi

source "$CONFIG_FILE"

# Deploy target (can be overridden)
DEPLOY_HOST="${DEPLOY_HOST:-${DOMAIN}}"
DEPLOY_USER="${DEPLOY_USER:-root}"

echo "🚀 Deploying to $DEPLOY_HOST ($DOMAIN)"
echo "   Gateway: $GW_PORT | Workspace: $WS_PORT | Dashboard: $DASH_PORT"
echo ""

# 1. Systemd units
echo "📦 Installing systemd units..."
ssh "$DEPLOY_USER@$DEPLOY_HOST" "mkdir -p /etc/systemd/system"
scp "$RENDERED_DIR/systemd/"*.service "$DEPLOY_USER@$DEPLOY_HOST:/etc/systemd/system/"

# 2. Caddy config
echo "📦 Installing Caddy config..."
scp "$RENDERED_DIR/caddy/Caddyfile" "$DEPLOY_USER@$DEPLOY_HOST:/etc/caddy/Caddyfile"

# 3. Environment
echo "📦 Installing environment..."
ssh "$DEPLOY_USER@$DEPLOY_HOST" "mkdir -p /opt/hermes"
scp "$RENDERED_DIR/env/.env" "$DEPLOY_USER@$DEPLOY_HOST:/opt/hermes/.env"

# 4. Reload & restart
echo "🔄 Reloading services..."
ssh "$DEPLOY_USER@$DEPLOY_HOST" "
    systemctl daemon-reload
    systemctl enable hermes-gateway@carlos hermes-workspace@carlos
    systemctl restart hermes-gateway@carlos
    sleep 3
    systemctl restart hermes-workspace@carlos
    systemctl reload caddy
"

# 5. Health checks
echo "🏥 Running health checks..."
sleep 5

checks=(
    "Gateway API:https://gateway.$DOMAIN/health"
    "Workspace:https://workspace.$DOMAIN"
    "Caddy:https://$DOMAIN"
)

for check in "${checks[@]}"; do
    name="${check%%:*}"
    url="${check#*:}"
    if curl -s -f --max-time 10 "$url" >/dev/null; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name ($url)"
    fi
done

echo ""
echo "✅ Deploy complete"
echo "   Gateway:  https://gateway.$DOMAIN"
echo "   Workspace: https://workspace.$DOMAIN"
echo "   Dashboard: https://dashboard.$DOMAIN (port $DASH_PORT)"