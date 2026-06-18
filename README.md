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
├── skills/                 # Hermes skills (zero personal config)
├── templates/              # Templates with {{PLACEHOLDERS}}
│   ├── env/               # .env.example
│   ├── systemd/           # systemd unit files
│   ├── caddy/             # Caddyfile.template
│   └── docker/            # docker-compose.yml.template
├── scripts/               # Read ~/.config/hermes-discord-toolkit/.env.local
├── examples/              # Functional examples (no secrets)
├── docs/                  # Documentation
└── .github/workflows/     # CI validation
```

## Configuration

All personal configuration lives in `~/.config/hermes-discord-toolkit/.env.local` (created by `setup.sh`). Templates use `{{VARIABLE}}` placeholders rendered by `render-templates.sh`.

See [Configuration Guide](docs/configuration.md) for all variables.

## License

MIT