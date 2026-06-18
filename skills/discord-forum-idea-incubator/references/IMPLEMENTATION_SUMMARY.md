# Discord Forum Idea Incubator - Resumo da Implementação

## 📦 O que foi criado

### Skill Principal
```
~/.hermes/skills/devops/discord-forum-idea-incubator/
├── SKILL.md                          # Documentação completa
├── scripts/
│   ├── forum_manager.py              # Discord Forum API wrapper
│   ├── idea_processor.py             # Voice/Text → Structured Idea
│   ├── kanban_bridge.py              # Forum ↔ Kanban sync bidirecional
│   ├── orchestrator.py               # Orquestrador principal
│   ├── setup_incubator.sh            # Setup interativo completo
│   └── setup_tags.py                 # Cria tags necessárias
└── references/
    └── runbook.md                    # Guia operacional dia-a-dia
```

---

## 🔧 Componentes Técnicos

### 1. **ForumManager** (`forum_manager.py`)
Wrapper assíncrono para Discord Forum Channels API:
- `create_thread()` - Cria threads com tags
- `list_threads()` - Lista threads ativas/arquivadas (usa guild endpoint)
- `get_thread()` - Obtém thread por ID
- `update_thread()` - Atualiza nome, archive, lock, tags
- `send_message()` - Envia mensagens na thread
- `build_applied_tags()` - Converte parâmetros em tag IDs
- `find_tag_id()` - Busca tag por nome

### 2. **IdeaProcessor** (`idea_processor.py`)
Transforma entradas brutas em threads estruturadas:
- `process_raw_idea()` - Pipeline completo: voz/texto → StructuredIdea
- Classificação automática: tipo, prioridade, esforço, domínio
- Limpeza de transcrição de voz (remove filler words PT-BR)
- Parser de slash command: `/ideia "titulo" --tipo X --prioridade Y`
- Templates de thread (Feature, Tech Debt, Spike)

### 3. **KanbanBridge** (`kanban_bridge.py`)
Sincronização bidirecional Forum ↔ Kanban:
- `thread_to_kanban()` - Thread → Task Kanban rica
- `kanban_to_thread_update()` - Task progress → Thread message
- `reconcile()` - Detecção de dessincronização
- Mapeamento domínio → skill automático

### 4. **IncubatorOrchestrator** (`orchestrator.py`)
Orquestrador de alto nível:
- Handlers: mensagem, voz, reação, slash commands
- Pipeline: captura → triagem → spike → promoção → Kanban
- Cron jobs: triagem semanal, resumo diário, reconciliação
- Slash commands: `/triagem`, `/spike`, `/promover`, `/arquivar`, `/resumo-incubadora`

---

## 🚀 Como Usar (Pós-Setup)

### 1. Configurar Environment
```bash
source ~/.hermes/incubator.env
sudo systemctl restart hermes-gateway
```

### 2. Criar Canais de Fórum no Discord
Crie a categoria **INCUBADORA** com 6 canais de fórum:
| Canal | Propósito |
|-------|-----------|
| `#ideias-brutas` | Captura inicial (voice/text) |
| `#em-análise` | Debate estruturado |
| `#experimentos` | Spikes/PoCs |
| `#prontas-para-produção` | Aprovadas, aguardando Kanban |
| `#arquivadas` | Decididas (feitas/descartadas/depois) |
| `#templates` | Templates de thread |

### 3. Criar Tags
```bash
# Preencher IDs em setup_tags.py e executar
python3 ~/.hermes/skills/devops/discord-forum-idea-incubator/scripts/setup_tags.py
```

Tags necessárias por canal:
- **status**: capturada, em-debate, validando, aprovada, arquivada, feita
- **prioridade**: P1-urgente, P2-alta, P3-normal, P4-baixa, P5-backlog
- **tipo**: feature, bug, tech-debt, pesquisa, processo, infra
- **esforco**: XS, S, M, L, XL, desconhecido
- **dominio**: career, pim, router, infra, hermes, geral

### 4. Usar no Dia a Dia

**Capturar ideia (Voice):**
1. Entre em `#ideias-brutas`
2. Grave áudio (até 3 min)
3. Thread criada automaticamente com tags

**Capturar ideia (Texto):**
```
#ideias-brutas
> Precisamos adicionar cache Redis no Router. Prioridade alta, tech-debt, domain router.
```

**Comando Slash (controle total):**
```
/ideia "Cache Redis" --tipo tech-debt --prioridade P2-alta --dominio router --esforco M
```

**Triagem (manual/auto):**
```
/triagem THREAD_ID --status em-debate --prioridade P2
```

**Spike técnico:**
```
/spike THREAD_ID --timebox 4h
```

**Promover para produção:**
```
/promover THREAD_ID --prioridade 2 --assignee default --skill cn-tech-ecosystem
```

**Arquivar:**
```
/arquivar THREAD_ID --motivo descartada
```

**Resumo diário:**
```
/resumo-incubadora --periodo dia
```

---

## ⚙️ Cron Jobs Configurados

| Job | Schedule | Função |
|-----|----------|--------|
| `incubator-weekly-triage` | Segunda 9h | Triagem automática threads em debate |
| `incubator-daily-summary` | Diário 18h | Resumo postado no canal Home |
| `incubator-daily-reconciliation` | Meia-noite | Sync Forum ↔ Kanban |

Ver/Executar:
```bash
hermes cron list
hermes cron run incubator-weekly-triage
```

---

## 🔗 Integração com Ecossistema CN Tech

| Domínio | Skill Mapeada | Board Kanban |
|---------|---------------|--------------|
| career | `cn-tech-ecosystem` | incubator |
| pim | `cn-tech-ecosystem` | incubator |
| router | `cn-tech-ecosystem` | incubator |
| infra | `cn-tech-ecosystem` | incubator |
| hermes | `hermes-agent` | incubator |
| geral | `system-architect-audit` | incubator |

---

## 📊 Métricas & Monitoramento

```bash
# Ver threads
python3 forum_manager.py list-threads CANAL_ID

# Ver tasks Kanban
hermes kanban list --board incubator
hermes kanban stats

# Reconciliação manual
hermes chat -q "Execute reconciliação Forum Kanban" --skills discord-forum-idea-incubator

# Logs gateway
journalctl -u hermes-gateway -f | grep -i incubator
```

---

## 🔐 Segurança

- Bot token em `~/.hermes/.env` (não commitar)
- Permissões Discord necessárias:
  - Manage Threads
  - Send Messages (em fóruns)
  - Add Reactions
  - Read Message History
  - View Channel (nos fóruns da incubadora)

---

## 📚 Próximos Passos Sugeridos

1. **Executar setup completo:**
   ```bash
   bash ~/.hermes/skills/devops/discord-forum-idea-incubator/scripts/setup_incubator.sh
   ```

2. **Criar webhook Discord → Hermes** para capturar mensagens em tempo real

3. **Configurar notificações Kanban → Discord** (task updates na thread)

4. **Adicionar métricas Prometheus/Grafana** se desejar

5. **Expandir para múltiplos boards** (por domínio/time)

---

## 🐛 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| Thread não criada | Verificar permissão bot no canal + tags existem |
| Tags não aplicadas | Nomes EXATOS no Discord (case-sensitive) |
| Kanban task não criada | `hermes kanban boards list` → verificar board 'incubator' |
| Cron não roda | `hermes cron status` + `journalctl -u hermes-gateway` |
| Voice não transcreve | `hermes config get stt.enabled` deve ser `true` |

---

*Implementado em 2026-06-17 | Hermes Agent + CN Tech Ecosystem*