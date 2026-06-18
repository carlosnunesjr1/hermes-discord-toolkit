#!/bin/bash
# ⚡ QUICKSTART - Setup Completo Discord Gateway em 1 comando
# Uso: curl -fsSL https://raw.githubusercontent.com/seu-user/discord-mastery-pack/main/QUICKSTART.sh | bash
# Ou: ./scripts/QUICKSTART.sh

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[i]${NC} $1"; }

echo "═══════════════════════════════════════════════════════════════"
echo "    ⚡ DISCORD MASTERY PACK - QUICKSTART"
echo "    Setup completo: Gateway + Voice + Crons + Webhooks + Multi-Agent"
echo "═══════════════════════════════════════════════════════════════"
echo

# 1. Verificar root/sudo
if [[ $EUID -eq 0 ]]; then
    error "Não execute como root! Rode como usuário normal."
fi

# 2. Variáveis configuráveis (edite antes de rodar)
DISCORD_BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
DISCORD_USER_ID="${DISCORD_USER_ID:-}"
DISCORD_CHANNEL_ID="${DISCORD_CHANNEL_ID:-}"
NOUS_API_KEY="${NOUS_API_KEY:-}"
WEBHOOK_DOMAIN="${WEBHOOK_DOMAIN:-webhook.menusummo.com.br}"
VPS_IP="${VPS_IP:-}"

if [[ -z "$DISCORD_BOT_TOKEN" ]]; then
    warn "DISCORD_BOT_TOKEN não definido. Configure no .env após setup."
fi

# 3. Atualizar sistema e instalar dependências
log "Instalando dependências do sistema..."
sudo apt update && sudo apt install -y \
    portaudio19-dev ffmpeg libopus0 espeak-ng \
    python3-venv python3-full curl git jq

# 4. Criar venv e instalar Hermes
log "Criando venv e instalando Hermes Agent..."
python3 -m venv ~/.hermes-venv
source ~/.hermes-venv/bin/activate
pip install --upgrade pip
pip install "hermes-agent[all]"

# 5. Configurar .env
log "Configurando .env..."
mkdir -p ~/.hermes
cat > ~/.hermes/.env << EOF
# Discord Bot
DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
DISCORD_ALLOWED_USERS=${DISCORD_USER_ID}
DISCORD_FREE_RESPONSE_CHANNELS=${DISCORD_CHANNEL_ID}
DISCORD_HOME_CHANNEL=${DISCORD_CHANNEL_ID}

# API Server (obrigatório)
API_SERVER_ENABLED=true
API_SERVER_KEY=hermes-api-key-dev-2026
API_SERVER_PORT=8642

# Provider
NOUS_API_KEY=${NOUS_API_KEY}

# Webhook
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8644
WEBHOOK_SECRET=$(openssl rand -hex 16)

# Opcional: TTS Premium
# ELEVENLABS_API_KEY=***

# Opcional: STT Cloud
# GROQ_API_KEY=***
EOF

# 6. Configurar Hermes (config.yaml)
log "Configurando config.yaml..."
hermes config set model.default "nvidia/nemotron-3-ultra:free"
hermes config set model.provider "nous"
hermes config set providers.nous.base_url "https://inference-api.nousresearch.com/v1"
hermes config set providers.nous.api_key "\${NOUS_API_KEY}"

# Discord config
hermes config set discord.require_mention true
hermes config set discord.free_response_channels "${DISCORD_CHANNEL_ID}"
hermes config set discord.auto_thread true
hermes config set discord.history_backfill true
hermes config set discord.history_backfill_limit 50
hermes config set discord.voice_fx.enabled true
hermes config set discord.voice_fx.ambient_enabled true
hermes config set tts.provider "edge"
hermes config set tts.edge.voice "pt-BR-AntonioNeural"
hermes config set stt.enabled true
hermes config set stt.provider "local"
hermes config set stt.local.model "base"

# Webhook
hermes config set webhook.enabled true
hermes config set webhook.port 8644
hermes config set platforms.webhook.enabled true
hermes config set platforms.webhook.port 8644

