# 🏛️ ARCHITECTURE.md
## Decisões Arquiteturais - Discord Mastery Pack

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                     HERMES AGENT                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Gateway   │  │  Session    │  │    Tool Executor    │ │
│  │  (Manager)  │◄─┤   Store     │  │   (Sandboxed)       │ │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘ │
│         │                                                │
│    ┌────┴────┐                                           │
│    ▼         ▼                                           │
│ ┌──────┐ ┌────────┐                                     │
│ │Discord│ │ Webhook │  ... outras plataformas          │
│ │Adapter│ │ Adapter │                                     │
│ └──────┘ └────────┘                                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌────────────────┐  │
│  │  LLM     │ │  TTS    │ │  STT    │ │   MCP Servers  │  │
│  │ (Nous/   │ │ (Edge/  │ │(faster- │ │ (Notion, GitHub,│  │
│  │  OR)     │ │ Eleven) │ │whisper) │ │  Linear, Obs)  │  │
│  └──────────┘ └─────────┘ └─────────┘ └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Decisões Chave

### 1. User Service vs System Service
**Decisão**: User systemd service (`systemctl --user`)

**Razões**:
- Não requer sudo para restart/logs
- Isola por usuário (multi-tenant ready)
- Persiste após logout com `loginctl enable-linger`
- Logs em `journalctl --user` (não polui system journal)

### 2. Configuração: config.yaml + gateway-config.yaml + .env
**Decisão**: Três arquivos com responsabilidades separadas

| Arquivo | Responsabilidade | Exemplos |
|---------|------------------|----------|
| `config.yaml` | Core Hermes, LLM, tools, memory | model, providers, tts, stt, delegation |
| `gateway-config.yaml` | Comportamento por plataforma | allow_admin_from, user_allowed_commands, voice_enabled |
| `.env` | Secrets (NÃO versionar) | DISCORD_BOT_TOKEN, API_KEYS, WEBHOOK_SECRET |

### 3. Channel Directory (Cache)
**Decisão**: Atualização a cada 5min, persistido em JSON

**Razões**:
- `send_message` tool precisa resolver nome→ID
- Evita API calls repetidas ao Discord
- Fallback graceful se API falhar

### 4. Webhook Delivery: "discord" + deliver_extra.chat_id
**Decisão**: Separar platform type de target

```yaml
# Webhook config
deliver: "discord"
deliver_extra:
  chat_id: "1516397585701666962"
  # thread_id opcional para fóruns
```

**Por que não `discord:CHANNEL_ID`?**
- Parser do gateway valida contra `_BUILTIN_DELIVER_PLATFORMS = {"discord", "telegram", ...}`
- `deliver_extra` permite thread_id, message_thread_id futuros
- Consistente com outras plataformas (telegram, slack, etc.)

### 5. Cron Jobs: Agent Mode vs No-Agent Mode

| Modo | Uso | Exemplo |
|------|-----|---------|
| **Agent** (padrão) | LLM reasoning necessário | Morning check-in, Weekly report |
| **No-Agent** | Script output = mensagem final | Health monitor (silent se OK) |
| **Script** | Script stdout → prompt | Backup report, log analysis |

### 6. Multi-Agent: Profiles + Shared Channel

**Arquitetura**:
```
Channel #geral (history=50)
    │
    ├─ @Carlos Alberto Nunes Avatar (coder profile)
    ├─ @Carlos Alberto Nunes Avatar (architect profile)  
    └─ @Carlos Alberto Nunes Avatar (critic profile)
    
Cada profile:
- SOUL.md próprio (persona)
- config.yaml herdado + overrides
- Sessão isolada por profile (group_sessions_per_user: true)
```

### 7. Voice: Edge TTS + faster-whisper (Local)

**Decisão**: TTS cloud-free (Edge), STT local (faster-whisper base)

**Trade-offs**:
| Aspecto | Edge TTS | ElevenLabs | OpenAI TTS |
|---------|----------|------------|------------|
| Custo | Grátis | $/mês | $/1M chars |
| Qualidade PT-BR | Boa (AntonioNeural) | Excelente | Boa |
| Latência | Baixa | Média | Baixa |
| Offline | ❌ | ❌ | ❌ |

**faster-whisper base**: ~150MB, ~2-3x realtime em CPU, boa precisão PT-BR

### 8. API Server (Port 8642) - OpenAI Compatible

**Propósito**: Permite clientes OpenAI-compatíveis (Open WebUI, LibreChat, etc.)

