---
name: discord-forum-idea-incubator
title: Discord Forum Idea Incubator
description: Use Discord forum channels as an idea incubation environment — capture, debate, refine ideas before promoting to production via Kanban/Hermes. Integrated with CN Tech ecosystem.
version: 1.0.0
tags: [discord, forum, idea-incubation, kanban, hermes, cn-tech]
---

# Discord Forum Idea Incubator

Transforma canais de fórum do Discord em um **ambiente de incubação de ideias** — da captura casual (voz/texto andando, em casa) até promoção controlada para produção via Kanban + Hermes.

## Arquitetura Conceitual

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISCORD FORUM (INCUBATOR)                    │
├─────────────────────────────────────────────────────────────────┤
│  📥 CAPTURA          🗣️ DEBATE           ✅ TRIAGEM             │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐             │
│  │ Voice   │───────▶│ Thread  │───────▶│ Tags +  │             │
│  │ / Text  │        │ Discuss │        │ Priority│             │
│  └─────────┘        └─────────┘        └────┬────┘             │
│                                              │                  │
└──────────────────────────────────────────────│──────────────────┘
                                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROMOÇÃO PARA PRODUÇÃO                        │
├─────────────────────────────────────────────────────────────────┤
│  🚀 HERMES KANBAN                                                │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │ Kanban  │───▶│ Worker  │───▶│ Verifier│───▶│ Deploy  │      │
│  │ Task    │    │ (Agent) │    │         │    │ (CI/CD) │      │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Estrutura do Fórum Discord

### Canais de Fórum Recomendados

```
📁 INCUBADORA (Category)
├── 💡 #ideias-brutas          # Captura inicial (voice/text livre)
├── 🔬 #em-análise             # Ideias promovidas para debate estruturado
├── ⚗️ #experimentos           # PoCs, spikes, validações técnicas
├── ✅ #prontas-para-produção  # Aprovadas, aguardando promoção Kanban
├── 📦 #arquivadas             # Decididas (feitas, descartadas, depois)
└── 🗂️ #templates              # Templates de thread para padronização
```

### Tags Obrigatórias por Thread

| Tag | Valores | Obrigatória |
|-----|---------|-------------|
| `status` | `capturada`, `em-debate`, `validando`, `aprovada`, `arquivada` | ✅ |
| `prioridade` | `P1-urgente`, `P2-alta`, `P3-normal`, `P4-baixa`, `P5-backlog` | ✅ |
| `tipo` | `feature`, `bug`, `tech-debt`, `pesquisa`, `processo`, `infra` | ✅ |
| `esforço` | `XS`, `S`, `M`, `L`, `XL`, `desconhecido` | ❌ |
| `domínio` | `career`, `pim`, `router`, `infra`, `hermes`, `geral` | ❌ |

## Fluxo de Trabalho Completo

### 1️⃣ CAPTURA (Qualquer momento, qualquer lugar)

**Via Discord Mobile/Desktop:**
- Grava áudio no canal `#ideias-brutas` → Hermes transcreve + cria thread automaticamente
- Digita texto direto → Hermes cria thread com template
- Reage com 🎯 em qualquer mensagem → Hermes converte em thread de ideia

**Comando Slash (no fórum):**
```
/ideia "Título rápido" --tipo feature --prioridade P3 --domínio career
```

**Automação via Hermes Gateway:**
- Voice messages → STT → Thread creation com metadata
- Text messages com prefixo `!ideia` → Thread creation
- Reactions 🎯/💡/🚀 em mensagens soltas → Thread creation

### 2️⃣ DEBATE ESTRUTURADO (Thread ativa)

**Estrutura padrão da thread (template):**

```markdown
## 💡 Ideia: [Título]

### Contexto
> O que motivou? Qual problema resolve?

### Hipótese de Valor
> Se fizermos X, então Y acontece porque Z.

### Critérios de Sucesso
- [ ] Critério mensurável 1
- [ ] Critério mensurável 2

### Riscos Conhecidos
- Risco 1: Mitigação
- Risco 2: Mitigação

### Dependências
- Sistema X, API Y, decisão Z

### Estimativa Rápida
- Esforço: [XS/S/M/L/XL]
- Complexidade técnica: [Baixa/Média/Alta]
- Tempo para MVP: [dias/semanas]

---

### 💬 Discussão
<!---thread-messages-->

### ✅ Decisão
- **Status:** [em-debate | validando | aprovada | arquivada]
- **Decisor:** @usuario
- **Data:** YYYY-MM-DD
- **Próximo passo:** [promover Kanban | spike técnico | descartar]
```

**Dinâmica de debate:**
- Reações 👍/👎 em argumentos → contagem visual de consenso
- Threads de sub-discussão via `🧵` reply para não poluir principal
- Polls nativos do Discord para decisões binárias
- Menção `@Hermes` para análises técnicas automáticas

### 3️⃣ TRIAGEM E PRIORIZAÇÃO (Semanal/Quinzenal)

