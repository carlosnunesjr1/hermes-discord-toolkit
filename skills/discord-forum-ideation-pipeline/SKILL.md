---
name: discord-forum-ideation-pipeline
category: devops
description: Design, implement, and operate Discord Forum Channels as a structured pre-production ideation/refinement pipeline with automated governance rituals, bidirectional Obsidian sync, and Hermes-as-sparring-partner.
tags: [discord, forum, ideation, pipeline, governance, obsidian, hermes, cn-tech]
version: 1.0
author: Hermes Agent
created: "2026-06-17"
---

# Discord Forum Channels as Structured Ideation/Refinement Pipeline

**Class-level skill** for designing, implementing, and operating Discord Forum Channels as a formal "pre-production laboratory" where ideas are captured, debated, validated, and promoted to production artifacts (GitHub issues, Kanban tasks, specs) — with automated governance rituals.

---

## 🎯 WHEN TO USE

- Team/individual wants a **structured idea funnel** inside Discord (where they already live)
- Need **traceability** from raw idea → spec → production issue → deploy
- Want **automated hygiene** (stale detection, forced decisions, metrics) without manual policing
- Require **bidirectional sync** with a knowledge base (Obsidian, Notion, GitHub Wiki)
- Operating in **zero-budget** constraint: only free-tier tools, open source, self-hosted

---

## 🏗️ CORE ARCHITECTURE

### Taxonomy (3 dimensions, all required on every thread)

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **Domain** (1 required) | `arquitetura`, `ia-agents`, `automação`, `dados`, `negócio`, `produto`, `experimento`, `meta` | Routing, expertise mapping, reporting |
| **Stage** (1 required, mutable) | `semente` → `brotando` → `maduro` → `em-produção` OR `podado` | Enforces forward flow, enables automation |
| **Attributes** (0–N) | `urgente`, `custo-zero`, `segredo`, `precisa-parceiro`, `recorrente` | Filters for rituals, prioritization |

### Four Thread Templates (enforced by bot)

| Template | Stage | Purpose | Key Fields |
|----------|-------|---------|------------|
| **🌱 SEMENTE** | `semente` | Capture raw idea in < 2 min | Contexto, Gatilho, Hipótese central, Próximos passos |
| **🌿 BROTANDO** | `brotando` | Active refinement & research | Problema, Solução, Pesquisa, Perguntas abertas, Validações, Artefatos |
| **🌳 MADURO** | `maduro` | Production-ready spec | Decisão, Spec técnica (MVP + out-of-scope), Arquitetura, Plano de entrega, Linked artifacts, Notas de transição |
| **✂️ PODADO** | `podado` | Archived with lesson | Motivo, Lição aprendida, Condições de revisita |

---

## 🤖 HERMES ROLES IN THE FORUM

| Role | Trigger | Action |
|------|---------|--------|
| **Sparring Partner** | `@Hermes sparring: ...` in `brotando` | Question premises, propose alternatives, estimate effort, flag risks, find prior art |
| **Research Agent** | `@Hermes research: ...` | Web search + browser, synthesize with citations, save to Obsidian |
| **Spec Writer** | Thread tagged `maduro` | Generate full technical spec (Markdown) + create GitHub issue via `gh CLI` |
| **Task Decomposer** | Spec approved | Break into atomic Kanban cards with dependencies |
| **Technical Validator** | Pre-promotion | Run spikes, check API limits, inference costs, compatibility |
| **Memory Keeper** | Continuous | Persist decisions, trade-offs, patterns to `memory` + Obsidian Vault |

---

## ⚙️ AUTOMATED RITUALS (Cron Jobs)

| Ritual | Schedule | Logic |
|--------|----------|-------|
| **Daily Obsidian Sync** | 06:00 daily | Export changed threads → Obsidian by stage; update master index `forum-index.md` |
| **Seed Harvest** | Mon 09:00 | Find `semente` threads inactive > 7d → nudge: promote, prune, or relegate |
| **Active Pruning** | Wed 10:00 | Find `brotando` threads inactive > 14d → demand decision: advance, prune, or demote |
| **Production Promotion** | Fri 16:00 | Find `maduro` threads without GitHub/Kanban link → auto-create issue + Kanban card → tag `em-produção` |
| **Weekly Dashboard** | Sun 20:00 | Compute KPIs (germination, flowering, harvest, conscious prune rates, lead time) + alerts + next-week focus |

---

## 📊 KPIs & TARGETS

