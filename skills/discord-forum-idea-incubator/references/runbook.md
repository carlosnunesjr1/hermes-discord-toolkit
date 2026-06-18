# Runbook Operacional - Discord Forum Idea Incubator

Guia operacional dia-a-dia da Incubadora de Ideias.

---

## 📋 Visão Rápida

| Componente | Comando/Status |
|------------|----------------|
| **Skill** | `discord-forum-idea-incubator` |
| **Scripts** | `~/.hermes/skills/devops/discord-forum-idea-incubator/scripts/` |
| **Config** | `~/.hermes/config.yaml` (seção `discord.forum_incubator`) |
| **Env** | `~/.hermes/incubator.env` |
| **Cron Jobs** | `hermes cron list` |
| **Kanban Board** | `incubator` |
| **Discord Category** | `INCUBADORA` |

---

## 🚀 Início Rápido (Pós-Setup)

```bash
# 1. Carregar env
source ~/.hermes/incubator.env

# 2. Reiniciar gateway
sudo systemctl restart hermes-gateway

# 3. Verificar status
hermes cron list
hermes kanban list
hermes chat -q "Status da incubadora" --toolsets discord
```

---

## 📱 Uso Diário no Discord

### Capturar Ideia (Voice)
1. Entre no canal **#ideias-brutas**
2. Grave áudio (até 3 min)
3. Hermes transcreve → cria thread estruturada automaticamente
4. Thread aparece com tags: `status:capturada`, `prioridade:P3-normal`, etc.

### Capturar Ideia (Texto)
```
#ideias-brutas
> Precisamos adicionar cache Redis no LLM Router para reduzir latência. Prioridade alta, tipo tech-debt, domínio router.
```
→ Thread criada automaticamente.

### Capturar via Reação
1. Em qualquer canal, reaja com 🎯 💡 ou 🚀 em uma mensagem
2. Hermes converte em thread no #ideias-brutas

### Comando Slash (Mais Controle)
```
/ideia "Cache Redis no Router" --tipo tech-debt --prioridade P2-alta --dominio router --esforco M
```

---

## 🔄 Fluxo de Trabalho (Lifecycle)

```
💡 #ideias-brutas (capturada)
    │
    ├─▶ Triagem manual/auto → 🔬 #em-análise (em-debate)
    │       │
    │       ├─▶ Debate 7 dias → ⚗️ #experimentos (validando) → Spike Kanban
    │       │       │
    │       │       └─▶ Viável → ✅ #prontas-para-produção (aprovada)
    │       │
    │       └─▶ Não viável/parado → 📦 #arquivadas (descartada/depois)
    │
    └─▶ Direto para produção (se trivial) → 🚀 Kanban Task
```

### Mover Thread (Comandos)
```
/triagem THREAD_ID --status em-debate --prioridade P2
/spike THREAD_ID --timebox 4h
/promover THREAD_ID --prioridade 2 --assignee default --skill cn-tech-ecosystem
/arquivar THREAD_ID --motivo descartada
```

---

## 🎯 Critérios de Triagem (Semanais)

| Prioridade | Critérios |
|------------|-----------|
| **P1-Urgente** | Alinhado a OKR atual + Esforço ≤ M + Dependências resolvidas |
| **P2-Alta** | Alinhado a OKR + (Esforço ≥ L OU 1 dependência) |
| **P3-Normal** | Não-OKR mas alto valor/baixo esforço (XS/S) |
| **P4-Baixa** | Nice-to-have, backlog futuro |
| **P5-Backlog** | Estacionado (aguarda decisão externa, budget, etc) |

**Auto-arquivamento:** Threads em `#em-análise` sem movimento por 7 dias → arquivadas automaticamente.

---

## ⚗️ Spikes / Validação Técnica

Para ideias `aprovadas` com `esforço ≥ M` ou `complexidade = Alta`:

```bash
# No Discord
/spike THREAD_ID --timebox 4h
```

**O que acontece:**
1. Thread movida para `#experimentos` com status `validando`
2. Task Kanban criada: `Spike: [Título]` com timebox
3. Worker executa spike, posta resultado na thread
4. Verificador valida critérios Pass/Fail
5. Decisão: promover → `#prontas-para-produção` ou arquivar

---

## 🚀 Promoção para Produção (Kanban)

```bash
# No Discord
/promover THREAD_ID --prioridade 2 --assignee default --skill cn-tech-ecosystem
```

**O que acontece:**
1. Thread: status → `aprovada`, move para `#prontas-para-produção`
2. Kanban Task criada com:
   - Title/Body da thread
   - Priority, Assignee, Skill mapeado do domínio
   - Link bidirecional Thread ↔ Task
3. Dispatcher Kanban assume (se `dispatch_in_gateway: true`)

**Mapeamento Domínio → Skill:**
| Domínio | Skill |
|---------|-------|
| career, pim, router, infra | `cn-tech-ecosystem` |
| hermes | `hermes-agent` |
| geral | `system-architect-audit` |