**Ritual de triagem (pode ser cron job Hermes):**
1. Bot posta resumo semanal no `#geral` ou DM
2. Usuário reage/vota nas threads do `#em-análise`
3. Hermes atualiza tags `prioridade` e `status` baseado em critérios:
   - `P1` = alinhado a OKR atual + esforço ≤ M + dependências resolvidas
   - `P2` = alinhado a OKR + esforço L/XL ou 1 dependência
   - `P3` = não-OKR mas alto valor/baixo esforço
   - `P4` = nice-to-have, backlog
   - `P5` = estacionado (aguarda decisão externa)

### 4️⃣ VALIDAÇÃO TÉCNICA (Spikes/PoCs)

Para ideias `aprovadas` com `esforço ≥ M` ou `complexidade = Alta`:

```
#experimentos  (canal de fórum)
├── Thread: "Spike: [Título da ideia]"
│   ├── Objetivo técnico claro
│   ├── Critérios de validação (pass/fail)
│   ├── Timebox: [2h | 4h | 1d | 2d]
│   └── Resultado: ✅ Viável / ❌ Inviável / ⚠️ Parcial
```

**Automação:**
- Hermes cria task Kanban `spike` automaticamente ao mover para `#experimentos`
- Worker executa spike, posta resultado na thread
- Verificador valida critérios
- Decisão: promover → `#prontas-para-produção` ou arquivar

### 5️⃣ PROMOÇÃO PARA PRODUÇÃO (Kanban)

**Comando de promoção:**
```
/promover [thread_id] --prioridade P2 --assignee default --skill cn-tech-ecosystem
```

**O que acontece:**
1. Hermes lê thread, extrai: título, descrição, critérios, esforço, domínio
2. Cria task Kanban com:
   - `title`: da thread
   - `body`: template estruturado (contexto + critérios + riscos)
   - `priority`: da tag
   - `assignee`: profile alvo
   - `skill`: domínio mapeado (career, pim, router, infra, hermes)
   - `parent`: link para thread Discord (metadata)
3. Posta confirmação na thread com link Kanban
4. Move thread para `#prontas-para-produção` com tag `status=aprovada`

### 6️⃣ EXECUÇÃO E FEEDBACK LOOP

```
Kanban Task (running)
    │
    ▼
Worker Agent executa
    │
    ▼
Atualiza thread Discord com progresso (webhook/hermes message)
    │
    ▼
Concluído → Verificador valida → Deploy
    │
    ▼
Thread movida para #arquivadas com tag `status=feita`
    Link para PR/Deploy na thread
```

## Integração Técnica

### Componentes Necessários

| Componente | Responsabilidade | Status |
|------------|------------------|--------|
| **Discord Gateway** | Recebe voice/text, events | ✅ Existente |
| **STT (faster-whisper)** | Voice → Text | ✅ Configurado |
| **Forum Manager Skill** | Thread CRUD, tags, templates | 🔧 A criar |
| **Idea Processor** | Parse, structure, triage | 🔧 A criar |
| **Kanban Bridge** | Thread → Kanban task | ✅ Parcial (kanban CLI) |
| **Cron Jobs** | Triagem semanal, resumos | 🔧 A criar |
| **Webhook/Notifier** | Kanban → Discord updates | 🔧 A criar |

### Configuração Hermes (config.yaml)

```yaml
# Discord Forum Incubator
discord:
  forum_incubator:
    enabled: true
    category_id: "123456789012345678"  # Category "INCUBADORA"
    channels:
      raw: "ideias-brutas"           # Forum channel ID
      analysis: "em-analise"
      experiments: "experimentos"
      ready: "prontas-para-producao"
      archive: "arquivadas"
      templates: "templates"
    tags:
      status: ["capturada", "em-debate", "validando", "aprovada", "arquivada", "feita"]
      prioridade: ["P1-urgente", "P2-alta", "P3-normal", "P4-baixa", "P5-backlog"]
      tipo: ["feature", "bug", "tech-debt", "pesquisa", "processo", "infra"]
      esforco: ["XS", "S", "M", "L", "XL", "desconhecido"]
      dominio: ["career", "pim", "router", "infra", "hermes", "geral"]
    auto_thread_from_voice: true
    auto_thread_from_reaction: ["🎯", "💡", "🚀"]
    idea_prefix: "!ideia"
    
# Kanban Integration
kanban:
  boards:
    incubator:
      name: "incubator"
      auto_create_from_forum: true
      default_assignee: "default"
      skill_mapping:
        career: "cn-tech-ecosystem"
        pim: "cn-tech-ecosystem"
        router: "cn-tech-ecosystem"
        infra: "cn-tech-ecosystem"
        hermes: "hermes-agent"
        geral: "system-architect-audit"

# Cron Jobs
cron:
  jobs:
    - name: "incubator-weekly-triage"
      schedule: "0 9 * * 1"  # Segunda 9h
      prompt: "Execute triagem semanal da incubadora: liste threads em 'em-debate', aplique critérios de prioridade, atualize tags, poste resumo no canal geral."
      skills: ["discord-forum-idea-incubator"]
      
    - name: "incubator-daily-summary"
      schedule: "0 18 * * *"  # Diário 18h
      prompt: "Resumo diário: novas ideias capturadas, threads movidas, spikes concluídos, tarefas Kanban criadas."
      skills: ["discord-forum-idea-incubator"]
```

