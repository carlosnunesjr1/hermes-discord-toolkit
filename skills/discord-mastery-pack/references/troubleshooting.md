# 🐛 TROUBLESHOOTING GUIDE
## Problemas Comuns + Soluções Rápidas

---

## 🤖 Discord Bot

### Bot não responde
| Sintoma | Causa | Solução |
|---------|-------|---------|
| Nenhuma resposta | Message Content Intent OFF | Discord Dev Portal → Bot → **Enable Message Content Intent** |
| Responde só DM | `require_mention: true` + canal não em `free_response_channels` | Adicione canal no `free_response_channels` ou menção |
| Slash commands não aparecem | Cache Discord | **Ctrl+R** no Discord, aguarde 5-10 min |
| "Application did not respond" | Gateway caiu / timeout | `journalctl --user -u hermes-gateway -f` → ver erro |

### Token Inválido
```bash
# 1. Discord Dev Portal → Applications → Bot → Reset Token
# 2. Atualizar
hermes config set DISCORD_BOT_TOKEN "NOVO_TOKEN"
# 3. Restart
systemctl --user restart hermes-gateway
```

### Channel Directory vazio
```bash
# Gateway reinicia e reconstrói
systemctl --user restart hermes-gateway
# Aguarde 30s e verifique
cat ~/.hermes/channel_directory.json
```

---

## 🎤 Voice Channel

### /voice join não entra
```bash
# Verificar deps
dpkg -l | grep -E "ffmpeg|libopus|portaudio"

# Instalar se faltando
sudo apt install -y ffmpeg libopus0 portaudio19-dev espeak-ng

# Reiniciar gateway
systemctl --user restart hermes-gateway
```

### TTS não fala
```bash
# Testar Edge TTS local
python -c "import edge_tts; print('OK')"

# Verificar config
hermes config get tts.provider
hermes config get tts.edge.voice
# Deve ser: edge / pt-BR-AntonioNeural
```

### STT não transcreve
```bash
# Testar faster-whisper
python -c "import faster_whisper; print('OK')"

# Baixar modelo (primeira vez ~150MB)
# Acontece automático no primeiro uso
# Verificar logs: journalctl --user -u hermes-gateway -f | grep -i whisper
```

### Áudio cortado/ruído
```yaml
# Ajustar em config.yaml ou gateway-config.yaml
voice_fx:
  ambient_gain: 0.18      # Reduzir se ambiente alto
  duck_gain: 0.06         # Reduzir se sua voz abafada
  speech_gain: 1.0        # Aumentar se voz baixa
  silence_threshold: 200  # Aumentar se corta fala
  silence_duration: 3     # Aumentar se corta pausas naturais
```

---

## ⏰ Cron Jobs

### Cron não executa
```bash
# 1. Verificar se gateway rodando
systemctl --user status hermes-gateway

# 2. Verificar timezone
hermes cron list  # Mostra next run no timezone correto

# 3. Testar manual
hermes cron run "Nome do Job"

# 4. Ver logs
journalctl --user -u hermes-gateway -f | grep -i cron
```

### Cron executa mas sem output no Discord
```bash
# Verificar deliver target
hermes cron list  # Confira coluna "Deliver"
# Deve ser: discord:CHANNEL_ID (não discord:CHANNEL_ID:THREAD_ID)

# Testar API send direto
curl -X POST -H "Authorization: Bearer $API_KEY" \
  http://localhost:8642/v1/send \
  -d '{"platform":"discord","chat_id":"CHANNEL_ID","text":"teste"}'
```

### Cron roda em loop / duplicado
```bash
# Verificar idempotency keys nos logs
journalctl --user -u hermes-gateway | grep -i "duplicate\|idempotent"

# Limpar estado se necessário
hermes cron remove "Nome"
hermes cron create "..."
```

---

## 🔗 Webhooks

### "Unknown deliver type: discord:12345"
```bash
# PROBLEMA: deliver type deve ser só "discord", chat_id vai em deliver_extra
# ERRADO:
--deliver "discord:1516397585701666962"
# CORRETO:
--deliver "discord" --deliver-chat-id "1516397585701666962"
```

### Webhook retorna "Invalid signature"
```bash
# 1. Pegar secret atual
hermes webhook list  # Copia o Secret

# 2. Gerar signature correta
python -c "
import hmac, hashlib, json
secret='SECRET_AQUI'
payload={'action':'opened','pull_request':{'number':42}}
body=json.dumps(payload, separators=(',',':')).encode()
sig='sha256='+hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
print(sig)
"

# 3. Testar
curl -X POST http://localhost:8644/webhooks/NOME \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: SIGNATURE_AQUI" \
  -d 'PAYLOAD_JSON'
```

