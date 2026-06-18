# 🎓 Discord Mastery Pack
## Pacote Completo: Setup + Curso + Produção + Manutenção

> **Tudo que você precisa para dominar o Discord Gateway do Hermes Agent** - do básico ao avançado, empacotado como skill reutilizável.

---

## 📦 O Que Inclui

```
discord-mastery-pack/
├── SKILL.md                    # Metadados da skill
├── references/
│   ├── COURSE.md               # 🎓 Curso Completo (9 módulos)
│   ├── ARCHITECTURE.md         # 🏛️ Decisões Arquiteturais
│   ├── essential-crons.yaml    # ⏰ 4 Crons Prontos
│   ├── webhooks.yaml           # 🔗 Webhooks GitHub + Template
│   ├── SOUL-coder.md           # 🤖 Persona Coder
│   ├── SOUL-architect.md       # 🏗️ Persona Architect
│   ├── SOUL-critic.md          # 🔍 Persona Critic
│   └── troubleshooting.md      # 🐛 Guia Problemas/Soluções
├── templates/
│   ├── config.yaml             # Config Hermes Base
│   ├── gateway-config.yaml     # Config Gateway Discord
│   ├── .env.template           # Secrets Template
│   └── hermes-gateway.service  # Systemd Service
├── scripts/
│   ├── QUICKSTART.sh           # ⚡ Setup 1 Comando
│   ├── deploy_mcp.sh           # 🔌 Deploy MCP (Notion, GitHub, Linear, Obsidian)
│   ├── health_check.sh         # 💚 Health Check para Cron
│   └── test_all.sh             # 🧪 Suite Testes Completa
└── assets/
    └── (diagramas, imagens)
```

---

## ⚡ Quickstart

```bash
# 1. Instalar skill
hermes skill install discord-mastery-pack

# 2. Rodar setup completo (interativo)
cd ~/.hermes/skills/devops/discord-mastery-pack
./scripts/QUICKSTART.sh

# 3. Ou usar templates manualmente
cp templates/.env.template ~/.hermes/.env
# Edite ~/.hermes/.env com seus tokens
# systemctl --user restart hermes-gateway
```

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

---

## 📚 Curso Estruturado (references/COURSE.md)

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
- **Crons**: `references/essential-crons.yaml`
- **Webhooks**: `references/webhooks.yaml`
- **Personas**: `references/SOUL-*.md`
- **Troubleshooting**: `references/troubleshooting.md`
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

**Mantido por**: Carlos Alberto Nunes  
**Hermes Agent**: >= 0.16.0  
**Última Atualização**: 2026-06-16