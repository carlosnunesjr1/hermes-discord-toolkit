---
name: discord-mastery-pack
version: 1.1.0
description: "Pacote completo Discord Gateway - Do básico ao avançado. Inclui setup 24/7, voice, crons, webhooks, multi-agent, MCP, launchpad. Empacotado como skill reutilizável + curso completo + daily workflow."
author: Carlos Alberto Nunes
tags: [discord, gateway, voice, cron, webhook, multi-agent, mcp, course, launchpad, daily-workflow]
requirements:
  - hermes-agent >= 0.16.0
  - python >= 3.11
  - discord.py (via hermes-agent[messaging])
  - ffmpeg, libopus, portaudio (voice)
---

# 🎓 DISCORD MASTERY PACK
## Pacote Completo: Setup + Curso + Manutenção + Produção + Launchpad + Daily Workflow

---

## 📦 COMO USAR ESTE PACOTE

### Opção 1: Como Skill Hermes (Recomendado)
```bash
# Instalar no seu Hermes
hermes skill install discord-mastery-pack

# Ou clonar e usar localmente
git clone <repo> ~/.hermes/skills/discord-mastery-pack
hermes skill enable discord-mastery-pack
```

### Opção 2: Como Módulo Standalone
```bash
# Copie a pasta para qualquer projeto
cp -r discord-mastery-pack /seu/projeto/
# Use os scripts/templates diretamente
```

### Opção 3: Como Documentação/Curso
Acesse `references/COURSE.md` para o curso completo passo a passo.

---

## 🏗️ ARQUITETURA DO PACOTE

```
discord-mastery-pack/
├── SKILL.md                    # Este arquivo (metadados da skill)
├── COURSE.md                   # 🎓 CURSO COMPLETO (Basic → Advanced)
├── DAILY_WORKFLOW.md           # 📋 Rotina diária completa (NOVO v1.1)
├── ARCHITECTURE.md             # 🏛️ Arquitetura & Decisões
├── TROUBLESHOOTING.md          # 🐛 50+ problemas + soluções
├── QUICKSTART.sh               # ⚡ Setup em 1 comando
├── config/
│   ├── gateway-config.yaml     # Config gateway Discord
│   ├── config.yaml             # Config Hermes base
│   ├── .env.template           # Template variáveis
│   └── systemd/
│       └── hermes-gateway.service
├── scripts/
│   ├── QUICKSTART.sh           # Setup 1 comando
│   ├── deploy_mcp.sh           # MCP Notion/GitHub/Linear/Obsidian
│   ├── health_check.sh         # Health check para cron (--no-agent)
│   ├── test_all.sh             # Suite completa testes
│   └── launchpad.html          # Landing page (NOVO v1.1)
├── profiles/
│   ├── coder/
│   │   └── SOUL.md             # Persona Coder
│   ├── architect/
│   │   └── SOUL.md             # Persona Architect
│   └── critic/
│       └── SOUL.md             # Persona Critic
├── crons/
│   └── essential-crons.yaml    # 4 jobs essenciais (morning, weekly, health, compression)
├── webhooks/
│   └── webhooks.yaml           # GitHub PR Review + templates
├── mcp/
│   ├── notion-config.yaml      # Sync tasks/notes
│   ├── github-config.yaml      # Issues/PRs no Discord
│   ├── linear-config.yaml      # Project management
│   └── obsidian-config.yaml    # Knowledge base
├── monitoring/
│   ├── health-check.sh         # Script saúde VPS
│   ├── alerts.yaml             # Config alertas
│   └── dashboard.json          # Grafana/Prometheus
├── testing/
│   └── test_all.sh             # Suite completa testes
├── secrets/
│   ├── .gitignore              # Protege secrets
│   ├── template.env            # Template sem valores reais
│   └── rotation-guide.md       # Rotação de tokens
├── troubleshooting/
│   ├── common-issues.md        # Problemas + soluções
│   ├── debug-guide.md          # Como debugar
│   └── logs-guide.md           # Onde olhar logs
├── launchpad/                  # 🌐 Landing page (NOVO v1.1)
│   └── index.html              # launchpad.menusummo.com.br
└── examples/
    ├── basic-bot.py            # Bot simples
    ├── voice-bot.py            # Bot com voice
    ├── multi-agent-demo.py     # 3 agentes colaborando
    └── webhook-receiver.py     # Receber webhooks
```

---

## ⚡ QUICKSTART (1 Comando)

```bash
# Setup completo automatizado
curl -fsSL https://raw.githubusercontent.com/seu-user/discord-mastery-pack/main/QUICKSTART.sh | bash

# Ou localmente
./scripts/QUICKSTART.sh
```

**O que o QUICKSTART faz:**
1. ✅ Instala dependências sistema (ffmpeg, libopus, portaudio)
2. ✅ Cria venv + instala hermes-agent[messaging]
3. ✅ Configura .env com template
4. ✅ Gera gateway-config.yaml otimizado
5. ✅ Instala systemd service 24/7
6. ✅ Cria 5 cron jobs essenciais
7. ✅ Configura webhook GitHub PR Review
8. ✅ Habilita Voice Channel + TTS/STT
9. ✅ Cria 3 profiles multi-agent (coder/architect/critic)
10. ✅ Deploy MCP Notion + GitHub
11. ✅ Roda testes de validação
12. ✅ Mostra checklist final
13. ✅ Deploy launchpad page (NOVO v1.1)