**Endpoints-chave**:
- `POST /v1/chat/completions` - Chat stateless
- `POST /v1/responses` - Stateful (previous_response_id)
- `GET /v1/models` - Lista hermes-agent
- `GET /health` - Health check para load balancer

**Auth**: `Authorization: Bearer API_SERVER_KEY`

---

## Fluxos de Dados

### Mensagem Discord → Resposta
```
1. Discord Gateway → WebSocket → DiscordAdapter
2. Adapter → MessageEvent → Gateway.handle_message()
3. SessionStore.get_or_create_session()
4. Build context (history + tools + system prompt)
5. Agent.run() → Tool calls → LLM → Response
6. Adapter.send(chat_id, response) → Discord REST API
7. Channel Directory update (async)
```

### Webhook GitHub → Discord
```
1. GitHub → POST https://webhook.menusummo.com.br/webhooks/github-pr-review
2. Caddy (port 80) → reverse_proxy localhost:8644
3. WebhookAdapter._handle_webhook()
4. HMAC validation → Event filter → Prompt render
4. Agent.run() com skills (github-code-review)
5. WebhookAdapter._deliver_cross_platform("discord", ...)
6. DiscordAdapter.send(chat_id, review) → #geral
```

### Cron Job → Discord
```
1. CronTicker (60s) → verifica schedules
2. CronRunner.execute() → cria Agent run
3. Agent.run() com prompt do cron
4. Response → deliver target (discord:CHANNEL_ID)
5. Cross-platform delivery via GatewayRunner.adapters["discord"]
```

---

## Segurança

### Secrets Management
- `.env` = arquivo único com TODOS os secrets
- `chmod 600 ~/.hermes/.env`
- `.gitignore` inclui `.env`, `*.key`, `*.pem`
- Systemd drop-in para env vars sensíveis

### HMAC Webhook Validation
- Por rota: secret próprio + global fallback
- `X-Hub-Signature-256` (GitHub) / `X-Signature` (outros)
- Reject se secret vazio E não loopback

### Discord Permissions
- `allow_admin_from`: Seu user ID = tudo permitido
- `user_allowed_commands`: Lista branca para outros
- `require_mention: true` = não responde sem @menção
- `ignore_no_mention: true` = silencioso se @outro_bot

### Network
- API Server: `127.0.0.1:8642` (loopback only)
- Webhook: `0.0.0.0:8644` → Caddy reverse proxy → Cloudflare
- Discord: WebSocket outbound only (port 443)

---

## Escalabilidade / Limitações

### Atual (Single Instance)
| Componente | Limite | Mitigação |
|------------|--------|-----------|
| Sessões simultâneas | ~100 | `max_concurrent_sessions` |
| Crons paralelos | 4 | `max_parallel_jobs` |
| Turnos por agente | 500 | `agent.max_turns` |
| Context window | 128k (modelo) | `/compress` cron |

### Próximos Níveis
1. **Multi-Gateway**: Redis pub/sub para sync de sessões
2. **Load Balancer**: Múltiplos gateway workers + sticky sessions
3. **Queue**: BullMQ/Redis para webhooks/crons assíncronos
4. **Observability**: OpenTelemetry → Tempo/Loki/Prometheus

---

## Versionamento / Migração

```
v1.0.0 (Current)
├── User service systemd
├── config.yaml + gateway-config.yaml + .env
├── 5 crons essenciais
├── 1 webhook (GitHub PR)
├── Voice: Edge TTS + faster-whisper
├── Multi-agent: 3 profiles (SOUL.md)
└── MCP: Notion, GitHub, Linear, Obsidian

v1.1.0 (Planned)
├── Auto-deploy script (Ansible/Terraform)
├── GitHub Actions CI para config validation
├── Grafana dashboards preset
├── Backup/restore automatizado
└── Multi-region support

v2.0.0 (Future)
├── Plugin marketplace
├── Visual workflow builder
├── Multi-gateway cluster
└── Enterprise SSO (OIDC/SAML)
```

---

## Referências de Código

| Componente | Path |
|------------|------|
| Gateway Runner | `/usr/local/lib/hermes-agent/gateway/run.py` |
| Discord Adapter | `/usr/local/lib/hermes-agent/plugins/platforms/discord/adapter.py` |
| Webhook Adapter | `/usr/local/lib/hermes-agent/gateway/platforms/webhook.py` |
| Config Loader | `/usr/local/lib/hermes-agent/gateway/config.py` |
| Cron System | `/usr/local/lib/hermes-agent/gateway/cron/` |
| Session Store | `/usr/local/lib/hermes-agent/gateway/session.py` |
| Channel Directory | `/usr/local/lib/hermes-agent/gateway/channel_directory.py` |