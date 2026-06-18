# Discord Configuration for INSIGHTS Forum Pipeline

## IDs (Production - CN Tech Discord)

| Item | Value |
|------|-------|
| **Forum Channel ID** | `1516891526540820550` |
| **Guild/Server ID** | `1516397585701666962` |
| **Free Response Channel** | `1516397585701666962` |

## config.yaml Snippet

```yaml
discord:
  require_mention: true
  free_response_channels: "1516397585701666962"
  allowed_channels: ""
  auto_thread: true
  thread_require_mention: false
  history_backfill: true
  history_backfill_limit: 50
  reactions: true
  channel_prompts: {}
  dm_role_auth_guild: ""
  server_actions: ""
  allow_any_attachment: false
  max_attachment_bytes: 33554432
  forum_channel_id: "1516891526540820550"
  guild_id: "1516397585701666962"
```

## Required Bot Permissions

- `Manage Threads`
- `Send Messages`
- `Embed Links`
- `Attach Files`
- `Use Application Commands`
- `Read Message History`
- `View Channel`

## Tag Setup (Discord UI)

Create these tags in the Forum Channel settings:

### Domain Tags (exactly 1 required)
- `arquitetura` 🏗️
- `ia-agents` 🤖
- `automação` 🔧
- `dados` 📊
- `negócio` 💰
- `produto` 🎨
- `experimento` 🧪
- `meta` 🧠

### Stage Tags (exactly 1 required, mutable)
- `semente` 🌱
- `brotando` 🌿
- `maduro` 🌳
- `podado` ✂️
- `em-produção` 🚀

### Attribute Tags (0-N optional)
- `urgente` 🔥
- `custo-zero` 💚
- `segredo` 🔒
- `precisa-parceiro` 🤝
- `recorrente` 🔄

## Pinned Reference Threads

Create 4 pinned threads (one per template):
1. `📖 MANUAL COMPLETO — #insights` — This document + all templates
2. `🌱 TEMPLATE SEMENTE` — Copy-paste template for new ideas
3. `🌿 TEMPLATE BROTANDO` — Copy-paste for active refinement
4. `🌳 TEMPLATE MADURO` — Copy-paste for production-ready specs
5. `✂️ TEMPLATE PODADO` — Copy-paste for archiving with lessons

## Cron Job References

All 5 cron jobs use `skill: discord-forum-ideation-pipeline` and `deliver: "origin"`:

| Job ID | Name | Schedule | Prompt File |
|--------|------|----------|-------------|
| `e7286e2a28e9` | Daily Obsidian Sync | `0 6 * * *` | `references/cron-prompts/daily-obsidian-sync.md` |
| `27679bfd30d1` | Seed Harvest | `0 9 * * 1` | `references/cron-prompts/seed-harvest.md` |
| `f207f6134302` | Active Pruning | `0 10 * * 3` | `references/cron-prompts/active-pruning.md` |
| `1785fd1ce49b` | Production Promotion | `0 16 * * 5` | `references/cron-prompts/production-promotion.md` |
| `d8834049d4e5` | Weekly Dashboard | `0 20 * * 0` | `references/cron-prompts/weekly-dashboard.md` |

## Validation Test (2026-06-17)

Test thread created: `@Hermes capture: teste de validação do fluxo completo`
- Tags applied: `automação` + `semente`
- Full flow: capture → tag brotando → research → debate → tag maduro → spec → tag podado
- All commands executed successfully
- GitHub issue created via spec-generator
- Research saved to Obsidian