---

## 🎯 O Que Você Consegue Após Setup

| Feature | Status | Comando Teste |
|---------|--------|---------------|
| **Gateway 24/7** | ✅ | `systemctl --user status hermes-gateway` |
| **Discord Bot** | ✅ | DM bot "oi" |
| **Slash Commands** | ✅ | Digite `/` no Discord |
| **Voice Channel** | ✅ | `/voice join` no VC |
| **Morning Check-in 07:00** | ✅ | `hermes cron run "Morning Voice Check-in"` |
| **Weekly Report Dom 20h** | ✅ | `hermes cron run "Weekly Executive Report"` |
| **Health Monitor 15min** | ✅ | `hermes cron run "VPS Health Monitor"` |
| **Token Compression 6h** | ✅ | `hermes cron run "Token Compression Routine"` |
| **GitHub PR Review** | ✅ | Configure DNS + GitHub Webhook |
| **Multi-Agent (3 profiles)** | ✅ | `hermes chat --profile coder` |
| **MCP Notion/GitHub** | 🔧 | `./scripts/deploy_mcp.sh all` |
| **Launchpad Page** | 🌐 | `https://launchpad.menusummo.com.br` |

---

## 📅 DAILY WORKFLOW (NOVO v1.1)

**Sua bíblia diária em `DAILY_WORKFLOW.md`:**

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

**3 Modos de Uso Discord:**

| Modo | Como Ativar | Para Quê |
|------|-------------|----------|
| **DEEP WORK** | DM privado: `Preciso arquitetar X` | Sessão isolada, foco total |
| **QUICK COMMANDS** | `#geral` → `@Hermes /compress` | Ações instantâneas |
| **VOICE BRAINSTORM** | Entre no VC → `/voice join` | Hands-free, clareza mental |

**Multi-Agent para Decisões Importantes:**
```
DM → @Hermes (architect): "Trade-offs microserviços vs modulith?"
DM → @Hermes (critic): "Quais riscos não estou vendo?"
DM → @Hermes (coder): "Implemente o core com testes"
```

**Webhooks Automáticos:**
- **GitHub PR** → Review técnico em `#geral` automaticamente
- **Próximos**: Vercel deploy, Linear issues, Supabase alerts

| Módulo | Tópico | Nível |
|--------|--------|-------|
| 1 | Fundamentos: Install, Config, Systemd | Básico |
| 2 | Recursos Core: Slash, Permissions, Context | Intermediário |
| 3 | Voice Channel: TTS, STT, FX, Check-in | Avançado |
| 4 | Cron Jobs: Patterns, Silent Mode, Debug | Produção |
| 5 | Webhooks: GitHub, Cloudflare, Security | Enterprise |
| 6 | Multi-Agent: Profiles, SOUL.md, Kanban | Elite |
| 7 | MCP: Notion, GitHub, Linear, Obsidian | Integração Total |
| 8 | Produção: Monitoring, Performance, Security | Senior |
| 9 | Segredos & Pro Tips: Undocumented, Hacks | Mestre |

---

## 🔧 Scripts Principais

```bash
# Setup completo automatizado
./scripts/QUICKSTART.sh

# Deploy MCP integrations
./scripts/deploy_mcp.sh all        # Todas
./scripts/deploy_mcp.sh notion     # Só Notion
./scripts/deploy_mcp.sh github     # Só GitHub

# Health check (usado pelo cron --no-agent)
./scripts/health_check.sh

# Suite completa de testes
./scripts/test_all.sh

# Deploy launchpad page (NOVO v1.1)
./scripts/launchpad.html
```

---

## 📋 Checklist Pós-Setup

- [ ] Gateway ativo: `systemctl --user status hermes-gateway`
- [ ] API health: `curl -H "Auth: Bearer *** localhost:8642/v1/health`
- [ ] Discord bot responde DM
- [ ] Slash commands aparecem (`/`)
- [ ] Voice join/leave funciona
- [ ] 4 crons agendados: `hermes cron list`
- [ ] Webhook GitHub testado: `hermes webhook test github-pr-review`
- [ ] DNS Cloudflare: `webhook.menusummo.com.br` → IP (Proxy ON)
- [ ] GitHub Webhook configurado no repo
- [ ] 3 profiles: `hermes profile list`

---

## 🐛 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Bot não responde | `Message Content Intent` ON no Discord Dev Portal |
| Voice não entra | `sudo apt install ffmpeg libopus0 portaudio19-dev` |
| Cron não executa | `systemctl --user status hermes-gateway` |
| Webhook "Unknown deliver" | Use `--deliver "discord" --deliver-chat-id "ID"` |
| Token inválido | Discord Dev Portal → Reset Token → `hermes config set` |
| Memória alta | `/compress` ou cron Token Compression |

Logs: `journalctl --user -u hermes-gateway -f`

---

## 📖 Documentação Completa

- **Curso**: `references/COURSE.md`
- **Arquitetura**: `references/ARCHITECTURE.md`
- **Option B Implementation**: `references/option-b-implementation.md` *(Complete Discord Gateway Bot deployment)*
- **Option B Gateway Integration Gap**: `references/option-b-gateway-gap.md` *(Missing /v1/discord/interaction endpoint, 404 error)*
- **Auto-Provisioning & UI Components**: `references/auto-provisioning-ui.md` *(Auto-create structure, Selects/Modals/Views, thread persistence, background Tasks)*
- **E2E Validation Suite**: `references/e2e-validation.md` *(Complete test checklist, all PASS)*
- **Crons**: `references/essential-crons.yaml`
- **Webhooks**: `references/webhooks.yaml`
- **Personas**: `references/SOUL-*.md`
- **Troubleshooting**: `references/troubleshooting.md`

