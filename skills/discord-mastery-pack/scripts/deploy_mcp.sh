#!/bin/bash
# scripts/deploy_mcp.sh - Deploy MCP Integrations
# Uso: ./deploy_mcp.sh [all|notion|github|linear|obsidian]

set -euo pipefail

log() { echo -e "\033[0;32m[✓]\033[0m $1"; }
warn() { echo -e "\033[1;33m[!]\033[0m $1"; }
error() { echo -e "\033[0;31m[✗]\033[0m $1"; exit 1; }

TARGET=${1:-all}

# Verificar Hermes
if ! command -v hermes &> /dev/null; then
    error "Hermes não encontrado. Rode QUICKSTART.sh primeiro."
fi

deploy_notion() {
    log "Deploying Notion MCP..."
    hermes mcp add notion << 'EOF'
# Notion API Key (Integration Token)
# Crie em: https://www.notion.so/my-integrations
NOTION_API_KEY=ntn_***

# Database IDs (opcional - para sync automático)
NOTION_TASKS_DB_ID=***
NOTION_NOTES_DB_ID=***
NOTION_PROJECTS_DB_ID=***
EOF
    log "Notion MCP configurado. Reinicie gateway: systemctl --user restart hermes-gateway"
}

deploy_github() {
    log "Deploying GitHub MCP..."
    hermes mcp add github << 'EOF'
# GitHub Personal Access Token (classic)
# Scopes: repo, admin:repo_hook, read:org, user
GITHUB_TOKEN=ghp_***

# Organization (opcional)
GITHUB_ORG=***
EOF
    log "GitHub MCP configurado."
}

deploy_linear() {
    log "Deploying Linear MCP..."
    hermes mcp add linear << 'EOF'
# Linear API Key
# Settings → API → Personal API keys
LINEAR_API_KEY=lin_api_***

# Team ID (opcional)
LINEAR_TEAM_ID=***
EOF
    log "Linear MCP configurado."
}

deploy_obsidian() {
    log "Deploying Obsidian MCP..."
    hermes mcp add obsidian << 'EOF'
# Obsidian Local REST API
# Instale plugin "Local REST API" no Obsidian
# Config: Port 27123, API Key
OBSIDIAN_API_KEY=***
OBSIDIAN_HOST=localhost
OBSIDIAN_PORT=27123

# Vault path (para file operations)
OBSIDIAN_VAULT_PATH=~/ObsidianVault
EOF
    log "Obsidian MCP configurado. Instale plugin 'Local REST API' no Obsidian."
}

case $TARGET in
    all)
        deploy_notion
        deploy_github
        deploy_linear
        deploy_obsidian
        ;;
    notion) deploy_notion ;;
    github) deploy_github ;;
    linear) deploy_linear ;;
    obsidian) deploy_obsidian ;;
    *) error "Uso: $0 [all|notion|github|linear|obsidian]" ;;
esac

log "Deploy concluído! Verifique: hermes mcp list"
log "Reinicie gateway: systemctl --user restart hermes-gateway"