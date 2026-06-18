# 📋 DAILY WORKFLOW & USAGE GUIDE
## Como Usar Discord + Hermes no Dia a Dia - Desbloqueando Todo Potencial

> **Este documento é sua "bíblia" de uso diário.** Leia, internalize, use como referencia. O poder está na consistência.

---

## 🎯 MODELO MENTAL: Discord não é "chat", é **INTERFACE DE COMANDO PARA SUA VIDA**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUA INTERFACE HERMES                         │
├─────────────────────────────────────────────────────────────────┤
│  💬 DM Direto        → Contexto privado, deep work, segredos   │
│  📍 #geral (menção)  → Contexto compartilhado, comandos rápidos│
│  🎤 Voice Channel    → Check-ins, brainstorms, hands-free      │
│  ⚡ Slash Commands   → Ações instantâneas, zero fricção         │
│  🤖 Multi-Agent      → Perspectivas especializadas sob demanda │
│  🔗 Webhooks         → Eventos externos → Ação automática      │
│  ⏰ Crons            → Rotinas automáticas, disciplina forçada  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌅 ROTINA MATINAL (07:00 - Automático + Manual)

### O que acontece AUTOMATICAMENTE (Cron):
```
07:00 → Bot entra no seu Voice Channel
      → "Bom dia, Carlos! São 7 da manhã."
      → Pergunta: "Como foi seu sono? Descansou bem?"
      → Pergunta: "Quais são as 3 prioridades de hoje?"
      → ESCUTA via STT (faster-whisper local)
      → Resume: "Entendi: sono [X], prioridades: [1], [2], [3]"
      → Deseja bom dia produtivo
      → Sai do VC
      → Salva na memory com tag 'morning-checkin'
```

### O que VOCÊ faz MANUALMENTE (após acordar):
```bash
# 1. Confere se check-in rodou (notificação no Discord)
# 2. Ajusta prioridades se mudou algo
# 3. Inicia sessão de trabalho
```

**Comando manual se quiser repetir:**
```
/cron run "Morning Voice Check-in"
# ou mencione: @Hermes refaz check-in matinal
```

---

## 💼 DURANTE O DIA - WORKFLOWS PRINCIPAIS

### 1. DEEP WORK (DM Privado)
```
VOCÊ (DM): "Preciso arquitetar o novo sistema de pagamentos"
HERMES: Inicia sessão isolada, contexto limpo, foco total
        Usa profile 'architect' se complexo
        Salva decisões na memory automaticamente
```

### 2. QUICK TASKS (Menção em #geral)
```
VOCÊ: @Hermes comprime contexto da sessão anterior
VOCÊ: @Hermes qual modelo estou usando?
VOCÊ: @Hermes nova sessão para revisar PR #42
VOCÊ: @Hermes status do gateway
```

### 3. CODE REVIEW (Webhook Automático)
```
GitHub PR aberto → Webhook dispara → Hermes analisa com skill github-code-review
                                           → Entrega review estruturado em #geral
                                           → Você lê, aprova/request changes
                                           → Zero context switching
```

### 4. VOICE BRAINSTORM (Quando travar)
```
/voice join (entre no VC)
Fale naturalmente: "Travado no design da API. Me ajuda a pensar"
Hermes responde via TTS, faz perguntas socráticas
/voice leave quando clarear
```

### 5. MULTI-AGENT PERSPECTIVES (Decisões importantes)
```
VOCÊ (DM): "/profile architect" → "Vale a pena migrar para Rust?"
VOCÊ (DM): "/profile critic"   → "Quais riscos não estou vendo?"
VOCÊ (DM): "/profile coder"    → "Como implementar isso limpo?"
# Cada profile tem SOUL.md próprio, sessão isolada
```

---

## 📅 ROTINA SEMANAL (Domingo 20:00 - Automático)

### Weekly Executive Report (Cron):
```
## 📊 Relatório Semanal - DD/MM/YYYY
### ✅ Conquistas (3-5 itens extraídos das sessões)
### 📈 Métricas: Sessões, Tokens, Crons executados
### 🎯 Próxima Semana: Top 3 prioridades
### ⚠️ Alertas/Riscos
Entregue em #geral domingo 20h
```