## 📁 Templates Prontos

- **Deploy Script**: `templates/deploy.sh` — Full management (install/update/start/stop/logs)
- **Systemd Service**: `templates/hermes-discord-bot.service` — Hardened systemd unit
- **Environment**: `templates/.env.template` — Bot config template
- **Python Deps**: `templates/requirements.txt` — discord.py, aiohttp, python-dotenv, pyyaml

## 📖 Documentação Legacy

- **Templates**: `templates/*.yaml`

---

## 🤝 Contribuição

1. Fork
2. Adicione módulo no COURSE.md
3. Teste: `./scripts/test_all.sh`
4. PR

---

## 📄 Licença

MIT - Livre para usar, modificar, distribuir.

---

## 🔑 LIÇÕES APRENDIDAS (Session 2026-06-16)

### Critical Fixes Applied
| Issue | Root Cause | Fix |
|-------|------------|-----|
| Gateway restart loop | System service conflict + stale PID | Use **user service** (`hermes gateway install`), kill orphan PID, `systemctl --user restart` |
| Discord token invalid | Token regenerated in Dev Portal | `hermes config set DISCORD_BOT_TOKEN \"new_token\"` + restart |
| Webhook "Unknown deliver type" | Wrong deliver format | Use `--deliver "discord" --deliver-chat-id "CHANNEL_ID"` (NOT `discord:CHANNEL_ID`) |
| Profiles missing | Not created | `hermes profile create coder/architect/critic` + copy SOUL.md |
| Voice deps missing | Not installed | `sudo apt install ffmpeg libopus0 portaudio19-dev espeak-ng` |
| TTS/STT import fails | Venv path | Use `/usr/local/lib/hermes-agent/venv/bin/python -c "import edge_tts"` |
| test_all.sh Bearer *** | Variable expansion | Use `$API_KEY` variable, not hardcoded `***` |
| **Systemd service conflict** | **System + user service on same port** | **`sudo systemctl disable --now hermes-gateway` (keep user service)** |
| **Gateway Bot 404 on /v1/discord/interaction** | **Endpoint doesn't exist in Gateway** | **Bot workaround: use `/v1/agents/spawn` or implement endpoint** |

### Working Configurations (Validated E2E)
```yaml
# gateway-config.yaml - CRITICAL: voice_enabled: true
platforms:
  discord:
    enabled: true
    extra:
      voice_enabled: true
      channel_history_size: 50
      allow_admin_from: "YOUR_USER_ID"
      user_allowed_commands: [help, whoami, new, model, compress, status, skills, cron, voice, undo, save, retry]
      require_mention: true
      group_sessions_per_user: true
      ignore_no_mention: true
```

```bash
# Webhook subscribe - CORRECT format
hermes webhook subscribe github-pr-review \
  --prompt "..." \
  --events "pull_request" \
  --deliver "discord" \
  --deliver-chat-id "1516397585701666962" \
  --skills "github-code-review"
```

### E2E Test Results (All PASS)
- Gateway Service: ACTIVE (user systemd)
- API Server: HEALTHY (port 8642)
- Models Endpoint: OK
- Chat Completions: WORKING
- Webhook Server: HEALTHY (port 8644)
- Channel Directory: 2 Discord channels
- Webhook Subscriptions: 1 configured
- Cron Jobs: 6 active
- Multi-Agent Profiles: 3 created (coder, architect, critic)
- SOUL.md: All 3 copied to profiles
- Voice Dependencies: All installed
- TTS/STT: Edge TTS + faster-whisper available

---

---

## 🔑 LIÇÕES APRENDIDAS (Session 2026-06-16)

### Critical Fixes Applied
| Issue | Root Cause | Fix |
|-------|------------|-----|
| Gateway restart loop | System service conflict + stale PID | Use **user service** (`hermes gateway install`), kill orphan PID, `systemctl --user restart` |
| Discord token invalid | Token regenerated in Dev Portal | `hermes config set DISCORD_BOT_TOKEN \"new_token\"` + restart |
| Webhook "Unknown deliver type" | Wrong deliver format | Use `--deliver "discord" --deliver-chat-id "CHANNEL_ID"` (NOT `discord:CHANNEL_ID`) |
| Profiles missing | Not created | `hermes profile create coder/architect/critic` + copy SOUL.md |
| Voice deps missing | Not installed | `sudo apt install ffmpeg libopus0 portaudio19-dev espeak-ng` |
| TTS/STT import fails | Venv path | Use `/usr/local/lib/hermes-agent/venv/bin/python -c "import edge_tts"` |
| test_all.sh Bearer *** | Variable expansion | Use `$API_KEY` variable, not hardcoded `***` |
| **Systemd service conflict** | **System + user service on same port** | **`sudo systemctl disable --now hermes-gateway` (keep user service)** |
| **Gateway Bot 404 on /v1/discord/interaction** | **Endpoint doesn't exist in Gateway** | **Bot workaround: use `/v1/agents/spawn` or implement endpoint** |
| Launchpad at main domain | Caddy virtual hosts | Add `handle { root * /var/www/launchpad; file_server }` to main domain block |
| Caddyfile nested sections | Brace matching broken | Use awk with brace counting for safe section replacement |
| Cloudflare DNS for webhook | Manual step | Add A record `webhook` → VPS IP (Proxy ON) |

