#!/usr/bin/env bash
set -euo pipefail

# Hermes Discord Bot - Deploy Script
# Usage: ./deploy.sh [install|update|start|stop|restart|status|logs|tail|test-gateway|setup-discord]

BOT_DIR="/home/carlos/hermes-discord-bot"
SERVICE_NAME="hermes-discord-bot"
VENV_DIR="$BOT_DIR/venv"

cd "$BOT_DIR"

function install() {
    echo "📦 Installing Hermes Discord Bot..."
    
    # Create venv
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
        echo "✅ Virtual environment created"
    fi
    
    # Install dependencies
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r requirements.txt
    echo "✅ Dependencies installed"
    
    # Check .env
    if [[ ! -f ".env" ]]; then
        cp .env.template .env
        echo "⚠️  Created .env from template - EDIT IT WITH YOUR TOKENS!"
        echo "   nano .env"
        return 1
    fi
    
    # Install systemd service
    sudo cp service/hermes-discord-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    echo "✅ Systemd service installed and enabled"
    
    echo ""
    echo "🎉 Installation complete!"
    echo "   Edit .env with your tokens, then run: ./deploy.sh start"
}

function update() {
    echo "🔄 Updating Hermes Discord Bot..."
    
    if [[ -d ".git" ]]; then
        git pull
        echo "✅ Code updated"
    fi
    
    "$VENV_DIR/bin/pip" install -r requirements.txt
    echo "✅ Dependencies updated"
    
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Service restarted"
}

function start() {
    echo "▶️ Starting $SERVICE_NAME..."
    sudo systemctl start "$SERVICE_NAME"
    sleep 2
    status
}

function stop() {
    echo "⏹️ Stopping $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME"
}

function restart() {
    echo "🔁 Restarting $SERVICE_NAME..."
    sudo systemctl restart "$SERVICE_NAME"
    sleep 2
    status
}

function status() {
    echo "📊 Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

function logs() {
    echo "📋 Recent logs (Ctrl+C to exit):"
    sudo journalctl -u "$SERVICE_NAME" -f --no-pager
}

function tail_logs() {
    lines="${1:-100}"
    sudo journalctl -u "$SERVICE_NAME" -n "$lines" --no-pager
}

function test_gateway() {
    echo "🔍 Testing Hermes Gateway connection..."
    "$VENV_DIR/bin/python" -c "
import asyncio, aiohttp
async def test():
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get('http://localhost:8642/health', timeout=aiohttp.ClientTimeout(total=5)) as r:
                print(f'Gateway health: {r.status} - {await r.json()}')
        except Exception as e:
            print(f'Gateway connection failed: {e}')
asyncio.run(test())
"
}

function setup_discord() {
    echo ""
    echo "📋 DISCORD DEVELOPER PORTAL SETUP"
    echo "=================================="
    echo ""
    echo "1. Go to: https://discord.com/developers/applications"
    echo "2. Create New Application → Name: 'Hermes Agent'"
    echo "3. Bot tab → Reset Token → COPY TOKEN → paste in .env as DISCORD_BOT_TOKEN"
    echo "4. Bot tab → Privileged Gateway Intents → ENABLE:"
    echo "   ✅ Message Content Intent"
    echo "   ✅ Server Messages Intent"
    echo "   ✅ Guild Members Intent (optional)"
    echo "5. OAuth2 → URL Generator → Scopes: ✅ bot ✅ applications.commands"
    echo "   Bot Permissions:"
    echo "   ✅ Manage Channels"
    echo "   ✅ Manage Threads"
    echo "   ✅ Send Messages"
    echo "   ✅ Send Messages in Threads"
    echo "   ✅ Embed Links"
    echo "   ✅ Read Message History"
    echo "   ✅ Use Slash Commands"
    echo "   ✅ Add Reactions"
    echo "   ✅ Manage Messages (optional)"
    echo "6. Copy generated URL → open in browser → invite bot to your server"
    echo "7. General Information → Application ID → paste in .env as DISCORD_APP_ID"
    echo "8. In Discord (Dev Mode on): Right-click server → Copy ID → paste in .env as DISCORD_GUILD_ID"
    echo ""
    echo "Then run: ./deploy.sh start"
}

case "${1:-}" in
    install)
        install
        ;;
    update)
        update
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    tail)
        tail_logs "${2:-}"
        ;;
    test-gateway)
        test_gateway
        ;;
    setup-discord)
        setup_discord
        ;;
    *)
        echo "Hermes Discord Bot - Deploy Script"
        echo ""
        echo "Usage: $0 {install|update|start|stop|restart|status|logs|tail|test-gateway|setup-discord}"
        echo ""
        echo "Commands:"
        echo "  install        - Initial setup (venv, deps, systemd)"
        echo "  update         - Pull code, update deps, restart"
        echo "  start          - Start the bot service"
        echo "  stop           - Stop the bot service"
        echo "  restart        - Restart the bot service"
        echo "  status         - Show service status"
        echo "  logs           - Follow live logs (journalctl -f)"
        echo "  tail [N]       - Show last N lines (default: 100)"
        echo "  test-gateway   - Test connection to Hermes Gateway"
        echo "  setup-discord  - Show Discord Developer Portal setup guide"
        exit 1
        ;;
esac