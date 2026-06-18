# Career Hub Job Funnel Integration for Discord Bot

**Added:** 2026-06-17 | **Context:** Full job funnel implementation connecting Discord ↔ Career Hub (port 2019)

## Overview

Complete job funnel system integrated into the Hermes Discord Bot (`hermes-discord-bot`) that enables:
- Auto-detection of job URLs posted in `#vagas-entrada`
- Automatic thread creation in `#vagas-analise` with full analysis
- AI-powered tier classification, fit scoring, gap analysis
- Action buttons: Save to Career Hub, Apply (move to Applied), Interview Prep, View Kanban, Discard
- Real-time Kanban sync in `#vagas-kanban` channel

## Architecture

### New Discord Category: `🎯 VAGAS & CARREIRA`

| Channel | Purpose |
|---------|---------|
| `#vagas-entrada` | Single entry point — paste job links (LinkedIn, Indeed, Gupy, Catho, etc.) |
| `#vagas-analise` | Auto-threads with analysis results + action buttons |
| `#vagas-kanban` | Live embed synced from Career Hub SQLite (Saved → Applied → Interview → Offer → Rejected) |
| `#vagas-empresas` | Company dossiers (culture, tech stack, Glassdoor) |
| `#vagas-contexto` | User professional profile (skills, seniority, preferences, salary range) |

### Auto-Thread Flow

```
User posts URL in #vagas-entrada
        │
        ▼
Bot detects job URL via regex (linkedin.com/jobs, indeed.com, gupy.io, catho.com.br, infojobs.com.br, vagas.com.br, trampos.co, programathor.com.br, getonbrd.com, glassdoor.com, github.com/careers, wellfound.com, remotar.com.br, workana.com, 99jobs.com, empregos.com.br, job.kenoby.com, kenoby.com, jobs.lever.co, greenhouse.io, comeet.com, breezy.hr)
        │
        ▼
Creates thread in #vagas-analise: "🔗 [User] - [URL]"
        │
        ▼
Runs analysis pipeline via CareerHubClient:
  ├─ extract_job_urls() → URL extraction
  ├─ classify_job_tier() → Tier 1/2/3 based on keywords
  ├─ detect_modality() → remoto/hibrido/presencial
  ├─ extract_salary() → salary parsing
  ├─ analyze_job_posting() → full analysis with user profile
        │
        ▼
Posts analysis embed + JobActionView buttons
```

## CareerHubClient (`career_hub_client.py`)

Async client for Career Hub API (port 2019):

```python
# Core methods
fetch_diario_regiao(keywords: List[str]) → 50 jobs from Diário da Região
list_jobs() → all saved jobs
save_job(job_data) → POST /api/jobs
update_job_status(job_id, status) → PATCH /api/job/:id (saved/applied/interview/offer/rejected)
delete_job(job_id)
get_profile() / save_profile(profile_data)
analyze_cv(cv_data) → requires LLM Router keys
generate_interview_prep(job_data, cv_data) → requires LLM Router keys
generate_career_plan(profile_data, goals) → requires LLM Router keys
```

### Job Analysis Pipeline

```python
analysis = {
    "extracted": {title, company, location, modality, salary, description, requirements},
    "classification": {"tier": 1|2|3, "reason": "..."},
    "fit_analysis": {
        "score": 0-100,
        "matching_skills": [],
        "gaps": [],
        "salary_fit": "match|mismatch|unknown",
        "location_fit": "match|mismatch|unknown"
    },
    "recommendation": {
        "action": "APPLY_NOW|PREPARE_THEN_APPLY|APPLY_THIS_WEEK|SAVE_AS_BACKUP",
        "priority": "high|medium|low",
        "cover_letter_points": []
    }
}
```

### Tier Classification Keywords

- **Tier 1 (Apply Today):** tech lead, staff, principal, architect, engineering manager, cto, vp engineering, director, head of, sênior, senior, fullstack, backend, frontend, devops, sre, platform engineer, data engineer, ml engineer, ai engineer, cloud engineer, kubernetes, aws, azure, gcp, terraform, react, node, python, go, golang, java, kotlin, typescript, rust, microservices, distributed systems
- **Tier 2 (This Week):** analista, coordinator, lead, gerente de projeto, project manager, product manager, scrum master, agile coach, qa, test engineer, automation, devops jr, jr backend, jr frontend, estágio, intern, trainee, júnior, junior
- **Tier 3 (Backup):** suporte, support, help desk, service desk, atendimento, vendas, sales, sdr, bdr, account executive, operacional, logística, administrativo, auxiliar, assistant

## Discord UI Components

### JobActionView (`bot.py`)

Buttons attached to each job analysis thread:
- `✅ Salvar no Career Hub` → `save_job()` with status="saved"
- `📝 Candidatar (Mover p/ Applied)` → `save_job()` with status="applied"
- `🎤 Preparar Entrevista (IA)` → `generate_interview_prep()` via LLM Router
- `📊 Ver Kanban` → fetches and displays Career Hub jobs grouped by status
- `🗑️ Descartar` → archives thread

Auto-refreshes `#vagas-kanban` embed after each action.

### SystemSelectView Integration