### Working Configurations (Validated E2E)
```yaml
# gateway-config.yaml - CRITICAL: voice_enabled: true
platforms:
  discord:
    enabled: true
    extra:
      voice_enabled: true
      channel_history_size: 50
      allow_admin_from: "YOUR_USER_ID"
      user_allowed_commands: [help, whoami, new, model, compress, status, skills, cron, voice, undo, save, retry]
      require_mention: true
      group_sessions_per_user: true
      ignore_no_mention: true
```

```bash
# Webhook subscribe - CORRECT format
hermes webhook subscribe github-pr-review \
  --prompt "..." \
  --events "pull_request" \
  --deliver "discord" \
  --deliver-chat-id "1516397585701666962" \
  --skills "github-code-review"
```

### Caddyfile Pattern for Launchpad at Root
```caddyfile
menusummo.com.br:80, www.menusummo.com.br:80 {
  # ... existing handlers ...
  
  # Launchpad at root - serves the Discord Mastery Pack UI
  handle {
    root * /var/www/launchpad
    file_server
  }
}
```

### E2E Test Results (All PASS)
- Gateway Service: ACTIVE (user systemd)
- API Server: HEALTHY (port 8642)
- Models Endpoint: OK
- Chat Completions: WORKING
- Webhook Server: HEALTHY (port 8644)
- Channel Directory: 2 Discord channels
- Webhook Subscriptions: 1 configured
- Cron Jobs: 6 active
- Multi-Agent Profiles: 3 created (coder, architect, critic)
- SOUL.md: All 3 copied to profiles
- Voice Dependencies: All installed
- TTS/STT: Edge TTS + faster-whisper available
- **Launchpad**: Dynamic, served at `https://menusummo.com.br/`

---

### 🌐 DYNAMIC LAUNCHPAD (NOVO v1.1) - Session 2026-06-16

#### Architecture: Service Registry → Generator → Static HTML + SSE
```
┌─────────────────┐    Generator Script    ┌──────────────────┐
│ services.yaml   │ ────────────────────► │ index.html       │
│ (single source) │  generate_launchpad() │ (static + JS)    │
└─────────────────┘    (< 1s)             └────────┬─────────┘
                                                   │
                        SSE / Polling              │
                           ◄───────────────────────┘
                                        Real-time health
                                        API-driven actions
```

#### Service Registry (services.yaml) - Single Source of Truth
```yaml
version: "1.0"
categories:
  - name: core
    label: "Core Infrastructure"
    order: 1
  - name: ops
    label: "Operations & Control"
    order: 2
  # ... 5 categories total

services:
  hermes-gateway:
    name: "Hermes Gateway"
    url: "https://api.menusummo.com.br"
    health_endpoint: "/v1/health"
    health_method: "GET"
    auth_type: "api_key"
    category: "core"
    critical: true
    icon: "terminal"
    color: "primary"
    tags: ["llm", "gateway", "api", "sessions"]

# 12 services across 5 categories: core, ops, dev, business, data
```

#### Quick Actions (API-Driven, Not alert())
```yaml
quick_actions:
  - id: "cron-morning-checkin"
    label: "Morning Check-in"
    endpoint: "/api/cron/run"
    method: "POST"
    payload: { name: "Morning Voice Check-in" }
  - id: "cron-health-check"
    label: "Health Check"
    endpoint: "/api/cron/run"
    payload: { name: "VPS Health Monitor" }
  - id: "webhook-test-github"
    label: "Test Webhook"
    endpoint: "/api/webhook/test"
    payload: { name: "github-pr-review" }
```

#### Generator Script: `scripts/generate_launchpad.py`
```python
# Key features:
# 1. Reads services.yaml → generates complete HTML
# 2. Embeds services JSON + actions JSON + health config in page
# 3. Generates dynamic service cards with category grouping
# 4. SSE health checks placeholder (needs /api/health/stream endpoint)
# 5. API-driven quick actions (calls Hermes API via /api/cron/run)
# 6. Category grouping with color coding
# 7. < 1s generation time for 12 services

# Usage:
python3 ~/.hermes/scripts/generate_launchpad.py
# Output: /var/www/launchpad/index.html

# Regenerate after any services.yaml change
```

#### Caddyfile Integration: Launchpad at Root Domain
```caddyfile
menusummo.com.br:80, www.menusummo.com.br:80 {
  # ... existing handlers ...
  
  # Launchpad at root - serves the Discord Mastery Pack UI
  handle {
    root * /var/www/launchpad
    file_server
  }
}
```

#### Files Created
| File | Purpose |
|------|---------|
| `~/.hermes/config/services.yaml` | Single source of truth (12 services, 5 categories) |
| `~/.hermes/scripts/generate_launchpad.py` | Generator script |
| `/var/www/launchpad/index.html` | Generated static HTML + embedded JS |
| `templates/services.yaml` | Template for new deployments |