| Metric | Formula | Target | Remediation if Missed |
|--------|---------|--------|----------------------|
| **Germination Rate** | `brotando` within 7d of `semente` / total `semente` | ≥ 60% | Tighten seed template (require hypothesis + trigger) |
| **Flowering Rate** | `maduro` within 21d of `brotando` / total `brotando` | ≥ 40% | Improve sparring quality; clarify `maduro` criteria |
| **Harvest Rate** | `em-produção` within 7d of `maduro` / total `maduro` | ≥ 90% | Automate promotion (cron already does this) |
| **Conscious Prune Rate** | `podado` with lesson / total `podado` | 100% | Bot blocks prune without template |
| **Median Lead Time** | Creation → `em-produção` (days) | ≤ 30 | Identify bottleneck stage via weekly dashboard |

---

## 🚫 ANTIPATTERNS & GUARDS

| Antipattern | Symptom | Guard |
|-------------|---------|-------|
| **Seed Graveyard** | Dozens of `semente` > 30d | Weekly harvest cron + 14d max rule |
| **Analysis Paralysis** | `brotando` with 50+ msgs, no decision | 14d timebox → Hermes forces decision |
| **Ghost Spec** | `maduro` > 7d without GitHub link | Friday cron auto-promotes |
| **Silent Prune** | Thread deleted without lesson | Bot requires ✂️ template on prune |
| **Lost Context** | Architectural decision only in Discord | Rule: all arch decisions → Obsidian + memory |

---

## 🔧 IMPLEMENTATION CHECKLIST

### One-time Setup (Discord UI)
- [ ] Create Forum Channel named `insights` (or similar)
- [ ] Configure **Tags** exactly per taxonomy above (Domains + Stages + Attributes)
- [ ] Create **4 Pinned Threads** (one per template) as living references
- [ ] Grant bot permissions: `Manage Threads`, `Send Messages`, `Embed Links`, `Attach Files`, `Use Application Commands`

### Hermes Configuration
- [x] Create 5 cron jobs (prompts in `references/cron-prompts/`) — **DEPLOYED 2026-06-17**
- [x] Verify `gh CLI` authenticated to target repo(s) — **carlosnunesjr1, scopes: gist, read:org, repo**
- [x] Verify Kanban API access (cn-tech-kanban or equivalent) — **via cn-tech-ecosystem**
- [x] Verify Obsidian Vault path mounted (`/opt/obsidian/` or configured) — **accessible**
- [x] **E2E VALIDATION COMPLETE** — Full flow tested: capture → tag brotando → research → debate → tag maduro → spec → tag podado

### Obsidian Vault Structure
```
Vault Brain OS/
├── 00-Inbox/           ← Seeds (auto-synced)
├── 01-Projects/        ← Maduro → spec.md + tasks.md
├── 02-Areas/           ← Domain continuous notes
├── 03-Resources/       ← Research, benchmarks from forum
├── 04-Archive/         ← Podado + lessons
└── 🤖 Hermes/
    ├── forum-index.md  ← Master navigation table
    └── cron-prompts/   ← Cron job prompts (versioned)
```

---

## 🎮 USER COMMANDS (Discord)

| Intent | Command Format |
|--------|----------------|
| New seed | Create thread → paste 🌱 template → tag `semente` + domain |
| Request sparring | `@Hermes sparring: [question OR "analise esta thread"]` |
| Promote to brotando | Edit thread: swap tag `semente`→`brotando`, title prefix `[BROTANDO]` |
| Request research | `@Hermes research: [topic] — salva no Obsidian` |
| Promote to maduro | Tag `maduro` → fill 🌳 template → `@Hermes spec: gera spec + issue GitHub` |
| Prune | Tag `podado` → fill ✂️ template |
| View dashboard | `@Hermes dashboard: insights` |

---

## ✅ VALIDATION RECORD (2026-06-17)

**Full E2E flow tested via Discord commands in forum channel `1516891526540820550` (guild `1516397585701666962`):**

| Step | Command | Result |
|------|---------|--------|
| 1. Capture | `@Hermes capture: teste de validação do fluxo completo` | Thread created with `semente` + `automação` |
| 2. Tag brotando | `@Hermes tag: <id> automação brotando` | Stage transition validated ✓ |
| 3. Research | `@Hermes research: técnicas modernas de cache preditivo...` | Deep research executed, saves to Obsidian |
| 4. Debate | `@Hermes debate: cache preditivo... é a melhor abordagem` | Sparring executed with contra-argumentos |
| 5. Tag maduro | `@Hermes tag: <id> automação maduro` | Stage transition validated ✓ |
| 6. Spec | `@Hermes spec: <id>` | SPEC.md generated + GitHub issue created |
| 7. Prune | `@Hermes tag: <id> podado "teste concluído"` | Archived with lesson template ✓ |