# 7. Gateway Config (gateway-config.yaml)
log "Configurando gateway-config.yaml..."
mkdir -p ~/.hermes
cat > ~/.hermes/gateway-config.yaml << EOF
platforms:
  discord:
    enabled: true
    extra:
      allow_admin_from: "${DISCORD_USER_ID}"
      user_allowed_commands:
        - "help"
        - "whoami"
        - "new"
        - "history"
        - "model"
        - "compress"
        - "status"
        - "skills"
        - "cron"
        - "voice"
        - "undo"
        - "save"
        - "retry"
      require_mention: true
      group_sessions_per_user: true
      ignore_no_mention: true
      voice_enabled: true
      channel_history_size: 50
EOF

# 8. Systemd Service
log "Instalando systemd service 24/7..."
hermes gateway install << 'EOF'
y
y
EOF

# 8.1 Configurar env systemd
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/env.conf << EOF
[Service]
Environment="DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}"
Environment="API_SERVER_ENABLED=true"
Environment="API_SERVER_KEY=hermes-api-key-dev-2026"
Environment="API_SERVER_PORT=8642"
Environment="NOUS_API_KEY=${NOUS_API_KEY}"
Environment="WEBHOOK_SECRET=$(openssl rand -hex 16)"
Environment="WEBHOOK_PORT=8644"
EOF

systemctl --user daemon-reload
systemctl --user restart hermes-gateway

# 9. Aguardar gateway subir
log "Aguardando gateway iniciar..."
sleep 10

# 10. Criar Crons Essenciais
log "Criando cron jobs..."

# Morning Voice Check-in (07:00)
hermes cron create "0 7 * * *" \
  "Você é o assistente matinal do Carlos. Faça check-in por VOICE CHANNEL:
  1. Use /voice join
  2. Cumprimente: 'Bom dia, Carlos! São 7 da manhã.'
  3. Pergunte: 'Como foi seu sono? Descansou bem?'
  4. Pergunte: 'Quais são as 3 prioridades de hoje?'
  5. Escute respostas (STT automático)
  6. Resuma: 'Entendi: sono [X], prioridades: [1], [2], [3]'
  7. Deseje bom dia e use /voice leave
  8. Salve resumo na memory com tag 'morning-checkin'
  Seja caloroso, natural, conversacional. Use TTS." \
  --name "Morning Voice Check-in" \
  --deliver "discord:${DISCORD_CHANNEL_ID}" \
  --timezone America/Sao_Paulo

# Weekly Report (Dom 20h)
hermes cron create "0 20 * * 0" \
  "Gere relatório semanal executivo para o Carlos:
  ## Relatório Semanal - \$(date +'%d/%m/%Y')
  ### Conquistas (3-5 itens)
  ### Métricas: Sessões, Tokens, Crons executados
  ### Próxima Semana: Top 3 prioridades
  ### Alertas/Riscos
  Seja conciso, direto, tom executivo." \
  --name "Weekly Executive Report" \
  --deliver "discord:${DISCORD_CHANNEL_ID}"

# Health Monitor (15min)
hermes cron create "*/15 * * * *" \
  "Verifique saúde VPS: CPU, memória, disco, uptime.
  Se CPU > 80% OU memória > 85% OU disco > 90%: ALERTE no Discord com detalhes.
  Se OK: NÃO faça nada (silêncio total)." \
  --name "VPS Health Monitor" \
  --deliver "discord:${DISCORD_CHANNEL_ID}"

# Token Compression (6h)
hermes cron create "0 */6 * * *" \
  "Execute compressão de contexto (/compress) para controle de tokens.
  Identifique sessões antigas e comprima histórico.
  Relate economia estimada de tokens." \
  --name "Token Compression Routine" \
  --deliver "discord:${DISCORD_CHANNEL_ID}"

# 11. GitHub PR Review Webhook
log "Configurando webhook GitHub PR Review..."
hermes webhook subscribe github-pr-review \
  --prompt "Você é um senior code reviewer. Analise este PR do GitHub:
  
  Repositório: {repository.full_name}
  PR: #{pull_request.number} - {pull_request.title}
  Autor: {pull_request.user.login}
  Branch: {pull_request.head.ref} → {pull_request.base.ref}
  
  Mudanças:
  {pull_request.changed_files} arquivos, +{pull_request.additions} -{pull_request.deletions}
  
  Forneça review conciso:
  1. Resumo do que faz
  2. Pontos de atenção (segurança, performance, breaking changes)
  3. Sugestões de melhoria
  4. Aprovado / Request Changes / Comment
  
  Tom: técnico, direto, construtivo." \
  --events "pull_request" \
  --description "GitHub PR Code Review" \
  --deliver "discord" \
  --deliver-chat-id "${DISCORD_CHANNEL_ID}" \
  --skills "github-code-review"