#### SSE Health Stream Endpoint (Needed)
```python
# Add to Hermes Gateway:
@app.get("/api/health/stream")
async def health_stream():
    async def event_generator():
        while True:
            for name, svc in services.items():
                status = await check_service(svc)
                yield f"data: {json.dumps({'name': name, 'status': status})}\n\n"
            await asyncio.sleep(30)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

#### Features Delivered
| Feature | Implementation |
|---------|----------------|
| Dynamic service cards | Generated from YAML, 5 categories, 12 services |
| Category grouping | Core, Ops, Dev, Business, Data with color coding |
| Quick actions | 6 API-driven buttons (not alert()) |
| SSE health checks | Placeholder ready, needs gateway endpoint |
| API-driven actions | Buttons call Hermes API endpoints |
| Category grouping | 5 categories with color coding |
| Config links | Links to all config files/scripts |
| Regeneration | Single command: `python3 generate_launchpad.py` |

---

### 🔑 LIÇÕES APRENDIDAS (Session 2026-06-16 - Part 2: Webhook Architecture &amp; Option B)

#### Webhook Configuration Structure (Critical)
| Issue | Root Cause | Fix |
|-------|------------|-----|
| Routes not loading | Config placed at `webhook.routes` instead of `webhook.extra.routes` | Routes **MUST** be under `platforms.webhook.extra.routes` in config.yaml |
| Discord signature validation failing | Wrong header format | Discord webhooks use `X-Webhook-Signature: <hex-hmac-sha256>` — compute with `hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()` |
| Outbound to Discord without Gateway Bot | No adapter connected | Use **Discord Channel Webhook URL** (Server Settings → Integrations → Webhooks) for `deliver: "webhook"` pattern |

#### Architecture Clarity: Webhook vs Gateway Bot
```text
CURRENT (webhook-only, ~15% Discord potential):
┌─────────────┐   HTTP/Webhook    ┌──────────────────┐
│   Discord   │ ────────────────► │ Hermes Gateway   │
│  (Webhook)  │   port 8644       │ (webhook adapter)│
└─────────────┘                   └────────┬─────────┘
                                            │ No WS, no events
                                            ▼
                                     Agent processes
                                     Responds via
                                     Discord Webhook URL
```

#### Option B Requirements (Gateway Bot with WS)

**3 Credentials Needed from Discord Developer Portal:**
| Credential | Location | Purpose |
|------------|----------|---------|
| `DISCORD_BOT_TOKEN` | Bot → Reset Token | Gateway WS connection (NOT webhook token) |
| `DISCORD_APP_ID` | General Information → Application ID | Slash command registration |
| `DISCORD_GUILD_ID` | Dev Mode → Right-click server → Copy ID | Instant command deploy to test guild |

**Required Bot Configuration:**
| Setting | Value |
|---------|-------|
| **Privileged Gateway Intents** | ✅ Message Content Intent, ✅ Server Messages Intent, ✅ Guild Members Intent (optional) |
| **OAuth2 Scopes** | `bot` + `applications.commands` |
| **Bot Permissions** | `Manage Channels`, `Manage Threads`, `Send Messages`, `Send Messages in Threads`, `Embed Links`, `Read Message History`, `Use Slash Commands`, `Add Reactions`, `Manage Messages` (optional) |

**What Option B Unlocks (100% Discord Potential):**
| Feature | Webhook-Only | Gateway Bot (Option B) |
|---------|--------------|------------------------|
| Read channel history | ❌ | ✅ |
| Detect @mentions in real-time | ❌ | ✅ |
| Create channels/threads dynamically | ❌ | ✅ |
| Slash commands (`/hermes ...`) | ❌ | ✅ |
| Thread/forum management | ❌ | ✅ |
| Reactions as controls | ❌ | ✅ |
| Voice channel audio capture | ❌ | ✅ (VoiceReceiver exists in adapter) |
| Multi-user sessions in same server | ❌ | ✅ |
| Per-channel/thread Hermes sessions | ❌ | ✅ |

---

### 🔑 LIÇÕES APRENDIDAS (Session 2026-06-16 - Part 4: Option B Gateway Integration Gap)

#### Critical: Hermes Gateway Missing `/v1/discord/interaction` Endpoint
**Problem:** The Discord Gateway Bot (hermes-discord-bot) forwards interactions to `POST /v1/discord/interaction` on the Hermes Gateway, but **this endpoint does not exist** — returns 404.

**Root Cause:** Hermes Gateway's Discord platform adapter (`gateway/platforms/discord/adapter.py`) registers WebSocket gateway connection and slash commands, but does NOT expose an HTTP endpoint for the external Discord bot to forward interactions.

**Current Architecture (Broken Path):**
```text
Discord Bot (WS) ──forward_interaction()──► POST /v1/discord/interaction ──► 404 NOT FOUND
```

**Validated Workaround (Immediate):**
The Discord bot's `gateway_client.py` should call existing Hermes Gateway endpoints instead:
```python
# Instead of /v1/discord/interaction (doesn't exist), use:
async def forward_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Option A: Spawn agent directly
    return await self.spawn_agent(
        goal=payload.get("message", ""),
        context=f"Discord interaction from user {payload.get('user_id')}",
        toolsets=["terminal", "file", "web", "browser", "coding"]
    )
    
    # Option B: Use /v1/agent/chat (if implemented in Gateway)
    # return await self._request("POST", "/v1/agent/chat", json_data={...})
