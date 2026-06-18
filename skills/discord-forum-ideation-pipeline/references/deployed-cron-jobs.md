# Cron Jobs Implantados — INSIGHTS Forum Pipeline

**Data dedeploy:** 2026-06-17  
**Ambiente:** Hermes Agent (prod profile)  
**Canal Forum Discord:** `1516891526540820550` (insights)  
**Guild Discord:** `1516397585701666962`

---

## Job IDs Ativos

| Ritual | Job ID | Agenda | Próxima Execução | Status |
|--------|--------|--------|------------------|--------|
| Daily Obsidian Sync | `e7286e2a28e9` | 0 6 * * * (diário 06:00) | 2026-06-18T06:00:00-03:00 | ✅ Agendado |
| Seed Harvest (Seg) | `27679bfd30d1` | 0 9 * * 1 (seg 09:00) | 2026-06-22T09:00:00-03:00 | ✅ Agendado |
| Active Pruning (Qua) | `f207f6134302` | 0 10 * * 3 (qua 10:00) | 2026-06-24T10:00:00-03:00 | ✅ Agendado |
| Production Promotion (Sex) | `1785fd1ce49b` | 0 16 * * 5 (sex 16:00) | 2026-06-19T16:00:00-03:00 | ✅ Agendado |
| Weekly Dashboard (Dom) | `d8834049d4e5` | 0 20 * * 0 (dom 20:00) | 2026-06-21T20:00:00-03:00 | ✅ Agendado |

---

## Configuração Comum

- **Skill anexada:** `discord-forum-ideation-pipeline`
- **Delivery:** `origin` (retorna ao chat/tópico de origem)
- **Repeat:** `forever`
- **Model/Provider:** Default (nemotron-3-ultra:free via Nous)

---

## Prompts Utilizados

Cada job usa o prompt correspondente em `references/cron-prompts/`:
- `daily-obsidian-sync.md` → Job `e7286e2a28e9`
- `seed-harvest.md` → Job `27679bfd30d1`
- `active-pruning.md` → Job `f207f6134302`
- `production-promotion.md` → Job `1785fd1ce49b`
- `weekly-dashboard.md` → Job `d8834049d4e5`

---

## Pré-requisitos Pendentes (para Produção Promotion funcionar)

1. **GitHub CLI autenticado** — `gh auth login` no ambiente do cron
2. **Repo CN Tech acessível** — Permissão de criar issues no org/repo alvo
3. **Kanban API** — `cn-tech-kanban` ou equivalente acessível
4. **Obsidian Vault** — Caminho `/opt/obsidian/` montado e gravável

---

## Comandos de Gestão

```bash
# Listar jobs
hermes cron list

# Executar job manualmente (teste)
hermes cron run <job_id>

# Pausar/Remover
hermes cron pause <job_id>
hermes cron remove <job_id>

# Ver output do último run (após execução)
hermes cron log <job_id>
```

---

## Notas de Implementação

- Jobs duplicados antigos (`db8e24fe58cb`, `0b4fcce05fcc`, `39b153bf0610`, `49974a7ef420`, `7d3f2706d5c8`) foram **removidos** — usavam skill genérica `discord` em vez da skill específica `discord-forum-ideation-pipeline`
- Nova versão usa a skill class-level correta com prompts versionados em `references/cron-prompts/`
- Delivery `origin` preserva contexto de thread/canal — crítico para respostas no fórum correto