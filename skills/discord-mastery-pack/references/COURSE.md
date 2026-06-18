# 🎓 DISCORD MASTERY COURSE
## Do Básico ao Avançado - Curso Completo com Segredos

---

## MÓDULO 1: FUNDAMENTOS (Básico)

### 1.1 Conceitos Core
- **Gateway**: Processo central que gerencia múltiplas plataformas (Discord, Telegram, Slack, etc.)
- **Adapter**: Implementação específica por plataforma (DiscordAdapter, TelegramAdapter)
- **Platform**: Nome da plataforma no Hermes (discord, telegram, slack, webhook, api_server)
- **Session**: Conversa isolada por usuário/canal/thread
- **Channel Directory**: Cache de canais acessíveis (atualizado a cada 5min)

### 1.2 Instalação Completa
```bash
# Sistema
sudo apt update && sudo apt install -y portaudio19-dev ffmpeg libopus0 espeak-ng python3-venv

# Hermes
python3 -m venv ~/.hermes-venv
source ~/.hermes-venv/bin/activate
pip install --upgrade "hermes-agent[all]"

# Verificar
hermes --version
```

### 1.3 Configuração Base
```yaml
# ~/.hermes/config.yaml - Essencial
model:
  default: nvidia/nemotron-3-ultra:free
  provider: nous

# Gateway Discord
discord:
  require_mention: true
  free_response_channels: "1516397585701666962"
  auto_thread: true
  history_backfill: true
  history_backfill_limit: 50
  voice_fx:
    enabled: true
```

### 1.4 Systemd Service (24/7)
```bash
# Instalar
hermes gateway install
# Responda 'y' para ambas as perguntas

# Verificar
systemctl --user status hermes-gateway
journalctl --user -u hermes-gateway -f
```

---

## MÓDULO 2: RECURSOS CORE (Intermediário)

### 2.1 Slash Commands Built-in
```
/help        /whoami      /new         /history
/model       /compress    /status      /skills
/cron        /voice       /undo        /save
/retry
```

### 2.2 Permissions Avançadas
```yaml
# gateway-config.yaml
platforms:
  discord:
    enabled: true
    extra:
      # Admin (você) - todos comandos
      allow_admin_from: "1294324312135831653"
      
      # Usuários regulares - apenas listados
      user_allowed_commands:
        - "help"
        - "whoami"
        - "new"
        - "model"
        - "compress"
        - "status"
        - "skills"
        - "cron"
        - "voice"
        - "undo"
        - "save"
        - "retry"
      
      # Comportamento
      require_mention: true
      group_sessions_per_user: true
      ignore_no_mention: true
```

### 2.3 Contexto de Canal
```yaml
# config.yaml ou gateway-config.yaml
discord:
  history_backfill: true
  history_backfill_limit: 50
  channel_history_size: 50  # Para multi-agent
```

---

## MÓDULO 3: VOICE CHANNEL (Avançado)

### 3.1 Setup Voice
```bash
# Dependências já instaladas no Módulo 1
# Habilitar no gateway-config.yaml:
voice_enabled: true
```

### 3.2 TTS Providers (Ordem de Qualidade)
```yaml
# config.yaml
tts:
  provider: edge          # Grátis, boa qualidade PT-BR
  edge:
    voice: pt-BR-AntonioNeural
  # elevenlabs:           # Premium, melhor qualidade
  #   voice_id: pNInz6obpgDQGcFmaJgB
  # openai:               # Bom, pagamento por uso
  #   model: gpt-4o-mini-tts
```

### 3.3 STT (Speech-to-Text)
```yaml
stt:
  enabled: true
  provider: local         # faster-whisper (grátis, offline)
  local:
    model: base           # tiny, base, small, medium, large
  # groq:                 # Cloud, mais rápido
  #   provider: groq
```

### 3.4 Voice FX (Processamento de Áudio)
```yaml
voice_fx:
  enabled: true
  ambient_enabled: true      # Som ambiente suave
  ambient_gain: 0.18
  duck_gain: 0.06            # Reduz som quando você fala
  speech_gain: 1.0
  ack_enabled: true          # Frases "um momento..." durante processamento
  ack_phrases:
    - "Let me look into that."
    - "One moment."
```