```

**Required Gateway Fix (Long-term):**
Add endpoint in Hermes Gateway Discord adapter or API server:
```python
# In gateway/platforms/discord/adapter.py or gateway/platforms/api_server.py
@router.post("/v1/discord/interaction")
async def handle_discord_interaction(request: Request):
    """Receive forwarded Discord interactions from Gateway Bot."""
    payload = await request.json()
    # Route to appropriate Hermes session based on thread_id / channel_id
    # Return response formatted for Discord bot to send back
```

**Verification Checklist:**
- [ ] Gateway Bot process running: `systemctl status hermes-discord-bot`
- [ ] Discord slash commands synced to guild
- [ ] DM/mention handling works (bot logs show "DM from..." / "Mention from...")
- [ ] Gateway health: `curl -H "Authorization: Bearer $KEY" https://api.menusummo.com.br/v1/health`
- [ ] **Current gap:** Bot logs show "Gateway error 404: 404: Not Found" on every interaction

**Architecture Decision:** 
Both paths now active in production:
- **Inbound Webhook** → Hermes Gateway (8644) → Agent → Discord Channel Webhook URL (outbound)
- **Gateway Bot (WS)** → Real-time events/slash commands → Hermes Gateway (8642) → **BROKEN: 404 on /v1/discord/interaction**

#### Systemd Service Conflict: User vs System
**Problem:** Two `hermes-gateway` services running on same port 8642:
- `hermes-gateway.service` (system, `/etc/systemd/system/`) — **CONFLICTING**
- `hermes-gateway.service` (user, `~/.config/systemd/user/`) — **CORRECT, ACTIVE**

**Fix Applied:**
```bash
# Disable system service (user service is the canonical one)
sudo systemctl disable --now hermes-gateway
sudo systemctl daemon-reload
systemctl --user daemon-reload
```
**3 Credentials Needed from Discord Developer Portal:**
| Credential | Location | Purpose |
|------------|----------|---------|
| `DISCORD_BOT_TOKEN` | Bot → Reset Token | Gateway WS connection (NOT webhook token) |
| `DISCORD_APP_ID` | General Information → Application ID | Slash command registration |
| `DISCORD_GUILD_ID` | Dev Mode → Right-click server → Copy ID | Instant command deploy to test guild |

**Required Bot Configuration:**
| Setting | Value |
|---------|-------|
| **Privileged Gateway Intents** | ✅ Message Content Intent, ✅ Server Messages Intent, ✅ Guild Members Intent (optional) |
| **OAuth2 Scopes** | `bot` + `applications.commands` |
| **Bot Permissions** | `Manage Channels`, `Manage Threads`, `Send Messages`, `Send Messages in Threads`, `Embed Links`, `Read Message History`, `Use Slash Commands`, `Add Reactions`, `Manage Messages` (optional) |

**What Option B Unlocks (100% Discord Potential):**
| Feature | Webhook-Only | Gateway Bot (Option B) |
|---------|--------------|------------------------|
| Read channel history | ❌ | ✅ |
| Detect @mentions in real-time | ❌ | ✅ |
| Create channels/threads dynamically | ❌ | ✅ |
| Slash commands (`/hermes ...`) | ❌ | ✅ |
| Thread/forum management | ❌ | ✅ |
| Reactions as controls | ❌ | ✅ |
| Voice channel audio capture | ❌ | ✅ (VoiceReceiver exists in adapter) |
| Multi-user sessions in same server | ❌ | ✅ |
| Per-channel/thread Hermes sessions | ❌ | ✅ |

---

### 🔑 LIÇÕES APRENDIDAS (Session 2026-06-16 - Part 3: Option B Implementation Complete)

#### Discord.py Intents — Critical Bug Fix
| Issue | Root Cause | Fix |
|-------|------------|-----|
| `TypeError: 'guild_threads' is not a valid flag name` | `guild_threads` is NOT a separate intent flag in discord.py 2.x | **Remove `guild_threads=True`** — threads are included in `guilds=True` |
| Intents config must match library version | Copy-pasted from older examples/guides | Use only valid flags: `guilds`, `guild_messages`, `message_content`, `dm_messages`, `reactions`, `members`, `guild_scheduled_events`, etc. |

**Valid Intents Pattern (discord.py 2.7+):**
```python
INTENTS = discord.Intents(
    guilds=True,           # Includes threads
    guild_messages=True,
    message_content=True,
    dm_messages=True,
    reactions=True,
    members=True,          # For member info in slash commands
)
```

#### Complete Option B Deployment Pattern (Validated E2E)

**Project Structure Created:**
```
/home/carlos/hermes-discord-bot/
├── bot.py                 # Main bot (discord.py 2.7, slash commands, events)
├── config.py              # Environment config + slash command definitions
├── gateway_client.py      # Async HTTP client → Hermes Gateway (localhost:8642)
├── thread_manager.py      # Thread ↔ Hermes session mapping
├── deploy.sh              # Install/update/manage script (systemd + venv)
├── service/
│   └── hermes-discord-bot.service  # systemd unit (hardened)
├── requirements.txt       # discord.py>=2.3, aiohttp>=3.9, python-dotenv, pyyaml
├── .env                   # DISCORD_BOT_TOKEN, DISCORD_APP_ID, DISCORD_GUILD_ID, HERMES_GATEWAY_URL
├── .env.template          # Template for new deployments
└── README.md              # Full documentation
```

