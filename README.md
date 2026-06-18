# hermes-discord-toolkit

Toolkit for running Discord bots on Hermes Agent. Skills, templates, and deployment scripts for self-hosted setups.

## What's inside

- **skills/** — Hermes skills (gateway bot, forum incubator, mastery pack)
- **templates/** — Systemd, Caddy, .env templates with placeholders
- **scripts/** — Setup, render, deploy automation
- **examples/** — Minimal working bots

## Quick start

```bash
git clone https://github.com/carlosnunesjr1/hermes-discord-toolkit
cd hermes-discord-toolkit
./scripts/setup.sh          # creates ~/.config/hermes-discord-toolkit/.env.local
./scripts/render-templates.sh
./scripts/deploy.sh
```

## Requirements

- Linux VPS (Ubuntu 24.04 tested)
- Hermes Agent gateway running
- Domain with Cloudflare (auto SSL via Caddy)

## Repository structure

```
hermes-discord-toolkit/
├── ci/ci.yml                    # GitHub Actions CI (copy to .github/workflows/ to enable)
├── .github/                     # (empty - GitHub OAuth lacks workflow scope)
├── .gitignore                   # Protects .local, secrets, rendered/
├── LICENSE                      # MIT
├── README.md                    # English main README
├── docs/
│   ├── configuration.md         # All variables reference
│   └── deployment.md            # VPS deploy guide
├── examples/
│   ├── basic-bot/               # Minimal slash-commands bot
│   └── voice-tts/               # Voice STT/TTS bot
├── scripts/
│   ├── setup.sh                 # Interactive config
│   ├── render-templates.sh      # Template rendering
│   ├── deploy.sh                # VPS deployment
│   └── validate.sh              # CI/local validation
├── templates/
│   ├── env/.env.example         # All vars with {{PLACEHOLDERS}}
│   ├── systemd/                 # systemd unit templates
│   └── caddy/Caddyfile.template # 9 subdomains + WebSocket
└── skills/                      # 4 Discord skills
    ├── discord-gateway-bot/
    ├── discord-forum-idea-incubator/
    ├── discord-forum-ideation-pipeline/
    └── discord-mastery-pack/
```

## Configuration

All personal configuration lives in `~/.config/hermes-discord-toolkit/.env.local` (created by `setup.sh`). Templates use `{{VARIABLE}}` placeholders rendered by `render-templates.sh`.

See [Configuration Guide](docs/configuration.md) for all variables.

## License

MIT