### Slash Commands (Discord)

| Comando | Descrição |
|---------|-----------|
| `/ideia "titulo" --tipo feature --prio P3 --dominio career` | Cria thread estruturada |
| `/triagem [thread_id] --status em-debate --prio P2` | Atualiza tags manualmente |
| `/spike [thread_id] --timebox 4h` | Cria task Kanban spike + move para #experimentos |
| `/promover [thread_id] --prio P2 --assignee default` | Promove para Kanban produção |
| `/arquivar [thread_id] --motivo "feita|descartada|depois"` | Arquiva com motivo |
| `/resumo-incubadora --periodo semana` | Gera relatório da incubadora |

## Templates de Thread (em `#templates`)

### Template: Feature/Produto
```markdown
# Template: Nova Feature

## Problema
Qual dor do usuário/cliente?

## Solução Proposta
Descrição da feature.

## Critérios de Aceite
- [ ] Critério 1
- [ ] Critério 2

## Métricas de Sucesso
- Métrica 1: target
- Métrica 2: target

## Riscos
- Técnico:
- Negócio:
- Dependências:
```

### Template: Tech Debt/Refatoração
```markdown
# Template: Tech Debt

## O que está errado
Descrição técnica.

## Impacto Atual
- Performance:
- Manutenibilidade:
- Bugs recorrentes:

## Solução Proposta
Abordagem + arquitetura.

## Escopo
- Arquivos/módulos afetados:
- Testes necessários:
- Migration strategy:

## Esforço Estimado
[S/M/L/XL]
```

### Template: Pesquisa/Spike
```markdown
# Template: Spike/Pesquisa

## Pergunta Técnica
O que precisamos validar?

## Hipótese
Acreditamos que X porque Y.

## Critérios de Validação (Pass/Fail)
- [ ] Critério técnico 1
- [ ] Critério técnico 2

## Timebox
[2h/4h/1d/2d]

## Recursos
- Docs:
- Código existente:
- Pessoas:
```

## Métricas da Incubadora

| Métrica | Target | Fonte |
|---------|--------|-------|
| Tempo captura → thread | < 30s | Gateway logs |
| Tempo thread → debate ativo | < 24h | Discord analytics |
| Taxa promoção (aprovada → Kanban) | > 30% | Kanban + Forum sync |
| Tempo triangulação (spike) | < timebox | Kanban task duration |
| Ideias arquivadas "depois" | < 20% | Tag analysis |
| Satisfação (reação 👍 final) | > 80% | Discord reactions |

## Pitfalls Conhecidos e Mitigações

| Pitfall | Sintoma | Mitigação |
|---------|---------|-----------|
| **Thread sprawl** | Muitas threads paralelas, perda de foco | WIP limit por canal (max 10 ativas em `#em-análise`) |
| **Voice noise** | Áudios longos, sem foco, criam threads ruins | STT + LLM summary obrigatório antes de criar thread; min 10s, max 3min |
| **Decision paralysis** | Debate infinito sem decisão | Timebox de debate (7 dias auto-arquiva se sem movimento), poll obrigatório |
| **Kanban sync drift** | Thread promoted mas task não criada / vice-versa | Reconciliação cron diária + webhook bidirecional |
| **Context loss** | Thread movida, histórico perdida | Nunca delete threads; arquivo com tags + link Kanban preservado |
| **Tag inconsistency** | Tags manuais inconsistentes | Automação Hermes força tags válidas; `/triagem` valida |

## Próximos Passos de Implementação

1. **Criar skill `discord-forum-idea-incubator`** (este arquivo) ✅
2. **Criar script Python: `forum_manager.py`** - Thread CRUD, tags, templates via Discord API
3. **Criar script Python: `idea_processor.py`** - Parse voice/text → structured thread
4. **Criar script Python: `kanban_bridge.py`** - Thread ↔ Kanban sync bidirecional
5. **Configurar cron jobs** no Hermes (`hermes cron create`)
6. **Testar E2E**: Voice → Thread → Debate → Spike → Kanban → Deploy
7. **Documentar runbook** operacional

## Comandos de Teste Rápido

```bash
# 1. Verificar canais de fórum disponíveis
hermes chat -q "Liste canais de fórum do Discord conectados" --toolsets discord

# 2. Criar thread de teste manual
hermes chat -q "Crie thread no fórum 'ideias-brutas': 'Teste incubadora: automação deploy'" --toolsets discord

# 3. Testar promoção Kanban
hermes kanban create "Teste da incubadora" --body "Vindo do forum Discord" --priority 2 --triage

# 4. Verificar cron jobs
hermes cron list
```

## Referências

- Discord Forum Channels API: https://discord.com/developers/docs/resources/channel#forum-channels
- Hermes Gateway Discord: `skill_view("hermes-agent", "references/gateway-troubleshooting.md")`
- Kanban Swarm Delegation: `skill_view("productivity/kanban-swarm-delegation")`
- CN Tech Ecosystem: `skill_view("devops/cn-tech-ecosystem")`
- Hermes Cron Jobs: `hermes cron --help`