### Sua Ação (Segunda de manhã):
```bash
# 1. Lê relatório no Discord
# 2. Ajusta prioridades da semana
# 3. Confere alertas
# 4. Inicia sprint
```

---

## ⚡ COMANDOS ESSENCIAIS (Memorize Estes)

### Slash Commands (digite `/` no Discord):
```
/new [nome]        → Nova sessão limpa
/history           → Ver histórico da sessão atual
/model             → Ver/trocar modelo (Nemotron, GPT-4, etc)
/compress          → Comprimir contexto (economiza tokens)
/status            → Status do gateway, sessões, memory
/skills            → Listar skills disponíveis
/cron              → Gerenciar crons (list, run, remove)
/voice join/leave  → Voice channel
/voice mode        → TTS on/off, STT config
/undo              → Desfazer última ação do agente
/save              → Salvar sessão atual nomeada
/retry             → Retentar última falha
/help              → Ajuda contextual
```

### Comandos Hermes CLI (Terminal/VPS):
```bash
# Gateway
journalctl --user -u hermes-gateway -f    # Logs ao vivo
systemctl --user restart hermes-gateway   # Restart
systemctl --user status hermes-gateway    # Status

# Crons
hermes cron list                          # Ver todos
hermes cron run "Nome"                    # Testar manual
hermes cron create "0 7 * * *" "prompt" --name "Job" --deliver "discord:CHANNEL_ID"

# Webhooks
hermes webhook list
hermes webhook test github-pr-review

# Sessões
hermes sessions list
hermes sessions prune                     # Limpar antigas

# Profiles
hermes chat --profile coder
hermes chat --profile architect
hermes chat --profile critic
```

---

## 🎤 VOICE CHANNEL - USO AVANÇADO

### Configuração Atual:
- **TTS**: Edge (pt-BR-AntonioNeural) - grátis, qualidade boa
- **STT**: faster-whisper base (local, offline, ~2-3x realtime)
- **FX**: Ambient sounds, duck gain (baixa música quando você fala)

### Fluxos de Voice:

#### A. Check-in Matinal (Automático 07:00)
```
/voice join → Fala → STT → Processa → TTS responde → /voice leave
```

#### B. Brainstorm Sob Demanda
```
Você entra no VC
/voice join
Fala: "Travado no X. Me ajuda a estruturar."
Hermes: Faz perguntas, sugere frameworks, resume no final
/voice leave
```

#### C. Pair Programming por Voz
```
Você: "Vamos implementar a função X"
Hermes: "OK. Primeira assinatura: def process_payment(..."
Você: "Não, quero async com retry"
Hermes: "Entendido. Async com exponential backoff..."
# Código aparece no chat/artifact simultaneamente
```

#### D. Configurações Voice:
```
/voice mode tts on/off
/voice mode stt on/off
/voice status
```

---

## 🤖 MULTI-AGENT - QUANDO USAR CADA PROFILE

| Profile | Quando Usar | SOUL.md Focus |
|---------|-------------|---------------|
| **coder** | Implementar, debuggar, refatorar, testar | Clean code, TDD, performance, pragmatismo |
| **architect** | Decisões técnicas, design sistemas, trade-offs | Scalability, DDD, evolutionary arch, fitness functions |
| **critic** | Code review, security audit, encontrar bugs | Assume breach, security first, maintainability |

### Workflow Multi-Agent (Exemplo Real):
```bash
# 1. Você tem decisão arquitetural complexa
DM → @Hermes (architect): "Microserviços vs Modulith para novo módulo?"

# 2. Ele analisa, devolve trade-offs, recomenda
# 3. Você quer validar riscos
DM → @Hermes (critic): "Quais riscos dessa abordagem modulith?"

# 4. Ele aponta: deployment coupling, testing complexity, etc
# 5. Você decide implementar
DM → @Hermes (coder): "Implemente o core do modulith com boundaries claros"

# 6. Ele entrega código limpo, testado, documentado
# 7. Critic revisa o PR via webhook automaticamente
```