---

## 📊 Monitoramento & Métricas

### Cron Jobs Ativos
```bash
hermes cron list
# incubator-weekly-triage    - Segunda 9h
# incubator-daily-summary    - Diário 18h
# incubator-daily-reconciliation - Meia-noite
```

### Executar Manual
```bash
hermes cron run incubator-weekly-triage
hermes cron run incubator-daily-summary
hermes cron run incubator-daily-reconciliation
```

### Verificar Kanban
```bash
hermes kanban list --status triage
hermes kanban list --status ready
hermes kanban stats
```

### Reconciliação Manual
```bash
# Via Hermes chat
hermes chat -q "Execute reconciliação Forum ↔ Kanban agora" --skills discord-forum-idea-incubator
```

---

## 🔧 Troubleshooting

### Thread não criada ao enviar áudio
```bash
# 1. Verificar STT
hermes config get stt.enabled  # deve ser true
# 2. Verificar canal correto
hermes chat -q "Qual o canal #ideias-brutas ID?" --toolsets discord
# 3. Verificar permissão do bot no canal
# 4. Logs: journalctl -u hermes-gateway -f | grep -i forum
```

### Tags não aplicadas
```bash
# Tags devem existir EXATAMENTE no canal de fórum
# Verificar: Discord → Canal → Gerenciar Tags
# Nomes: "capturada", "P1-urgente", "feature", "XS", "career" (case-sensitive)
```

### Kanban task não criada ao promover
```bash
# 1. Verificar board 'incubator' existe
hermes kanban list --board incubator
# 2. Verificar skill mapeada existe
hermes skills list | grep -E "cn-tech-ecosystem|hermes-agent"
# 3. Verificar profile assignee existe
hermes profile list
```

### Cron jobs não executando
```bash
# 1. Verificar scheduler ativo
hermes cron status
# 2. Verificar logs
journalctl -u hermes-gateway -f | grep -i cron
# 3. Executar manual para testar
hermes cron run incubator-weekly-triage
```

### Reconciliação mostra discrepancies
| Problema | Causa | Fix |
|----------|-------|-----|
| Thread aprovada sem task | Promoção falhou | Re-executar `/promover` |
| Task órfã (sem thread) | Thread deletada | Arquivar task manual |
| Status dessincronizados | Update manual | Reconciliação corrige na próxima execução |

---

## 📁 Estrutura de Arquivos

```
~/.hermes/skills/devops/discord-forum-idea-incubator/
├── SKILL.md                      # Documentação principal
├── scripts/
│   ├── forum_manager.py          # Discord Forum API wrapper
│   ├── idea_processor.py         # Voice/Text → Structured Idea
│   ├── kanban_bridge.py          # Forum ↔ Kanban sync
│   ├── orchestrator.py           # Main orchestrator
│   └── setup_incubator.sh        # Setup interativo
├── templates/                    # (Armazenados no Discord #templates)
└── references/
    └── runbook.md                # Este arquivo
```

---

## 🔐 Segurança & Permissões

### Discord Bot Permissions Necessárias
- `Manage Threads` (criar/arquivar threads)
- `Manage Messages` (posts de sistema)
- `Add Reactions` (reactions de sistema)
- `Read Message History` (backfill)
- `Send Messages` (em fóruns)
- `Create Public Threads` (em fóruns)
- `Manage Tags` (se bot criar tags)

### Variáveis Sensíveis
```bash
# ~/.hermes/.env ou ~/.hermes/incubator.env
DISCORD_BOT_TOKEN=***          # Bot token (não user token)
# NÃO commitar esses arquivos
```

---

## 🔄 Atualizações & Manutenção

### Atualizar Skill
```bash
cd ~/.hermes/skills/devops/discord-forum-idea-incubator
git pull  # se versionado
# ou
hermes skills update discord-forum-idea-incubator
```

### Adicionar Nova Tag
1. Discord → Canal → Gerenciar Tags → Criar
2. Atualizar `forum_manager.py` → `build_applied_tags()` se nova categoria
3. Testar: `hermes chat -q "Teste tag nova" --toolsets discord`

### Mudar Critérios Triagem
Editar `orchestrator.py` → `run_weekly_triage()` ou config no `config.yaml`.

---

## 📞 Suporte & Escalação

| Problema | Contato |
|----------|---------|
| Bug no script | Abrir issue no repo da skill |
| Discord API | Verificar status.discord.com |
| Hermes Gateway | `journalctl -u hermes-gateway -f` |
| Kanban | `hermes kanban status` |

---

## 📚 Referências

- [Skill Principal](./SKILL.md)
- [Discord Forum Channels API](https://discord.com/developers/docs/resources/channel#forum-channels)
- [Hermes Kanban Docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)
- [Hermes Cron Docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [CN Tech Ecosystem](../cn-tech-ecosystem/SKILL.md)

---

*Runbook versão 1.0 - Atualizado: 2026-06-17*