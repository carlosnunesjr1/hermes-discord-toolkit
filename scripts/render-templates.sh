#!/bin/bash
# render-templates.sh — Render templates using ~/.config/hermes-discord-toolkit/.env.local
# Output to ./rendered/

set -euo pipefail

CONFIG_FILE="${1:-$HOME/.config/hermes-discord-toolkit/.env.local}"
OUTPUT_DIR="$(dirname "$0")/../rendered"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config not found: $CONFIG_FILE"
    echo "   Run ./scripts/setup.sh first"
    exit 1
fi

# Load variables
set -a
source "$CONFIG_FILE"
set +a

mkdir -p "$OUTPUT_DIR"/{systemd,caddy,env}

echo "🔧 Rendering templates from $CONFIG_FILE..."

render() {
    local src="$1"
    local dst="$2"
    if [[ ! -f "$src" ]]; then
        echo "  ⚠️  Missing: $src"
        return
    fi
    envsubst < "$src" > "$dst"
    echo "  ✅ $dst"
}

TEMPLATE_DIR="$(dirname "$0")/../templates"

# Systemd
render "$TEMPLATE_DIR/systemd/hermes-gateway@.service"   "$OUTPUT_DIR/systemd/hermes-gateway@.service"
render "$TEMPLATE_DIR/systemd/hermes-workspace@.service" "$OUTPUT_DIR/systemd/hermes-workspace@.service"

# Caddy
render "$TEMPLATE_DIR/caddy/Caddyfile.template"         "$OUTPUT_DIR/caddy/Caddyfile"

# Env (for remote deploy)
render "$TEMPLATE_DIR/env/.env.example"                 "$OUTPUT_DIR/env/.env"

echo ""
echo "✅ Rendered to $OUTPUT_DIR/"
echo "   Deploy: ./scripts/deploy.sh"