### Canal Compartilhado (#geral com history=50):
- Todos profiles veem últimas 50 mensagens
- Menção `@Hermes` roteia para profile ativo ou pergunta qual usar
- Contexto compartilhado = zero perda de informação

---

## 🔗 WEBHOOKS - EVENTOS EXTERNOS VIRAM AÇÃO

### GitHub PR Review (Já Configurado):
```
PR aberto/sincronizado → POST webhook.menusummo.com.br/webhooks/github-pr-review
                       → HMAC validation
                       → Agent com skill github-code-review
                       → Review estruturado em #geral
                       → Você age: Approve / Request Changes / Comment
```

### Próximos Webhooks para Adicionar:
```bash
# GitHub Issues
hermes webhook subscribe github-issues \
  --events "issues,issue_comment" \
  --prompt "Novo issue: {action} #{number} - {title}. Resuma e sugira labels/assignees."

# Vercel Deploy
hermes webhook subscribe vercel-deploy \
  --events "deployment.created,deployment.ready" \
  --prompt "Deploy {state}: {url}. Notifique se falhou."

# Linear (Project Management)
hermes webhook subscribe linear-issues \
  --events "IssueCreated,IssueUpdated" \
  --prompt "Linear: {action} {identifier} - {title}. Atualize contexto."

# Supabase (Database)
hermes webhook subscribe supabase-alerts \
  --events "database.webhook" \
  --prompt "Alerta DB: {type} - {message}. Sugira investigação."
```

---

## 🛡️ ADMIN & MANUTENÇÃO (Sua Rotina de "Sysadmin")

### Diário (30 seg):
```bash
# 1. Check gateway health
curl -H "Authorization: Bearer *** localhost:8642/v1/health

# 2. Check Discord bot online (DM "oi")

# 3. Check crons rodando
hermes cron list | grep -E "Morning|Health|Compression"
```

### Semanal (5 min):
```bash
# 1. Token compression manual se necessário
/compress

# 2. Limpar sessões antigas
hermes sessions prune

# 3. Ver logs erros
journalctl --user -u hermes-gateway --since "1 week ago" | grep -i error

# 4. Backup config
cp ~/.hermes/config.yaml ~/backups/config-$(date +%Y%m%d).yaml
cp ~/.hermes/.env ~/backups/env-$(date +%Y%m%d).bak
```

### Mensal (15 min):
```bash
# 1. ROTAÇÃO DE TOKENS (CRÍTICO)
# Discord: Dev Portal → Reset Token
hermes config set DISCORD_BOT_TOKEN "NOVO_TOKEN"
# Webhook: hermes webhook subscribe --secret NOVO_SECRET
# API: Editar API_SERVER_KEY no .env + systemd env

# 2. Restart gateway
systemctl --user restart hermes-gateway

# 3. Atualizar Hermes
pip install --upgrade "hermes-agent[all]"
systemctl --user restart hermes-gateway

# 4. Verificar dependências voice
dpkg -l | grep -E "ffmpeg|libopus|portaudio"
/usr/local/lib/hermes-venv/bin/python -c "import edge_tts, faster_whisper"
```

---

## 🔐 SEGREDOS & CONFIGURAÇÕES (Onde Tudo Mora)

| Arquivo | O que tem | Como editar |
|---------|-----------|-------------|
| `~/.hermes/.env` | **Todos secrets** (tokens, keys) | `hermes config set KEY "VALUE"` |
| `~/.hermes/config.yaml` | Core config (model, tts, stt, memory) | `hermes config set path.to.key value` |
| `~/.hermes/gateway-config.yaml` | Comportamento Discord (perms, voice, history) | Editar direto + `systemctl --user restart hermes-gateway` |
| `~/.config/systemd/user/hermes-gateway.service.d/env.conf` | Env vars systemd | Editar direto + `systemctl --user daemon-reload` |
| `~/.hermes/profiles/*/SOUL.md` | Personas dos agents | Editar direto |

