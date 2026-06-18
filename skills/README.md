# Skills

Hermes Agent skills for Discord integration. Each skill is self-contained with its own `SKILL.md`, scripts, templates, and references.

## Available Skills

| Skill | Description | Category |
|-------|-------------|----------|
| `discord-gateway-bot` | Standalone Discord Gateway WebSocket bot with Hermes integration — slash commands, thread management, auto-provisioning, background automation, voice, UI components | Core |
| `discord-forum-idea-incubator` | Discord forum channels as idea incubation environment — capture, debate, refine ideas before promoting to production via Kanban/Hermes | Ideation |
| `discord-forum-ideation-pipeline` | Automated pipeline from forum threads → structured ideas → Kanban tasks → Hermes execution | Pipeline |
| `discord-mastery-pack` | Complete Discord Gateway package — basic to advanced. Setup 24/7, voice, crons, webhooks, multi-agent, MCP, launchpad. Skill + course + daily workflow | Mastery |

---

## Installation

### Via Hermes CLI (recommended)

```bash
# Install individual skill
hermes skills install ./skills/discord-gateway-bot --name discord-gateway-bot

# Or from GitHub (after publishing)
hermes skills install https://github.com/carlosnunesjr1/hermes-discord-toolkit/raw/main/skills/discord-gateway-bot/SKILL.md
```

### Manual (development)

```bash
# Symlink to Hermes skills directory
ln -s /path/to/hermes-discord-toolkit/skills/discord-gateway-bot ~/.hermes/skills/discord-gateway-bot
hermes skills list | grep discord
```

---

## Skill Details

### discord-gateway-bot

**Core bot implementation** — Standalone process connecting via Discord Gateway WS and Hermes Gateway HTTP.

**Features:**
- Slash commands (`/chat`, `/skill`, `/deploy`, `/status`, etc.)
- Thread management (auto-create, archive, cleanup)
- Auto-provisioning (new user → DM → guided setup)
- Background automation (cron jobs, scheduled tasks)
- Voice support (jarvis mode, podcast mode)
- UI components (buttons, selects, modals)
- Webhook outbound (Discord → Hermes → Discord)
- Resilience layer (reconnection, rate limit handling)
- Image/file handling

**References:** 15+ docs in `references/` covering architecture, troubleshooting, voice, webhooks, etc.

**Templates:** systemd service, deploy script

---

### discord-forum-idea-incubator

**Idea incubator** — Uses Discord forum channels as structured ideation space.

**Flow:**
1. User creates thread in forum channel
2. Bot adds tags, assigns reviewers
3. Discussion happens in thread
4. `/incubate promote` → moves to Kanban as task
5. Hermes executes via Kanban dispatcher

**Scripts:**
- `orchestrator.py` — Main loop
- `forum_manager.py` — Forum API operations
- `idea_processor.py` — Thread → idea conversion
- `kanban_bridge.py` — Kanban integration
- `setup_incubator.sh` — One-time setup

---

### discord-forum-ideation-pipeline

**Automated pipeline** — Forum threads → structured ideas → Kanban → Hermes execution.

**Stages:**
1. **Capture** — New thread detected
2. **Enrich** — AI extracts key info, tags
3. **Validate** — Reviewers approve/reject
4. **Promote** → Kanban task with spec
5. **Execute** — Hermes dispatcher picks up

---

### discord-mastery-pack

**Mastery package** — Complete learning + implementation path.

**Contents:**
- `references/COURSE.md` — Full course curriculum
- `references/DAILY_WORKFLOW.md` — Daily operations
- `references/SOUL-*.md` — Persona definitions (architect, coder, critic)
- `references/essential-crons.yaml` — Production cron definitions
- `references/webhooks.yaml` — Webhook configs
- `scripts/QUICKSTART.sh` — One-command setup
- `scripts/deploy_mcp.sh` — MCP server deployment
- `scripts/health_check.sh` — System health verification
- `scripts/test_all.sh` — Full test suite
- `templates/` — Config, systemd, deploy, requirements

**Use case:** Teams wanting complete Discord + Hermes mastery with documented workflows.

---

## Quick Start (All Skills)

```bash
# 1. Configure toolkit
cd hermes-discord-toolkit
./scripts/setup.sh

# 2. Render templates
./scripts/render-templates.sh

# 3. Deploy infrastructure
./scripts/deploy.sh

# 4. Install skills on VPS (as deploy user)
hermes skills install ./skills/discord-gateway-bot --name discord-gateway-bot
hermes skills install ./skills/discord-forum-idea-incubator --name discord-forum-idea-incubator
hermes skills install ./skills/discord-mastery-pack --name discord-mastery-pack

# 5. Run quickstart (mastery pack)
~/hermes-discord-toolkit/skills/discord-mastery-pack/scripts/QUICKSTART.sh
```

---

## Dependencies

| Skill | Requires |
|-------|----------|
| `discord-gateway-bot` | Hermes Gateway running, Discord bot token |
| `discord-forum-idea-incubator` | `discord-gateway-bot`, Kanban board |
| `discord-forum-ideation-pipeline` | `discord-forum-idea-incubator`, Hermes Kanban |
| `discord-mastery-pack` | All above + MCP servers (optional) |

---

## Development

```bash
# Test skill locally
cd skills/discord-gateway-bot
python3 -m pytest scripts/test.py -v

# Validate SKILL.md frontmatter
python3 -c "import yaml; yaml.safe_load(open('SKILL.md'))"

# Check references
ls references/
```