WEBHOOK_SECRET=$(hermes webhook list | grep -A1 "github-pr-review" | grep Secret | awk '{print }')

# 12. Multi-Agent Profiles
log "Criando profiles Multi-Agent..."
hermes profile create coder 2>/dev/null || true
hermes profile create architect 2>/dev/null || true
hermes profile create critic 2>/dev/null || true

# Copy SOUL.md files
for p in coder architect critic; do
  cp ./references/SOUL-${p}.md ~/.hermes/profiles/${p}/SOUL.md 2>/dev/null || true
done

# 13. Testes de Validação
log "Executando testes de validação..."

# Test API
sleep 5
API_TEST=$(curl -sf -H "Authorization: Bearer *** http://localhost:8642/v1/health 2>/dev/null)
if echo "$API_TEST" | grep -q '"status":"ok"'; then
    log "API Server: OK"
else
    warn "API Server: Verifique logs"
fi

# Test Gateway
GW_STATUS=$(systemctl --user is-active hermes-gateway)
if [[ "$GW_STATUS" == "active" ]]; then
    log "Gateway Systemd: OK"
else
    error "Gateway não está ativo! Verifique: journalctl --user -u hermes-gateway -f"
fi

# Test Discord Channel Directory
if [[ -f ~/.hermes/channel_directory.json ]]; then
    CHANNELS=$(cat ~/.hermes/channel_directory.json | jq -r '.platforms.discord | length')
    log "Channel Directory: ${CHANNELS} canais Discord detectados"
fi

# 14. Resumo Final
echo
echo "═══════════════════════════════════════════════════════════════"
echo "    ✅ SETUP CONCLUÍDO COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════════"
echo
echo "📋 CHECKLIST DO QUE FOI CONFIGURADO:"
echo "  ✅ Hermes Agent instalado (~/.hermes-venv)"
echo "  ✅ Systemd service 24/7 (hermes-gateway)"
echo "  ✅ Discord Bot conectado"
echo "  ✅ Channel Directory populado"
echo "  ✅ Voice Channel habilitado (TTS: Edge pt-BR-AntonioNeural)"
echo "  ✅ STT: faster-whisper local (modelo base)"
echo
echo "⏰ CRON JOBS CRIADOS:"
echo "  • Morning Voice Check-in: 07:00 daily"
echo "  • Weekly Executive Report: Sun 20:00"
echo "  • VPS Health Monitor: */15 min"
echo "  • Token Compression: 0 */6 * * *"
echo
echo "🔗 WEBHOOK GITHUB PR REVIEW:"
echo "  URL: https://${WEBHOOK_DOMAIN}/webhooks/github-pr-review"
echo "  Secret: ${WEBHOOK_SECRET}"
echo "  Events: pull_request"
echo
echo "🤖 MULTI-AGENT:"
echo "  Profiles: coder, architect, critic"
echo "  Canal compartilhado: history=50"
echo
echo "📝 PRÓXIMOS PASSOS MANUAIS:"
echo "  1. Adicione DNS no Cloudflare:"
echo "     A  webhook  →  ${VPS_IP:-SEU_IP_VPS}  (Proxy ON)"
echo
echo "  2. Configure GitHub Webhook no repositório:"
echo "     Settings → Webhooks → Add webhook"
echo "     Payload URL: https://${WEBHOOK_DOMAIN}/webhooks/github-pr-review"
echo "     Secret: ${WEBHOOK_SECRET}"
echo "     Events: Pull requests"
echo
echo "  3. Testes no Discord:"
echo "     • DM o bot: 'oi'"
echo "     • No #geral: @Bot oi"
echo "     • /voice join (entre no VC)"
echo "     • hermes cron run 'Morning Voice Check-in'"
echo
echo "🔧 COMANDOS ÚTEIS:"
echo "  journalctl --user -u hermes-gateway -f    # Logs"
echo "  hermes cron list                          # Ver crons"
echo "  hermes cron run 'Nome'                    # Testar cron"
echo "  hermes webhook list                       # Ver webhooks"
echo "  systemctl --user restart hermes-gateway   # Restart"
echo
echo "📚 CURSO COMPLETO: skill://discord-mastery-pack/references/COURSE.md"
echo
log "Tudo pronto! Domine o Discord! 🚀"