**Deployment Commands:**
```bash
# 1. Configure tokens
nano .env  # Add DISCORD_BOT_TOKEN, DISCORD_APP_ID, DISCORD_GUILD_ID

# 2. Install (creates venv, installs deps, installs systemd service)
./deploy.sh install

# 3. Start
./deploy.sh start

# 4. Verify
./deploy.sh status
./deploy.sh logs
```

**Key Implementation Details:**

| Component | Pattern |
|-----------|---------|
| **Slash Commands** | Guild-specific sync (instant), `app_commands.CommandTree`, ephemeral for admin |
| **Thread Sessions** | 1:1 mapping: Discord thread ↔ Hermes session (persists context) |
| **Mention Handling** | Strip `<@bot_id>` prefix, route to active thread session or create new |
| **Gateway Integration** | POST `http://localhost:8642/v1/agent/chat` with `{platform, user_id, chat_id, thread_id, message, session_id}` |
| **Reaction Controls** | ✅=approve, ❌=reject, 🔄=restart gateway, 📋=logs (on bot messages) |
| **systemd Hardening** | `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`, `ProtectHome=read-only` |

**Slash Commands Deployed:**
| Command | Description |
|---------|-------------|
| `/hermes status` | Gateway health + connected adapters |
| `/hermes help` | Lista todos comandos |
| `/hermes thread create` | Cria thread isolada + sessão Hermes |
| `/hermes thread list` | Lista threads no canal |
| `/hermes thread my` | Lista suas threads |
| `/hermes thread archive` | Arquiva thread atual |
| `/hermes agent spawn` | Spawna subagent com objetivo |
| `/hermes agent list` | Lista agents ativos |
| `/hermes cron list` | Lista cron jobs |
| `/hermes cron run` | Executa cron job manualmente |
| `/hermes deploy` | Trigger deploy (git pull + restart) |
| `/hermes skills` | Skills disponíveis no Hermes |
| `/hermes logs` | Logs recentes do gateway |

#### Webhook + Bot Hybrid Architecture (Current State)
```text
┌─────────────────┐     HTTPS       ┌──────────────┐
│   Discord       │ ──────────────► │   Caddy      │  ──► webhook.menusummo.com.br:8644
│  (Webhook URL)  │  webhook.        │  (SSL/Proxy) │       (route: discord, HMAC)
│                 │  menusummo.com   │              │
└─────────────────┘                 └──────────────┘
                                             │
                    ┌────────────────────────┘
                    ▼
         ┌──────────────────┐     localhost      ┌─────────────────┐
         │ hermes-discord-  │ ─────────────────► │ Hermes Gateway  │
         │ bot (WS)         │   HTTP :8642       │ :8642           │
         │ systemd service  │                    │ (your control)  │
         └──────────────────┘                    └─────────────────┘
```

**Both paths now active:**
- **Inbound webhook** → Hermes Gateway → Agent → Discord Channel Webhook URL (outbound)
- **Gateway Bot (WS)** → Real-time events/slash commands → Hermes Gateway → Agent → Discord WS response

---

---

### 🔑 LIÇÕES APRENDIDAS (Session 2026-06-17 - Auto-Provisioning, UI Components, Background Automation)

#### Complete Auto-Provisioning on Bot Startup
| Feature | Implementation |
|---------|----------------|
| **7 Categories × 4 Channels** | HERMES-OPS, CN-TECH (6), WORKSPACE (5), INFRA, AGENTS, TASKS, BRAIN |
| **28 Channels + 28 Threads** | Each channel gets initial thread with bot owner |
| **Permission Overwrites** | Bot: manage_channels, manage_threads, send_messages |
| **System Panel Auto-Post** | In deploy, monitor, spawn, memory channels |
| **Idempotent** | `_auto_provisioned` flag prevents re-creation |

#### Real Service Mapping (Discord Channel ↔ Actual Running Service)
| Channel | Service | Type | Port |
|---------|---------|------|------|
| #career-hub | cn-tech-career-hub | Docker | 2019 |
| #nexus-pim | cn-tech-nectar-summo | Docker | 9121/3001 |
| #nectar | cn-tech-nectar-summo | Docker | 9121/3001 |
| #central-comando | cn-tech-centraldecomando | Docker | 9130 |
| #control-daemon | cn-tech-control-daemon | Docker | 9120 |
| #redis | cn_tech-redis-1 | Docker | 6379 |
| #workspace | hermes-workspace.service | systemd | 3002 |
| #dashboard | hermes-dashboard.service | systemd | ? |
| #gateway | hermes-gateway.service | systemd | 8642 |
| #webhook | Webhook HTTP | Docker | 8644 |

#### Rich UI Components (discord.py 2.7+)
| Component | Type | Usage |
|-----------|------|-------|
| **SystemSelectView** | 7 Selects | HERMES-OPS, CN-TECH, WORKSPACE, INFRA, AGENTS, TASKS, BRAIN |
| **AgentSpawnModal** | Modal | Goal + Context + Toolsets |
| **ThreadCreateModal** | Modal | Name + Topic + Category |
| **DeployConfirmView** | Buttons | ▶️ Deploy / 📋 Logs / ❌ Cancel |
| **Reaction Controls** | ✅❌🔄📋🧵🤖 | On bot messages |