### Secrets Atuais (Referência):
```bash
DISCORD_BOT_TOKEN=MTUxNj...xHoQ          # Discord Bot
DISCORD_ALLOWED_USERS=1294324312135831653 # Seu User ID (admin)
DISCORD_FREE_RESPONSE_CHANNELS=1516397585701666962 # #geral
API_SERVER_KEY=hermes-api-key-dev-2026    # API auth
WEBHOOK_SECRET=xiVxJ9Mys5HMvfOKGYwTW...   # GitHub webhook HMAC
NOUS_API_KEY=***                          # LLM provider
```

---

## 🚀 DESBLOQUEANDO POTENCIAL MÁXIMO - CHECKLIST

### Nível 1: Básico (Já Feito)
- [x] Gateway 24/7
- [x] DM + Menção + Slash commands
- [x] Voice channel básico
- [x] 4 Crons essenciais
- [x] GitHub PR Review webhook

### Nível 2: Intermediário (Próximos)
- [ ] Testar Voice check-in matinal real
- [ ] Usar `/compress` rotineiramente
- [ ] Multi-agent para decisão real
- [ ] Configurar MCP Notion (sync tasks)
- [ ] Configurar MCP GitHub (issues no Discord)

### Nível 3: Avançado
- [ ] Custom skills para seu domínio
- [ ] Webhooks: Vercel, Linear, Supabase
- [ ] Kanban multi-agent com artifacts
- [ ] Observability: Grafana + Loki + Tempo
- [ ] Custom adapter para ferramenta interna

### Nível 4: Mestre
- [ ] Plugin Hermes próprio
- [ ] Multi-gateway cluster (HA)
- [ ] Enterprise SSO (OIDC)
- [ ] Visual workflow builder
- [ ] Ensinar outros (multiplicar)

---

## 🎯 SUA ROTINA IDEAL (Resumo Executivo)

| Horário | Ação | Tool |
|---------|------|------|
| **07:00** | Check-in matinal (auto) | Cron + Voice |
| **07:30** | Deep work session 1 | DM + coder/architect |
| **10:00** | Quick sync / PR reviews | #geral + Webhook |
| **12:00** | Almoço / Break | - |
| **13:30** | Deep work session 2 | DM + profile adequado |
| **16:00** | Admin / Emails / Shallow | Menções rápidas |
| **17:30** | Wrap up / Próximos passos | `/save` + memory |
| **20:00** (Dom) | Weekly review (auto) | Cron + Report |

---

## 💡 DICAS DE OURO (Hard-Earned)

1. **DM para contexto profundo, #geral para ações rápidas**
2. **Voice para clareza mental, texto para precisão**
3. **Multi-agent = perspectivas, não substituição do seu julgamento**
4. **Webhooks eliminam context switching - configure tudo que puder**
5. **Crons criam disciplina que força de vontade não sustenta**
6. **Memory é seu segundo cérebro - confia nela, alimente-a**
7. **Profiles não são "modos", são especialistas - use o certo**
8. **Rotação de tokens mensal = segurança real, não teatro**
9. **Test_all.sh semanal = paz de espírito**
10. **Documentação viva > documentação perfeita**

---

## 📞 QUANDO TRAVAR (Debug Rápido)

```bash
# 1. Gateway não responde?
journalctl --user -u hermes-gateway -f

# 2. Bot offline?
curl localhost:8642/v1/health
systemctl --user restart hermes-gateway

# 3. Voice não entra?
dpkg -l | grep -E "ffmpeg|libopus|portaudio"
/voice join (tenta de novo)

# 4. Cron não rodou?
hermes cron list
hermes cron run "Nome"

# 5. Webhook falhou?
hermes webhook test github-pr-review
# Check DNS Cloudflare: webhook.menusummo.com.br → IP (Proxy ON)

# 6. Memory perdida?
cat ~/.hermes/channel_directory.json
hermes sessions list
```

---

**Este documento vive em:** `~/.hermes/skills/devops/discord-mastery-pack/references/DAILY_WORKFLOW.md`

**Atualize sempre que descobrir novo padrão. O sistema evolui com você.**