### 3.5 Check-in Matinal (Cron + Voice)
```bash
hermes cron create "0 7 * * *" \
  "Você é o assistente matinal. Faça check-in por VOICE:
  1. /voice join
  2. 'Bom dia! São 7 da manhã.'
  3. Pergunte: 'Como foi seu sono?'
  4. Pergunte: '3 prioridades de hoje?'
  5. Escute (STT automático)
  6. Resuma e salve na memory com tag 'morning-checkin'
  7. /voice leave" \
  --name "Morning Voice Check-in" \
  --deliver "discord:1516397585701666962" \
  --timezone America/Sao_Paulo
```

---

## MÓDULO 4: CRON JOBS (Produção)

### 4.1 Jobs Essenciais
```bash
# Morning Check-in (07:00)
hermes cron create "0 7 * * *" "prompt..." --name "Morning Check-in" --deliver "discord:CHANNEL_ID"

# Weekly Report (Dom 20h)
hermes cron create "0 20 * * 0" "Gere relatório semanal executivo..." --name "Weekly Report" --deliver "discord:CHANNEL_ID"

# Health Monitor (15min)
hermes cron create "*/15 * * * *" "Check CPU>80%, RAM>85%, Disco>90%. Alerte se crítico." --name "Health Monitor" --deliver "discord:CHANNEL_ID"

# Token Compression (6h)
hermes cron create "0 */6 * * *" "Execute compressão de contexto. Relate economia." --name "Token Compression" --deliver "discord:CHANNEL_ID"
```

### 4.2 Modos de Execução
```bash
# Agent mode (padrão) - usa LLM
hermes cron create "0 7 * * *" "prompt complexo" --name "Job"

# No-agent mode - script apenas, stdout = mensagem
hermes cron create "*/5 * * * *" "" --name "Health" --script "health-check.sh" --no-agent --deliver "discord:CHANNEL_ID"

# Script mode - script stdout injetado no prompt
hermes cron create "0 3 * * *" "Analise: {script_output}" --name "Backup" --script "backup.sh" --deliver "discord:CHANNEL_ID"
```

---

## MÓDULO 5: WEBHOOKS (Enterprise)

### 5.1 GitHub PR Review
```bash
hermes webhook subscribe github-pr-review \
  --prompt "Você é senior code reviewer. Analise PR:
  Repo: {repository.full_name}
  PR: #{pull_request.number} - {pull_request.title}
  Autor: {pull_request.user.login}
  Files: {pull_request.changed_files} (+{additions}/-{deletions})
  Review: 1.Resumo 2.Pontos atenção 3.Melhorias 4.Aprovado/Changes/Comment" \
  --events "pull_request" \
  --deliver "discord" \
  --deliver-chat-id "1516397585701666962" \
  --skills "github-code-review"
```

### 5.2 Cloudflare DNS (Obrigatório para Webhooks)
```
Tipo: A
Nome: webhook
IPv4: SEU_IP_VPS
Proxy: ON (laranja)
SSL: Full (Strict)
```

### 5.3 GitHub Webhook Config
```
Payload URL: https://webhook.menusummo.com.br/webhooks/github-pr-review
Content-Type: application/json
Secret: [copie do hermes webhook list]
Events: Pull requests
Active: ✓
```

---

## MÓDULO 6: MULTI-AGENT (Elite)

### 6.1 Criar 3 Profiles
```bash
hermes profile create coder
hermes profile create architect  
hermes profile create critic
```

### 6.2 SOUL.md Personas
```markdown
# profiles/coder/SOUL.md
## Persona: Senior Coder
- Foco: Implementação limpa, testável, performática
- Stack: Python, TypeScript, Rust, Go
- Princípios: SOLID, DRY, KISS, TDD
- Tom: Técnico, direto, construtivo
- Evita: Over-engineering, hype-driven dev
```