**All 5 cron jobs active and scheduled:**
- `e7286e2a28e9` Daily Obsidian Sync (06:00 daily)
- `27679bfd30d1` Seed Harvest (Mon 09:00)
- `f207f6134302` Active Pruning (Wed 10:00)
- `1785fd1ce49b` Production Promotion (Fri 16:00)
- `d8834049d4e5` Weekly Dashboard (Sun 20:00)

**Manual/Readme pinned:** Thread "📖 MANUAL COMPLETO — #insights" created with full taxonomy, templates, commands, KPIs, rituals.

---

## 📁 SUPPORT FILES

- `references/cron-prompts/seed-harvest.md` — Prompt for Monday harvest cron
- `references/cron-prompts/active-pruning.md` — Prompt for Wednesday pruning cron
- `references/cron-prompts/production-promotion.md` — Prompt for Friday promotion cron
- `references/cron-prompts/weekly-dashboard.md` — Prompt for Sunday dashboard cron
- `references/cron-prompts/daily-obsidian-sync.md` — Prompt for daily sync cron
- `references/deployed-cron-jobs.md` — **Job IDs, schedule, status & prerequisites for 5 active cron jobs** (deployed 2026-06-17)
- `references/discord-config.md` — **Discord IDs, config.yaml snippet, permissions, webhook setup**
- `templates/seed.md` — 🌱 SEMENTE template (copy-paste ready)
- `templates/sprouting.md` — 🌿 BROTANDO template
- `templates/mature.md` — 🌳 MADURO template
- `templates/pruned.md` — ✂️ PODADO template
- `scripts/forum-sync.py` — (Future) Python script for robust Discord→Obsidian sync via API

---

## 🔗 RELATED SKILLS

### Core Pipeline Skills (Local)
- `capture-command` — `@Hermes capture:` cria thread estruturada com tag domínio + semente
- `tag-manager` — `@Hermes tag:` gerencia tags domínio/estágio com validação de transições
- `debate-sparring` — `@Hermes debate:` sparring intelectual rigoroso, contesta premissas
- `research-agent` — `@Hermes research:` investigação profunda web + síntese + Obsidian
- `spec-generator` — `@Hermes spec:` thread maduro → SPEC.md Obsidian + Issue GitHub

### Infrastructure & Operations
- `discord-mastery-pack` — Gateway bot foundation
- `cn-tech-ecosystem-ops` — CN Tech VPS operations context
- `hermes-gateway-ops` — Hermes Gateway configuration
- `obsidian` — Vault operations (second-brain skill)

---

## 📝 CHANGELOG

| Date | Version | Change |
|------|---------|--------|
| 2026-06-17 | 1.1 | E2E validation complete: all commands tested, cron jobs active, GitHub/Obsidian integrated, manual pinned |
| 2026-06-17 | 1.0 | Initial creation from live implementation for CN Tech INSIGHTS forum |

---

## ⚠️ PITFALLS LEARNED

1. **Disk space** — VPS filled to 100% during file write. Always check `df -h` before large writes; clean backups/caches first.
2. **Web search billing** — Nous Firecrawl failed with payment error. Have fallback: use `browser_navigate` to official Discord docs, or rely on internal knowledge for well-established features.
3. **Cron delivery target** — Use `deliver: "origin"` to auto-route back to originating chat/topic. Explicit `discord:chat_id` loses thread context.
4. **Template enforcement** — Bots can't *force* template use on thread create. Solution: pinned reference threads + social convention + prune cron that penalizes non-compliance.
5. **Stage transition ambiguity** — Users forget to update stage tag. Cron jobs must read *current tags*, not assume progression.
6. **Local skills availability** — The 5 pipeline commands (`capture`, `tag`, `debate`, `research`, `spec`) are implemented as separate local skills. They MUST be present in `~/.hermes/skills/local/` and Hermes must reload skills after adding/updating them. Verify with `hermes skills list | grep -E "capture|tag|debate|research|spec"`.
7. **Discord Forum IDs hardcoded** — The `forum_channel_id` (1516891526540820550) and `guild_id` (1516397585701666962) are in `config.yaml`. If forum is recreated, update both config and all cron job prompts that reference the channel.