Added "🎯 VAGAS — Funil de Carreira" select menu:
- `📰 Buscar Diário da Região` → calls `fetch_diario_regiao([])`
- `📋 Ver Kanban` → displays Career Hub Kanban
- `➕ Adicionar Vaga Manual` → shows `/vaga adicionar` hint
- `🔍 Analisar Link de Vaga` → explains auto-thread flow
- `👤 Atualizar Meu Perfil` → shows `/vaga perfil` hint

## Slash Commands (`/vaga` command group)

```python
/vaga analisar <url>           # Analyze job URL (or last in #vagas-entrada)
/vaga kanban                   # Show synced Kanban embed
/vaga adicionar empresa: titulo: local: modalidade: salario: link: descricao: requisitos:
/vaga perfil                   # Show/update Career Hub profile
/vaga buscar-diario            # Fetch 50 jobs from Diário da Região
```

## Auto-Provisioning

Added to `AUTO_PROVISION_STRUCTURE` in `bot.py`:

```python
"🎯 VAGAS & CARREIRA": {
    "vagas-entrada": "📥 Entrada de Vagas (cole links aqui)",
    "vagas-analise": "🔍 Análise Automática de Vagas",
    "vagas-kanban": "📋 Kanban Sincronizado (Career Hub)",
    "vagas-empresas": "🏢 Dossiês de Empresas",
    "vagas-contexto": "👤 Seu Perfil Profissional",
}
```

Channels auto-created on first bot startup with system panels posted.

## Configuration

### Environment Variables (`.env`)

```bash
# Auto-threading triggers extended for job URLs
AUTO_THREAD_TRIGGERS=@Hermes,/hermes,hermes ,oi hermes,hermes bot,vaga,linkedin,indeed,gupy,catho
```

### Career Hub API Endpoint

Configured in `CareerHubClient.__init__()`:
```python
base_url = "http://localhost:2019"  # Career Hub v1 (production)
```

## Dependencies

- `discord.py>=2.3.0`
- `aiohttp>=3.9.0`
- `python-dotenv>=1.0.0`

## Integration Points

### Career Hub (port 2019)
- SQLite + better-sqlite3 (WAL mode)
- Tables: `job_applications` (empresa, titulo, local, modalidade, salario, link, descricao, requisitos, beneficios, email, telefone, senioridade, source, regiao, status)
- API: GET/POST/PATCH/DELETE `/api/jobs`, POST `/api/fetch-diario-regiao`

### Hermes Gateway (port 8642)
- LLM Router for interview prep generation (`POST /api/interview-generate`)
- Brain sync for profile context
- Webhook delivery for notifications

### LLM Router (port 8799)
- Required for AI features: CV analysis, interview prep, career plan
- Config: `/home/carlos/.hermes/cn-tech/infra/router/config/llm-router.json`
- Placeholder keys block AI features until replaced with real OpenRouter key

## Deployment

```bash
cd /home/carlos/hermes-discord-bot
cp .env.template .env
# Edit .env with DISCORD_BOT_TOKEN, DISCORD_APP_ID, DISCORD_GUILD_ID
./deploy.sh install
./deploy.sh start
```

Systemd service: `hermes-discord-bot.service` (hardened, watchdog enabled)

## Testing Checklist

- [ ] Post job link in `#vagas-entrada` → thread created in `#vagas-analise`
- [ ] Analysis embed shows tier, fit score, gaps, recommendation
- [ ] `✅ Salvar` → job appears in Career Hub `/api/jobs`
- [ ] `📝 Candidatar` → job status changes to "applied" in Kanban
- [ ] `🎤 Preparar Entrevista` → calls LLM Router (requires keys)
- [ ] `📊 Ver Kanban` → shows all jobs grouped by status
- [ ] `#vagas-kanban` embed updates in real-time
- [ ] `/vaga kanban` command works
- [ ] `/vaga buscar-diario` returns 50 jobs
- [ ] `/vaga adicionar` modal saves to Career Hub

## Known Limitations

1. **Job extraction from URL** — Currently uses placeholder data; needs scraper or API integration for real extraction
2. **LLM Router keys** — AI features (interview prep, CV analysis, career plan) blocked until real OpenRouter key configured
3. **Duplicate detection** — No auto-dedup on save (same job fetched twice = two entries)
4. **User profile storage** — Currently reads from Career Hub profile; could extend with per-Discord-user profiles

## Files Created/Modified

```
/home/carlos/hermes-discord-bot/
├── bot.py                          # Added JobActionView, SystemSelectView "VAGAS" menu, _handle_job_link, _post_job_analysis, /vaga commands
├── career_hub_client.py            # NEW: CareerHubClient + job analysis pipeline
├── config.py                       # Added auto_thread_default_channels includes #vagas-* channels
├── gateway_client.py               # Existing: Gateway API client
├── thread_manager.py               # Existing: Thread ↔ Session mapping
├── resilience.py                   # Existing: Circuit breakers, queue, health checks
├── requirements.txt                # Dependencies
├── .env.template                   # Template with DISCORD_* vars
├── deploy.sh                       # Deploy script
└── service/hermes-discord-bot.service  # Systemd unit
```