### 6.3 Canal Compartilhado
```yaml
# gateway-config.yaml
platforms:
  discord:
    extra:
      channel_history_size: 50
      allow_bots: "mentions"
      group_sessions_per_user: true
```

### 6.4 Kanban Multi-Agent
```bash
# Dispatch automático no gateway
kanban:
  dispatch_in_gateway: true
  auto_decompose: true
  orchestrator_profile: orchestrator
```

---

## MÓDULO 7: MCP (Integração Total)

### 7.1 Notion MCP
```bash
hermes mcp add notion
# Configura: NOTION_API_KEY, NOTION_DATABASE_ID
```

### 7.2 GitHub MCP
```bash
hermes mcp add github
# Configura: GITHUB_TOKEN
```

### 7.3 Linear/Obsidian
```bash
hermes mcp add linear
hermes mcp add obsidian
```

---

## MÓDULO 8: PRODUÇÃO (Senior)

### 8.1 Health Checks
```bash
# API Health
curl -H "Authorization: Bearer $API_KEY" http://localhost:8642/v1/health

# Modelos
curl -H "Authorization: Bearer $API_KEY" http://localhost:8642/v1/models

# Status Gateway
curl -H "Authorization: Bearer $API_KEY" http://localhost:8642/v1/status
```

### 8.2 Token Compression
```bash
# Manual
/compress

# Automático (cron)
hermes cron create "0 */6 * * *" "Execute compressão automática" --name "Token Compression"
```

### 8.3 Rotação de Secrets
```bash
# Discord Token (mensal)
# 1. Discord Dev Portal → Reset Token
# 2. hermes config set DISCORD_BOT_TOKEN "novo_token"
# 3. systemctl --user restart hermes-gateway
```

---

## MÓDULO 9: SEGREDOS & PRO TIPS (Mestre)

### 9.1 Features Não Documentadas
- `DISCORD_ALLOW_ALL_USERS=true` - Acesso total (cuidado!)
- `channel_history_size: 50` - Contexto cross-agent
- `ignore_no_mention: true` - Silencia menções a outros bots
- `reply_to_mode: "first"` - Resposta em thread apenas na primeira

### 9.2 Debug Avançado
```bash
# Logs detalhados
journalctl --user -u hermes-gateway -f | grep -E "(discord|webhook|cron|voice)"

# Channel directory
cat ~/.hermes/channel_directory.json

# Webhook subscriptions
cat ~/.hermes/webhook_subscriptions.json
```

### 9.3 Performance Hacks
- Use `compress` a cada 6h via cron
- `history_backfill_limit: 20` para canais muito ativos
- `max_concurrent_sessions: 10` no gateway config
- Desative `history_backfill` se não precisa de contexto histórico

### 9.4 Custom Adapter Pattern
```python
# plugins/minha_plataforma/adapter.py
from gateway.platforms.base import BasePlatformAdapter

class MinhaPlataformaAdapter(BasePlatformAdapter):
    async def connect(self): ...
    async def send(self, chat_id, content, metadata=None): ...
    async def disconnect(self): ...

# gateway-config.yaml
platforms:
  minha_plataforma:
    enabled: true
    extra: {api_key: "..."}
```

---

## 📋 CHECKLIST FINAL DE DOMÍNIO

- [ ] Gateway 24/7 systemd ativo
- [ ] Discord: DM, Menção, Slash commands
- [ ] Voice: Join/Leave, TTS, STT, FX
- [ ] 5 Crons: Morning, Weekly, Health, Compression, Custom
- [ ] Webhooks: GitHub PR Review + DNS Cloudflare
- [ ] Multi-Agent: 3 profiles + SOUL.md + Canal compartilhado
- [ ] MCP: Notion + GitHub + Linear/Obsidian
- [ ] Monitoring: Health, Logs, Alertas
- [ ] Secrets: Rotação mensal documentada
- [ ] Troubleshooting: Diagnostica qualquer falha em <5min

---

**Próximo:** Execute `./QUICKSTART.sh` para setup completo automatizado.