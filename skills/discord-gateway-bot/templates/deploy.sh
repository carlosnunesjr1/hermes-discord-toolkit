#!/usr/bin/env bash
# Hermes Discord Bot - Deploy/Management Script
# Template for skill: discord-gateway-bot

set -euo pipefail

# =============================================================================
# CONFIGURATION - MODIFY THESE FOR YOUR DEPLOYMENT
# =============================================================================
BOT_DIR="${BOT_DIR:-/home/carlos/hermes-discord-bot}"
SERVICE_NAME="${SERVICE_NAME:-hermes-discord-bot}"
VENV_DIR="${BOT_DIR}/venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

# Discord tokens (set in .env, not here)
# DISCORD_BOT_TOKEN=
# DISCORD_APP_ID=
# DISCORD_GUILD_ID=

# =============================================================================
# HELPERS
# =============================================================================
log() { echo -e "\033[1;32m[$(date '+%H:%M:%S')]\033[0m $*"; }
warn() { echo -e "\033[1;33m[$(date '+%H:%M:%S')] WARN:\033[0m $*" >&2; }
error() { echo -e "\033[1;31m[$(date '+%H:%M:%S')] ERROR:\033[0m $*" >&2; }

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

install() {
    log "Installing Hermes Discord Bot..."
    
    cd "${BOT_DIR}"
    
    # Virtual environment
    if [[ ! -d "${VENV_DIR}" ]]; then
        python3 -m venv "${VENV_DIR}"
        log "Virtual environment created"
    fi
    
    # Dependencies
    "${PIP}" install --upgrade pip -q
    "${PIP}" install -r requirements.txt -q
    log "Dependencies installed"
    
    # Environment file
    if [[ ! -f ".env" ]]; then
        cp .env.template .env
        warn "Created .env from template — EDIT IT WITH YOUR TOKENS!"
        warn "  nano .env"
        return 1
    fi
    
    # Systemd service
    sudo cp "service/${SERVICE_NAME}.service" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}"
    log "Systemd service installed and enabled"
    
    log "Installation complete!"
    log "Next: edit .env with tokens, then run: $0 start"
}

update() {
    log "Updating Hermes Discord Bot..."
    
    cd "${BOT_DIR}"
    
    # Git pull if repo
    if [[ -d ".git" ]]; then
        git pull
        log "Code updated"
    fi
    
    # Dependencies
    "${PIP}" install -r requirements.txt -q
    log "Dependencies updated"
    
    # Restart service
    sudo systemctl restart "${SERVICE_NAME}"
    log "Service restarted"
}

start() {
    log "Starting ${SERVICE_NAME}..."
    sudo systemctl start "${SERVICE_NAME}"
    sleep 2
    status
}

stop() {
    log "Stopping ${SERVICE_NAME}..."
    sudo systemctl stop "${SERVICE_NAME}"
}

restart() {
    log "Restarting ${SERVICE_NAME}..."
    sudo systemctl restart "${SERVICE_NAME}"
    sleep 2
    status
}

status() {
    log "Service status:"
    sudo systemctl status "${SERVICE_NAME}" --no-pager -l
}

logs() {
    log "Following logs (Ctrl+C to exit):"
    sudo journalctl -u "${SERVICE_NAME}" -f --no-pager
}

tail_logs() {
    local lines="${1:-100}"
    sudo journalctl -u "${SERVICE_NAME}" -n "${lines}" --no-pager
}

test_gateway() {
    log "Testing Hermes Gateway connection..."
    "${PYTHON}" -c "
import asyncio, aiohttp, sys
async def test():
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get('http://localhost:8642/health', timeout=aiohttp.ClientTimeout(total=5)) as r:
                data = await r.json()
                print(f'Gateway health: {r.status} - {data}')
                sys.exit(0 if r.status == 200 else 1)
        except Exception as e:
            print(f'Gateway connection failed: {e}')
            sys.exit(1)
asyncio.run(test())
"
}

setup_discord() {
    cat << 'EOF'

=========================================
DISCORD DEVELOPER PORTAL SETUP
=========================================

1. Go to: https://discord.com/developers/applications
2. Create New Application → Name: "Hermes Agent"
3. Bot tab → Reset Token → COPY TOKEN → .env as DISCORD_BOT_TOKEN
4. Bot tab → Privileged Gateway Intents → ENABLE:
   ✅ Message Content Intent
   ✅ Server Messages Intent
   ✅ Guild Members Intent (optional)
5. OAuth2 → URL Generator → Scopes: ✅ bot ✅ applications.commands
   Bot Permissions:
   ✅ Manage Channels
   ✅ Manage Threads
   ✅ Send Messages
   ✅ Send Messages in Threads
   ✅ Embed Links
   ✅ Read Message History
   ✅ Use Slash Commands
   ✅ Add Reactions
   ✅ Manage Messages (optional)
6. Copy generated URL → open in browser → invite bot to your server
7. General Information → Application ID → .env as DISCORD_APP_ID
8. In Discord (Dev Mode on): Right-click server → Copy ID → .env as DISCORD_GUILD_ID

Then run: ./deploy.sh start

EOF
}

# =============================================================================
# MAIN
# =============================================================================
case "${1:-}" in
    install)    install ;;
    update)     update ;;
    start)      start ;;
    stop)       stop ;;
    restart)    restart ;;
    status)     status ;;
    logs)       logs ;;
    tail)       tail_logs "${2:-}" ;;
    test-gateway) test_gateway ;;
    setup-discord) setup_discord ;;
    *)
        cat << EOF
Hermes Discord Bot - Deploy Script

Usage: $0 {install|update|start|stop|restart|status|logs|tail|test-gateway|setup-discord}

Commands:
  install         - Initial setup (venv, deps, systemd)
  update          - Pull code, update deps, restart
  start           - Start the bot service
  stop            - Stop the bot service
  restart         - Restart the bot service
  status          - Show service status
  logs            - Follow live logs (journalctl -f)
  tail [N]        - Show last N lines (default: 100)
  test-gateway    - Test connection to Hermes Gateway (:8642)
  setup-discord   - Show Discord Developer Portal setup guide

EOF
        exit 1
        ;;
esac