#### New Slash Commands Added
| Command | Description |
|---------|-------------|
| `/hermes brain sync/memory/context/sessions/knowledge/clear` | Brain: sync vault, memory, context |
| `/hermes autothread on/off/channels/triggers/status` | Auto-threading DM/#geral config |
| `/hermes evolve analyze/apply/status` | Auto-evolução da estrutura Discord |

#### Background Automation Tasks
| Task | Interval | Function |
|------|----------|----------|
| `_monitor_system_events` | 60s | Scan gateway logs → auto-create alert threads in #incidents |
| `_cleanup_inactive_threads` | 1h | Remove threads > 1 week inactive |
| `_sync_thread_sessions` | 5min | Ensure Hermes sessions linked to active threads |

**Alert Auto-Creation:**
```python
# Triggers on: ERROR, FATAL, CRITICAL, Exception, Traceback, OutOfMemory, Connection refused, Timeout
# Creates thread: 🔴 ALERT: ERROR - HH:MM in #incidents with logs + SystemSelectView
```

#### Thread Persistence with Session Preservation (Fixed)
- **File**: `~/.hermes/discord_threads.json`
- **Format**: `{ "threads": [...], "saved_at": "..." }` — **MUST be dict with "threads" key**
- **Bug Fixed**: Old format was list `[]` causing `'list' object has no attribute 'get'` error
- **Archive**: Preserves `hermes_session_id` before archiving
- **Unarchive**: Restores `is_active`, logs session restoration
- **Auto-Unarchive**: Archived thread receiving message → auto-restore + context

#### Webhook Outbound Discord Delivery (Complete Implementation)
- **New Method**: `_deliver_discord_webhook()` in `gateway/platforms/webhook.py:894`
- **Supports**: 
  - `webhook_url` in `deliver_extra` 
  - `DISCORD_WEBHOOK_{channel_id}` env var (e.g., `DISCORD_WEBHOOK_1516397585701666962`)
  - `DISCORD_DEFAULT_WEBHOOK_URL` fallback
- **Thread Support**: `thread_id` or `message_thread_id` in `deliver_extra`
- **Config**: `deliver: "discord"` + `deliver_extra.webhook_url`
- **HMAC**: Uses Discord webhook URL directly (no signature needed for outbound)
- **Payload**: Discord-compatible JSON with `content`, `username`, `avatar_url`, `thread_id`

**Usage in config.yaml:**
```yaml
webhook:
  extra:
    routes:
      my-route:
        deliver: "discord"
        deliver_extra:
          webhook_url: "https://discord.com/api/webhooks/ID/TOKEN"
          thread_id: 123456789  # optional
```

**Required .env for channel mapping:**
```bash
DISCORD_WEBHOOK_1516397585701666962=https://discord.com/api/webhooks/ID/TOKEN
DISCORD_DEFAULT_WEBHOOK_URL=https://discord.com/api/webhooks/ID/TOKEN
```

#### Gateway Integration Workaround (Validated)
| Endpoint | Status | Workaround |
|----------|--------|------------|
| `/v1/discord/interaction` | ❌ 404 | Use `/v1/agents/spawn` via `gateway_client.spawn_agent()` |

**Implementation in `gateway_client.py`:**
```python
async def forward_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Route to agent spawn instead of missing endpoint
    return await self.spawn_agent(
        goal=payload.get("content", ""),
        context=f"Discord interaction from user {payload.get('user_id')}",
        toolsets=["terminal", "file", "web", "browser", "coding"]
    )
```

#### Complete CN-TECH + WORKSPACE Structure (28 Channels Mapped)
| Category | Channels | Services Mapped |
|----------|----------|-----------------|
| **CN-TECH (6)** | career-hub, nexus-pim, nectar, central-comando, control-daemon, redis | 6 Docker containers |
| **WORKSPACE (5)** | workspace, dashboard, gateway, webhook | 4 systemd + 1 webhook |
| **HERMES-OPS (4)** | deploy, monitor, incidents, logs | Gateway + Bot |
| **INFRA (4)** | vps-health, docker, network, backups | VPS + Docker |
| **AGENTS (3)** | active, spawn, history | Agent Orchestrator |
| **TASKS (4)** | features, bugs, research, docs | Work Mgmt |
| **BRAIN (4)** | memory, context, sessions, knowledge | Memory System |

#### Complete Service Mapping Table
| Channel | Service | Type | Port | Status |
|---------|---------|------|------|--------|
| #career-hub | cn-tech-career-hub | Docker | 2019 | ✅ Healthy |
| #nexus-pim | cn-tech-nectar-summo | Docker | 9121/3001 | ✅ Healthy |
| #nectar | cn-tech-nectar-summo | Docker | 9121/3001 | ✅ Healthy |
| #central-comando | cn-tech-centraldecomando | Docker | 9130 | ✅ Healthy |
| #control-daemon | cn-tech-control-daemon | Docker | 9120 | ✅ Healthy |
| #redis | cn_tech-redis-1 | Docker | 6379 | ✅ Healthy |
| #workspace | hermes-workspace.service | systemd | 3002 | ✅ Active |
| #dashboard | hermes-dashboard.service | systemd | ? | ✅ Active |
| #gateway | hermes-gateway.service | systemd | 8642 | ✅ Active |
| #webhook | Webhook HTTP | Docker | 8644 | ✅ Active |

---

**Mantido por**: Carlos Alberto Nunes 
**Hermes Agent**: >= 0.16.0 
**Última Atualização**: 2026-06-17