### Cloudflare bloqueia / 522 / 524
```bash
# DNS
# Tipo: A, Nome: webhook, IP: SEU_IP_VPS, Proxy: ON (laranja)

# SSL/TLS
# Mode: Full (Strict) - precisa cert válido no VPS
# OU Flexible se não tiver cert no VPS

# Firewall Rules
# Bypass para webhook.menusummo.com.br se tiver WAF
```

---

## 🏗️ Gateway / Systemd

### Gateway reinicia constante (restart loop)
```bash
# 1. Ver logs completos
journalctl --user -u hermes-gateway -n 100 --no-pager

# 2. Causas comuns:
# - API_SERVER_KEY não definido no env
# - Porta 8642 em uso (outro processo)
# - Token Discord inválido
# - Out of memory (OOM kill)

# 3. Ver memória
journalctl --user -u hermes-gateway | grep -i "memory\|oom\|killed"
```

### "Gateway already running (PID XXXX)"
```bash
# Matar processo órfão
kill -9 XXXX
# Ou
pkill -f "hermes gateway"
# Restart
systemctl --user restart hermes-gateway
```

### systemd timeout no stop
```bash
# Aumentar TimeoutStopSec no service
# ~/.config/systemd/user/hermes-gateway.service
TimeoutStopSec=300
# systemctl --user daemon-reload
```

---

## 💾 Memória / Performance

### Memória crescendo indefinidamente
```bash
# 1. Verificar sessões
hermes sessions list

# 2. Comprimir manual
/compress

# 3. Cron automático (já configurado)
# Token Compression a cada 6h

# 4. Limpar antigas
hermes sessions prune
```

### CPU alto constante
```bash
# Verificar processos
htop -u $USER

# Causas comuns:
# - LSP/TypeScript server (Node) consumindo CPU
# - Muitos crons simultâneos (max_parallel_jobs)
# - Loop de agente (max_turns muito alto)

# Ajustar em config.yaml:
agent:
  max_turns: 200  # Reduzir de 500
cron:
  max_parallel_jobs: 2
```

---

## 🔐 Secrets / Permissions

### "Permission denied" em .env / config
```bash
# Hermes protege arquivos sensíveis
# Use hermes config para editar:
hermes config set KEY "VALUE"
# NÃO edite diretamente ~/.hermes/.env
```

### Token rotation
```bash
# Mensal recomendado:
# 1. Discord: Dev Portal → Reset Token
hermes config set DISCORD_BOT_TOKEN "NOVO"
# 2. Webhook: hermes webhook subscribe --secret NOVO_SECRET
# 3. API Server: editar API_SERVER_KEY em .env + systemd env
# 4. Restart all
systemctl --user restart hermes-gateway
```

---

## 📍 Onde Olhar Logs

```bash
# Gateway principal (tudo)
journalctl --user -u hermes-gateway -f

# Só Discord
journalctl --user -u hermes-gateway -f | grep -i discord

# Só Webhooks
journalctl --user -u hermes-gateway -f | grep -i webhook

# Só Crons
journalctl --user -u hermes-gateway -f | grep -i cron

# Só Voice
journalctl --user -u hermes-gateway -f | grep -i voice

# Erros apenas
journalctl --user -u hermes-gateway -f | grep -i "error\|fail\|exception"

# Últimas 100 linhas
journalctl --user -u hermes-gateway -n 100 --no-pager
```

---

## 🆘 Ainda Quebrado?

### Checklist de Diagnóstico Rápido
```bash
# 1. Status geral
systemctl --user status hermes-gateway
curl -H "Authorization: Bearer $KEY" http://localhost:8642/v1/health

# 2. Logs recentes
journalctl --user -u hermes-gateway -n 50 --no-pager | tail -30

# 3. Configuração
hermes config get discord
hermes config get webhook
cat ~/.hermes/channel_directory.json

# 4. Teste isolado
hermes cron run "VPS Health Monitor"
hermes webhook test github-pr-review

# 5. Reset nuclear (último recurso)
systemctl --user stop hermes-gateway
pkill -9 -f "hermes gateway"
rm ~/.hermes/gateway_state.json ~/.hermes/sessions.db*
systemctl --user start hermes-gateway
```

### Contato / Recursos
- **Docs**: https://hermes-agent.nousresearch.com/docs
- **Discord Adapter Source**: `/usr/local/lib/hermes-agent/plugins/platforms/discord/adapter.py`
- **Gateway Config**: `/usr/local/lib/hermes-agent/gateway/config.py`
- **Issues**: GitHub Hermes Agent repo